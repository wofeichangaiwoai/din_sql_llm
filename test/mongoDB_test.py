import uuid

from pymongo import MongoClient


client = MongoClient('mongodb://dataspace:4mJeaeCDufehQUL8@mongodb.databases.svc.cluster.local:27017/dataspace')

db = client['dataspace']
collection = db['conversation']
data = {'_id': uuid.uuid4().hex[:24], 'name': 'John', 'age': 30}
print(data)
res = collection.insert_one(data).inserted_id
id = str(res)
print(id)

result = collection.find_one({'_id': id})
print(result)

update_data = {'$set': {'age': 26, 'gendar':'man'}}
collection.update_one({'_id': id}, update_data)
result = collection.find_one({'_id': id})
print(result)

result = collection.find_one({'_id': uuid.uuid4().hex[:24]})
print(result)
