import datetime
import os
import uuid
from loguru import logger
import redis
from addict import Dict
from kubernetes import client, config
import json
from collections import OrderedDict

from ubix.common.huggingface_text_gen_inference_ex import HuggingFaceTextGenInferenceEx, publish_msg


class APIStatus():
    namespace = "data-tooling"
    deployment_name = "colossal-ai-tgi"
    format_str = '%Y-%m-%d %H:%M:%S'
    request_flag = "llm_request_info_key"
    r = redis.StrictRedis(host=os.environ["REDIS_HOST"],
                          password=os.environ["REDIS_PASSWORD"],
                          decode_responses=True
                          )

    def get_api_ready_time(self, host_list):
        api_ready_list = [self.r.get(host) for host in host_list]
        logger.info(f"api_ready_list:{api_ready_list}")
        return min(api_ready_list)

    def enable_llm_request(self, pod_cnt=0, current_request_time=None):
        current_request_time = current_request_time or datetime.datetime.now()
        request_info = self.r.get(self.request_flag)
        request_info = Dict(json.loads(request_info or "{}"))
        time_gap_seconds = 999999
        if request_info.request_time:
            logger.info(f"request_info from Redis with key:{self.request_flag}, : {type(request_info)}, request_info:{request_info}")
            previous_time = datetime.datetime.strptime(request_info.request_time, self.format_str)
            time_gap_seconds = (current_request_time - previous_time).total_seconds()

        # Remove the flag, if the request is a few mins ago, and Pod cnt is 0
        if pod_cnt == 0 and time_gap_seconds > 2 * 60 and request_info:
            logger.info(
                f"Will try to remove the inactive request_info:{request_info}, "
                f"time_gap_seconds:{time_gap_seconds},current_time:{current_request_time}, pod_cnt:{pod_cnt}")
            self.r.delete(self.request_flag)
            request_info = None

        if request_info or (pod_cnt == 0 and time_gap_seconds <= 2 * 60):
            logger.info(f"already have the active request_info:{request_info}, pod_cnt={pod_cnt}")
            return request_info
        elif pod_cnt > 0 and request_info is None:
            # Request info have already dropped from redis
            logger.info("The LLM already start with other way")
            return Dict({"request_time": None, "request_id": None, "pods_cnt": pod_cnt})
        else:
            # If can not find the flag, submit the hello request, and save the flag
            logger.info(f"pod_cnt:{pod_cnt}, time_gap_seconds:{time_gap_seconds}, request_info:{request_info}")
            request_id = uuid.uuid4().hex
            request_dict = {"request_id": request_id, "prompt": "hello", "invocation_params": {}}
            publish_msg(request_dict)
            request_info = {"request_time": current_request_time.strftime(self.format_str),
                            "request_id": request_id,
                            "pods_cnt": pod_cnt}
            logger.info(f"Submit a new request, {request_info}, pod_cnt:{pod_cnt}")
            self.r.set(self.request_flag, json.dumps(request_info, indent=4), ex=3600*48)
            return Dict(request_info)

    def get_api_status(self, enable_llm=False):
        current_request_time = datetime.datetime.now()
        config.load_incluster_config()
        api = client.AppsV1Api()
        deployment = api.read_namespaced_deployment(self.deployment_name, self.namespace)

        deployment_labels = deployment.spec.selector.match_labels

        label_selector = ",".join([f"{key}={value}" for key, value in deployment_labels.items()])

        core_api = client.CoreV1Api()
        pods = core_api.list_namespaced_pod(self.namespace, label_selector=label_selector)
        pods_cnt = len(pods.items)
        request_info = self.enable_llm_request(pods_cnt, current_request_time=current_request_time)
        request_time = request_info.request_time
        if pods_cnt == 0 and not enable_llm:
            return {'pod_cnt': 0}
        elif pods_cnt == 0 and enable_llm:
            return {'pod_cnt': 0,
                    'status_dict': {
                        "request_status": {"index": 0,
                                           "name": "request_status",
                                           "eta": None,
                                           "cost": None,
                                           "status": "ready",
                                           "ready_time": request_time,
                                           "comments": "The time submit the request",
                                           }}}
        else:
            pod = sorted(pods.items, key=lambda pod: pod.metadata.creation_timestamp)[0]
            pod_name_list = [pod.metadata.name for pod in pods.items]
            cur_pod_name = pod.metadata.name
            pod_name = pod.metadata.name

            if request_info.get("pod_name", None) is None and enable_llm:
                request_info["pod_name"] = cur_pod_name
                # self.r.set(self.request_flag, json.dumps(request_info, indent=4), ex=3600*48)

            first_pod_exist = True
            if request_info.get("pod_name") not in pod_name_list:
                first_pod_exist = False
                pod_name = request_info.get("pod_name")

            res = Dict({
                'first_pod': pod_name,
                'first_pod_exist': first_pod_exist,
                'cur_pod_list': pod_name_list,
                'pod_cnt': len(pods.items),
                'status_dict': None

            })

            status_dict = OrderedDict()
            if first_pod_exist:
                status_dict.update({
                    "request_status": {"index": 0,
                                       "name": "request_status",
                                       "eta": None,
                                       "cost": None,
                                       "status": "ready",
                                       "ready_time": request_time,
                                       "comments": "The time submit the request",
                                       }})
            status_dict.update({
                "pod_create_status": {"index": 1,
                                      "name": "pod_create",
                                      "eta": 10,
                                      "cost": None,
                                      "status": None,
                                      "ready_time": None,
                                      "comments": "The pod metadata was created in k8s",
                                      },
                "resource_allocated_status": {"index": 2,
                                              "name": "resource_allocated_status",
                                              "eta": 75,
                                              "cost": None,
                                              "status": None,
                                              "ready_time": None,
                                              "comments": "Allocate the resource, find the node for the pod"
                                              },
                "image_status": {"index": 3,
                                 "name": "image_status",
                                 "eta": 200,
                                 "cost": None,
                                 "status": None,
                                 "ready_time": None,
                                 "comments": "Pull the docker image from remote to the node"
                                 },
                "api_ready_status": {"index": 4,
                                     "name": "api_ready",
                                     "eta": 250,
                                     "cost": None,
                                     "status": None,
                                     "ready_time": None,
                                     "comments": "API is already online"
                                     }
            })

            try:
                status_dict.get("pod_create_status").update({
                    "status": "ready",
                    "ready_time": pod.metadata.creation_timestamp.strftime(self.format_str)
                })

                status_dict.get("resource_allocated_status").update({
                    "status": 'ready',
                    "ready_time": pod.status.start_time.strftime(self.format_str)
                }
                )
                status_dict.get("image_status").update({
                    "status": 'ready',
                    "ready_time": pod.status.container_statuses[0].state.running.started_at.strftime(
                        self.format_str)
                }
                )

                status_dict.get("api_ready_status").update({
                    "status": 'ready',
                    "ready_time": self.get_api_ready_time([cur_pod_name])
                })
            except Exception as e:
                logger.info(e)

            total_cost = 0
            for cur_item, previous_item in zip(list(status_dict.items())[1:], list(status_dict.items())):
                logger.info(f"cur_item.keys:{cur_item}")
                cur_key, cur_dict = cur_item
                _, previous_dict = previous_item
                if cur_dict.get("ready_time", None) and previous_dict.get("ready_time", None):
                    cur_time = datetime.datetime.strptime(cur_dict.get("ready_time", None), self.format_str)
                    previous_time = datetime.datetime.strptime(previous_dict.get("ready_time", None), self.format_str)
                    seconds_interval = (cur_time - previous_time).total_seconds()
                    status_dict[cur_key]["cost"] = int(seconds_interval)
                    total_cost = total_cost + seconds_interval
                    logger.info(f"{cur_key}, cost:{seconds_interval}, total_sec:{total_cost}")
            res["status_dict"] = status_dict
            res["total_cost"] = int(total_cost)
            return res
