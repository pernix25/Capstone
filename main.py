import pymongo
import cv2
from picture import draw
import random as r

# row 13-18, radius = 100
# row 7-12, radius = 75
# row 1-6, radius = 50

# Database stuff

# keys: row, col, hold_type, img_coords
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Capstone"]
collection = db["moonBoard"]

# functions

def query():
    print('starting query')
    data = collection.find()
    for item in data:
        print(item)

def create_route(hold_type, num_routes=1):
    def get_radius(row_num):
        if row_num >= 13:
            return 100
        elif row_num >= 7:
            return 75
        else:
            return 50

    def pick_next_hold(hold_type, curr_row_num, col_num=None, col_tolerance=3):
        next_row = curr_row_num + 2
        possible_holds = []
        while (next_row <= 17):
            possible_holds = list(collection.find({'$and': [{'row': {'$eq': next_row}}, {'hold_type': f'{hold_type}'}]}))
            if (possible_holds):
                break
            next_row += 1

        if (possible_holds):
            curr_row = next_row
            return (r.choice(possible_holds), curr_row)
        else:
            return (False, False)

    start_holds = []
    finish_holds = []
    middle_holds = []
    
    possible_starting_holds = list(collection.find({'$and': [{'row': {'$gte': 5}}, {'row': {'$lte': 7}}, {'hold_type': f'{hold_type}'}]}))
    possible_finish_holds = list(collection.find({'$and': [{'row': {'$eq': 18}}, {'hold_type': f'{hold_type}'}]}))
    random_start = r.choice(possible_starting_holds)

    random_finsih = r.choice(possible_finish_holds)
    start_holds.append(random_start)
    finish_holds.append(random_finsih)

    image_with_circle = cv2.imread("moonBoard.jpg")

    start_row = random_start['row']
    start_radius = get_radius(start_row)
    finish_radius = get_radius(18)

    start_coords = list(random_start['img_coords'])
    finish_coords = list(random_finsih['img_coords'])

    image_with_circle = draw(image_with_circle, start_coords, start_radius)
    image_with_circle = draw(image_with_circle, finish_coords, finish_radius)

    curr_row = start_row

    while (curr_row <= 17):
        next_hold, curr_row = pick_next_hold(hold_type, curr_row)
        
        if (next_hold):
            hold_coords = list(next_hold['img_coords'])
            image_with_circle = draw(image_with_circle, hold_coords, get_radius(next_hold['row']))
        else:
            break


    # Display the image
    cv2.imshow("Image with Circle", image_with_circle)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    create_route('crimp')

if __name__ == '__main__':
    main()
