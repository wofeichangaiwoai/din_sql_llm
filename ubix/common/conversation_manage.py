from datetime import datetime

from easydict import EasyDict as edict

import uuid

from pymongo import MongoClient
from ubix.common.log_basic import *

client = MongoClient('mongodb://dataspace:4mJeaeCDufehQUL8@mongodb.databases.svc.cluster.local:27017/dataspace')

db = client['dataspace']
collection = db['conversation']


def save_conversation(conversation):
    if "start_time" not in conversation:
        conversation["start_time"] = conversation["conversation_list"][0]["start_time"]

    if "_id" not in conversation:
        conversation["_id"] = conversation["conversation_id"]
    if "_id" not in conversation:
        logging.error(f"Can not find _id:{conversation}")
        return None
    id = conversation["_id"]
    update_data = {'$set': conversation}
    collection.update_one({"_id": id}, update_data, upsert=True)
    return collection.find_one({'_id': id})


def update_conversation(args):
    id = args.get("_id")
    conversation = collection.find_one({'_id': id, 'user_id': args.get("user_id")})
    logging.info(f"update conversation with {args}")
    logging.info(f"conversation old: {conversation}")
    conversation = {**conversation, **args,}
    logging.info(f"conversation new: {conversation}")
    update_data = {'$set': conversation}
    collection.update_one({"_id": id}, update_data, upsert=True)

    conversation = get_conversation_by_id(args.get("_id"))
    conversation.pop("conversation_list")
    return conversation


def get_or_create_conversion(request_data, header):
    id = request_data.get("_id", None) or request_data.get("conversation_id")
    conversion = collection.find_one({'_id': id})
    start = datetime.now()
    if conversion is None:
        logging.info(f"Create a new conversation:{id}")
        conversion = edict({
            "_id": request_data.conversation_id,
            "start_time": start.strftime('%Y-%m-%d %H:%M:%S'),
            "account_id": header.get("Account-ID", "UNKNOWN"),
            "user_id":  header.get("User-ID", "UNKNOWN"),
            "query_type": request_data.query_type,
            "conversation_id": request_data.conversation_id,
            "conversation_list": []
        })
    return edict(conversion)


def get_conversation_list(user_id):
    query = {"user_id": user_id}

    result = collection.find(query)

    result_mini = []

    for item in result:
        item: dict = item
        item['qa_count'] = len(item['conversation_list'])
        item['qa_first'] = item['conversation_list'][0]
        item.pop('conversation_list')
        result_mini.append(item)

    return result_mini


def get_conversation_by_id(id):
    conversation = collection.find_one({"_id": id})
    return conversation
