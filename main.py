import pymongo
import cv2
from picture import draw

# row 13-18, radius = 100
# row 7-12, radius = 75
# row 1-6, radius = 50

# Database stuff

# keys: row, col, hold_type, img_coords
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Capstone"]
collection = db["moonBoard"]
