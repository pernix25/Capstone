import pymongo

# keys: row, col, hold_type, img_coords

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["Capstone"]

collection = db["moonBoard"]

#collection.insert_one({'filePath': '12345', 'holdType': 'crimp', 'photoNumber': 1})

#query = collection.find_one({"filePath": "12345"})

query = collection.find()

print(query[0]['img_coords'])