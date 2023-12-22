import os
import pika


mq_server = os.environ.get('MQ_SERVER')
mq_user = os.environ.get('MQ_USER')
mq_password = os.environ.get('MQ_PASSWORD')

print(f"mq_server:{mq_server},mq_user:{mq_user}, mq_password:{mq_password}")

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host=mq_server,
    credentials=pika.PlainCredentials(mq_user, mq_password))
)
channel = connection.channel()


channel.queue_declare(queue='hello')


channel.basic_publish(exchange='', routing_key='hello', body='Hello, RabbitMQ!')

print(" [x] Sent 'Hello, RabbitMQ!'")

"""
python test/mq_test.py

"""
