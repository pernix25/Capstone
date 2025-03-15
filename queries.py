import pymongo

# keys: row, col, hold_type, img_coords

client = pymongo.MongoClient("mongodb://localhost:27017/")

db = client["Capstone"]

moon_collection = db["moonBoard"]
route_collection = db['routes']

#moon_collection.insert_one({'filePath': '12345', 'holdType': 'crimp', 'photoNumber': 1})

#query = moon_collection.find_one({"filePath": "12345"})
"""
query_all = moon_collection.find()
for item in query_all:
    print(item)
"""
#start_holds = moon_collection.find({'$and': [{'row': {'$gte': 5}}, {'row': {'$lte': 7}}, {'hold_type': 'crimp'}]})

all_routes = route_collection.find()
for row in all_routes:
    print(row)