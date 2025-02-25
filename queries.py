import pymongo

# keys: row, col, hold_type, img_coords

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["Capstone"]

collection = db["moonBoard"]

#collection.insert_one({'filePath': '12345', 'holdType': 'crimp', 'photoNumber': 1})

#query = collection.find_one({"filePath": "12345"})
"""
query_all = collection.find()
"""

start_holds = collection.find({'$and': [{'row': {'$gte': 5}}, {'row': {'$lte': 7}}, {'hold_type': 'crimp'}]})

for row in start_holds:
    print(row)