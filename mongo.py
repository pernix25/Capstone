import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["Capstone"]

collection = db["singleHolds"]

#collection.insert_one({'filePath': '12345', 'holdType': 'crimp', 'photoNumber': 1})

result = collection.find_one({"filePath": "12345"})
print(result)