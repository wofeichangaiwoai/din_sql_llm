from __future__ import annotations
import os
import logging
from typing import (
    Any,
    List,
    Optional,
)

import text_generation
from langchain.llms import HuggingFaceTextGenInference
from langchain.callbacks.manager import (
    CallbackManagerForLLMRun,
)

import os
import pika
import uuid
import json

logger = logging.getLogger(__name__)
import redis

host = os.environ["REDIS_HOST"]
r = redis.Redis(host=host, password=os.environ["REDIS_PASSWORD"], port=6379, db=0)
MQ_TOPIC = "chat_ubix_request"

class HuggingFaceTextGenInferenceEx(HuggingFaceTextGenInference):
    @staticmethod
    def submit_request(prompt, **kwargs) -> str:
        request_id = uuid.uuid4().hex
        # self.client.generate(prompt, **kwargs)
        return request_id

    @staticmethod
    def get_response(request_id) -> str:
        _, value = r.brpop(request_id, 120)
        response_dict = json.loads(value.decode('utf-8'))
        print(f"response_dict:{json.dumps(response_dict, indent=4)})")
        return response_dict

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        if self.streaming:
            completion = ""
            for chunk in self._stream(prompt, stop, run_manager, **kwargs):
                completion += chunk.text
            return completion

        invocation_params = self._invocation_params(stop, **kwargs)
        request_id = uuid.uuid4().hex
        print(f"request_id:{request_id}")
        request_dict = {"request_id": request_id, "prompt": prompt, "invocation_params": invocation_params}
        publish_msg(request_dict)
        response_dict: dict = self.get_response(request_id)
        generated_text = response_dict.get("llm_answer")
        # remove stop sequences from the end of the generated text
        for stop_seq in invocation_params["stop_sequences"]:
            if stop_seq in generated_text:
                generated_text = generated_text[
                                     : generated_text.index(stop_seq)
                                     ]
        return generated_text


def publish_msg(request_dict: dict):
    request_json = json.dumps(request_dict, indent=4)
    print(f"input json request:\n{request_json}")
    request_id = request_dict.get("request_id")

    mq_server = os.environ.get('MQ_SERVER')
    mq_user = os.environ.get('MQ_USER')
    mq_password = os.environ.get('MQ_PASSWORD')
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=mq_server,
        credentials=pika.PlainCredentials(mq_user, mq_password))
    )
    channel = connection.channel()

    channel.queue_declare(queue=MQ_TOPIC)

    channel.basic_publish(exchange='', routing_key=MQ_TOPIC, body=json.dumps(request_dict))

    print(f" [x] Sent 'Hello, RabbitMQ!' {request_json}")
    return request_id



 
