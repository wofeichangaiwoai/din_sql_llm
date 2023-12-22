import json
import os
import traceback

import pika
import text_generation
import redis

mq_server = os.environ.get('MQ_SERVER')
mq_user = os.environ.get('MQ_USER')
mq_password = os.environ.get('MQ_PASSWORD')

host = os.environ["REDIS_HOST"]
r = redis.Redis(host=host, password=os.environ["REDIS_PASSWORD"], port=6379, db=0)

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=mq_server,
    credentials=pika.PlainCredentials(mq_user, mq_password))
)

def callback(ch, method, properties, body):

    print(f" [x] Received {body}, {type(body)}")
    try:
        request_json = body.decode("utf-8")
        print(f"input json request:\n{request_json}")
        request_dict = json.loads(request_json)
        request_id = request_dict.get("request_id")
        client = text_generation.Client(
            base_url="http://colossal-llm-api.home-dev.ubix.io",
            timeout=120
        )
        prompt = request_dict.get("prompt")
        invocation_params = request_dict.get("invocation_params")
        print(f"invocation_params:{invocation_params}")
        res = client.generate(prompt, **invocation_params)
        response = {
            "request_id": request_id,
            "llm_cost": "xxxx",
            "llm_host": "abc.com",
            "llm_answer": res.generated_text,
            "params": invocation_params
        }
        print(f'Try to save data to redis')
        data_str: str = json.dumps(response, indent=4)
        r.rpush(request_id, data_str)
        r.expire(request_id, 3600)
        print(f"request:{request_id} already save to redis")
        return response
    except Exception as e:
        print(traceback.format_exc())
        print(e)


channel = connection.channel()


channel.basic_consume(queue='chat_ubix_request', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit, press Ctrl+C')
channel.start_consuming()

"""
MQ_PASSWORD=iaD9VVSE_H1y7CZuRd2DE7f8IRU-BXqb \
MQ_SERVER=rabbitmq-backoffice.databases.svc.cluster.local \
MQ_USER=default_user_I4azCn5HqKRKPfrQdF- \

python ubix/common/consumer_test.py

"""
