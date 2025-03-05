import pymongo
import cv2
from picture import draw
import random as r

# row 13-18, radius = 100
# row 7-12, radius = 75
# row 1-6, radius = 50

# holds are 8 in apart - horizontal
# holds are about 7 in apart - vertical
HORIZONTAL = 8
VERTICAL = 7
APE = 72

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
    def within_reach(curr_row_col, potential_row_col, ape_index):
        curr_row = curr_row_col[0]
        curr_col = curr_row_col[1]
        potential_row = potential_row_col[0]
        potential_col = potential_row_col[1]
        
        row_diff = round(potential_row - curr_row)
        col_diff = round(potential_col - curr_col)

        if (abs(col_diff * 8) > (ape_index * 0.5)):
            return False
        else:
            return True

    def pick_next_hold(hold_type, row_num, col_num, ape_index):

        next_row = row_num + 2
        while (next_row < 18):
            possible_holds = list(collection.find({'$and': [{'row': {'$eq': next_row}}, {'hold_type': f'{hold_type}'}]}))
            if (possible_holds):
                r.shuffle(possible_holds)
                for chosen_hold in possible_holds:
                    if (within_reach((row_num, col_num), (chosen_hold['row'], chosen_hold['col']), ape_index)):
                        return (chosen_hold, next_row)
            next_row += 1

        return (False, False)
    
    route = []

    possible_starting_holds = list(collection.find({'$and': [{'row': {'$gte': 5}}, {'row': {'$lte': 7}}, {'hold_type': f'{hold_type}'}]})) 
    random_start = r.choice(possible_starting_holds)
    start_row = random_start['row']
    route.append(random_start)

    curr_row = start_row
    curr_col = random_start['col']

    top_most_hold = random_start

    while (curr_row <= 17):
        next_hold, curr_row = pick_next_hold(hold_type, curr_row, curr_col, APE)
        
        if (next_hold):            
            route.append(next_hold)
            
            curr_row = next_hold['row']
            curr_col = next_hold['col']
            top_most_hold = next_hold
        else:
            break

    curr_row_col = (top_most_hold['row'], top_most_hold['col'])
    
    possible_finish_holds = list(collection.find({'$and': [{'row': {'$eq': 18}}, {'hold_type': f'{hold_type}'}]}))
    r.shuffle(possible_finish_holds)
    for hold in possible_finish_holds:
        if (within_reach(curr_row_col, (hold['row'], hold['col']), APE)):
            random_finish = hold
            break
        else:
            print('chossing finish at random')
            random_finish = r.choice(possible_finish_holds)

    route.append(random_finish)
    return route

def print_route(holds):
    def get_radius(row_num):
        if row_num >= 13:
            return 100
        elif row_num >= 7:
            return 75
        else:
            return 50
        
    route_length = len(holds) - 1
    img = cv2.imread("moonBoard.jpg")

    for index, hold in enumerate(holds):
        hold_coords = hold['img_coords']
        if index == 0:
            img = draw(img, hold_coords, get_radius(hold['row']), (0,255,0))
        elif index == route_length:
            img = draw(img, hold_coords, get_radius(hold['row']), (0,0,255))
        else:
            img = draw(img, hold_coords, get_radius(hold['row']))
    
    # Display the image
    cv2.imshow("Image with Circle", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def alter_route(route, hold_num):
    hold_index = hold_num - 1
    
    if (hold_index == 0):
        # changes the start hold
        next_hold = route[hold_index + 1]
    elif (hold_index == len(route)):
        # changes the finish hold
        previous_hold = route[hold_index - 1]
    else:
        # changes an intermidiate hold
        previous_hold = route[hold_index - 1]
        next_hold = route[hold_index + 1]

def main():
    route = create_route('crimp')
    print_route(route)

if __name__ == '__main__':
    main()
