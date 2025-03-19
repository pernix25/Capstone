import pymongo
import cv2
from picture import draw

def print_route(holds):
    # creates an image of the route created
    def get_radius(row_num):
        # get the radius of circle for drrawing on image based on row number
        if row_num >= 13:
            return 100
        elif row_num >= 7:
            return 75
        else:
            return 50

    img = cv2.imread("moonBoard.jpg")

    # iterate over input list and draw circles around the holds
    for hold in holds:
        hold_coords = hold['img_coords']

        # draw green circle for start hold
        img = draw(img, hold_coords, get_radius(hold['row']), (0,255,0))

    # Display the image
    cv2.imshow("Press Zero to proceed", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Capstone"]
collection = db["moonBoard"]

hold = 'pocket'

holds_query = list(collection.find({'hold_type': hold}))

print_route(holds_query)
