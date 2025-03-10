import pymongo
import cv2
from picture import draw
import random as r

# holds are 8 in apart - horizontal
# holds are about 7 in apart - vertical
# Marks ape index
HORIZONTAL = 8
VERTICAL = 7
APE = 72

# Database stuff

# keys: row, col, hold_type, img_coords
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Capstone"]
collection = db["moonBoard"]

# functions

def query() -> None:
    # returns all enteries in moonBoard database
    print('starting query')
    data = collection.find()
    for item in data:
        print(item)

def within_reach(curr_row_col, potential_row_col, ape_index) -> bool:
    # determines weather a hold is within reach based on 50% of ape index
    """ needs to include row difference in determining if a hold is within reach """
    curr_row = curr_row_col[0]
    curr_col = curr_row_col[1]
    potential_row = potential_row_col[0]
    potential_col = potential_row_col[1]
    
    row_diff = round(potential_row - curr_row)
    col_diff = round(potential_col - curr_col)

    # calculate differnece between holds and if its grater than 50% ape index return false
    if (abs(col_diff * HORIZONTAL) > (ape_index * 0.5)):
        return False
    else:
        return True

def create_route(hold_type, num_routes=1) -> list:
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

    return img

def alter_route(route, hold_num, difficulty, ape_index) -> list:
    def pick_hold(curr_hold, difficulty, ape_index, next_hold=None, previous_hold=None) -> dict:
        """ potential problem with function: may error if now hold type does not exist in row query """
        """ figure out a way to find new hold when you're at the most difficult or easiest hold already """
        """ find solution to picking a hold when the elected type doesn't exist in the row """
        # picks new hold based on type
        categories_by_name = {'jug': 0, 'edge': 1, 'pinch': 2, 'crimp': 3, 'small pinch': 4, 'small crimp': 5}
        categories_by_number = {0: 'jug', 1: 'edge', 2: 'pinch', 3: 'crimp', 4: 'small pinch', 5: 'small crimp'}
        
        curr_hold_type = curr_hold['hold_type']
        curr_row = curr_hold['row']
        curr_col = curr_hold['col']

        if (next_hold and previous_hold):
            # pick a new intermidiate hold, still within reach of other holds
            if (difficulty):
                # make hold more difficult
                new_hold_type = curr_hold_type
                while (True):
                    temp_curr_row = curr_row
                    try:
                        new_hold_type = categories_by_number[categories_by_name[new_hold_type] + 1]
                    except KeyError:
                        return route
                    
                    row_stack = [curr_row - 1, curr_row + 1]
                    for _ in range(len(row_stack) + 1):
                        row = list(collection.find({'$and': [{'row': {'$eq': temp_curr_row}}, {'hold_type': f'{new_hold_type}'}]}))
                        r.shuffle(row)
                        for hold in row:
                            previous_hold_row_col = (previous_hold['row'], previous_hold['col'])
                            next_hold_row_col = (next_hold['row'], next_hold['col'])
                            if (within_reach((hold['row'], hold['col']), next_hold_row_col, ape_index) and within_reach(previous_hold_row_col, (hold['row'], hold['col']), ape_index)):
                                return hold
                        if (len(row_stack) > 0):
                            temp_curr_row = row_stack.pop()
                    # didn't find a new hold, repeat proccess
            else:
                # make hold easier
                new_hold_type = curr_hold_type
                while (True):
                    temp_curr_row = curr_row
                    try:
                        new_hold_type = categories_by_number[categories_by_name[new_hold_type] - 1]
                    except KeyError:
                        return route
                    
                    row_stack = [curr_row + 1, curr_row - 1]
                    for _ in range(len(row_stack) + 1):
                        row = list(collection.find({'$and': [{'row': {'$eq': temp_curr_row}}, {'hold_type': f'{new_hold_type}'}]}))
                        r.shuffle(row)
                        for hold in row:
                            previous_hold_row_col = (previous_hold['row'], previous_hold['col'])
                            next_hold_row_col = (next_hold['row'], next_hold['col'])
                            if (within_reach((hold['row'], hold['col']), next_hold_row_col, ape_index) and within_reach(previous_hold_row_col, (hold['row'], hold['col']), ape_index)):
                                return hold
                        if (len(row_stack) > 0):
                            temp_curr_row = row_stack.pop()
                    # didn't find a new hold, repeat proccess

        elif (next_hold):
            # picks a new start hold still within reach of next hold
            if (difficulty):
                # get harder hold type
                new_hold_type = curr_hold_type
                while (True):
                    # loop should either find hold or get key error
                    temp_curr_row = curr_row
                    try:
                        new_hold_type = categories_by_number[categories_by_name[new_hold_type] + 1]
                    except KeyError:
                        return route

                    # this method only works if the row has elected hold_type in it
                    row_stack = [curr_row - 1, curr_row + 1]
                    for _ in range(len(row_stack) + 1):
                        row = list(collection.find({'$and': [{'row': {'$eq': temp_curr_row}}, {'hold_type': f'{new_hold_type}'}]}))
                        r.shuffle(row)
                        for hold in row:
                            next_hold_row_col = (curr_row, curr_col)
                            if (within_reach((hold['row'], hold['col']), next_hold_row_col, ape_index)):
                                return hold
                        if (len(row_stack) > 0):
                            temp_curr_row = row_stack.pop()
                    # didn't find a new hold, repeat proccess
            else:
                # get easier hold type
                new_hold_type = curr_hold_type
                while (True):
                    # loop should either find hold or get key error
                    temp_curr_row = curr_row
                    try:
                        new_hold_type = categories_by_number[categories_by_name[new_hold_type] - 1]
                    except KeyError:
                        return route

                    # this method only works if the row has elected hold_type in it
                    row_stack = [curr_row + 1, curr_row - 1]
                    for _ in range(len(row_stack) + 1):
                        row = list(collection.find({'$and': [{'row': {'$eq': temp_curr_row}}, {'hold_type': f'{new_hold_type}'}]}))
                        r.shuffle(row)
                        for hold in row:
                            next_hold_row_col = (curr_row, curr_col)
                            if (within_reach((hold['row'], hold['col']), next_hold_row_col, ape_index)):
                                return hold
                        if (len(row_stack) > 0):
                            temp_curr_row = row_stack.pop()
                    # didn't find a new hold, repeat proccess                
        
        elif (previous_hold):
            # picks a new finish hold still within reach of the previous hold
            if (difficulty):
                # pick a harder finish hold
                new_hold_type = curr_hold_type
                while (True):
                    try:
                        new_hold_type = categories_by_number[categories_by_name[new_hold_type] + 1]
                    except KeyError:
                        return route

                    row = list(collection.find({'$and': [{'row': {'$eq': 18}}, {'hold_type': f'{new_hold_type}'}]}))
                    r.shuffle(row)
                    for hold in row:
                        previous_hold_row_col = (previous_hold['row'], previous_hold['col'])
                        if (within_reach((hold['row'], hold['col']), previous_hold_row_col, ape_index)):
                            return hold
            else:
                # pick an easier finish hold
                new_hold_type = curr_hold_type
                while (True):
                    try:
                        new_hold_type = categories_by_number[categories_by_name[new_hold_type] - 1]
                    except KeyError:
                        return route

                    row = list(collection.find({'$and': [{'row': {'$eq': 18}}, {'hold_type': f'{new_hold_type}'}]}))
                    r.shuffle(row)
                    for hold in row:
                        previous_hold_row_col = (previous_hold['row'], previous_hold['col'])
                        if (within_reach((hold['row'], hold['col']), previous_hold_row_col, ape_index)):
                            return hold

        else:
            raise ValueError

    hold_index = hold_num - 1
    curr_hold = route[hold_index]
    
    if (hold_index == 0):
        # changes the start hold
        next_hold = route[hold_index + 1]
        new_hold = pick_hold(curr_hold, difficulty, ape_index, next_hold=next_hold)
        route.pop(0)
        route.insert(0, new_hold)
    elif (hold_num == len(route)):
        # changes the finish hold
        previous_hold = route[hold_index - 1]
        new_hold = pick_hold(curr_hold, difficulty, ape_index, previous_hold=previous_hold)
        route.pop()
        route.append(new_hold)
    else:
        # changes an intermidiate hold
        previous_hold = route[hold_index - 1]
        next_hold = route[hold_index + 1]
        new_hold = pick_hold(curr_hold, difficulty, ape_index, next_hold, previous_hold)
        route.pop(hold_index)
        route.insert(hold_index, new_hold)

    return route

def main():
    routes = [create_route('crimp')]
    img = print_route(routes[-1])

    usr_input = 'y'
    while (usr_input != 'n'):
        usr_input = input('Would you like to alter the route? (y/n) ').lower()
        if (usr_input == 'y'):
            usr_input = input(f'Starting from the bottom (with 1 as the first hold and {len(routes[-1])} as the last hold), which one would you like to modify? ')
            try:
                hold_number = int(usr_input)
            except ValueError:
                print('Please enter a number')
                continue
            
            difficulty = int(input('Enter 0 to make hold easier, 1 for harder: '))
            new_route = alter_route(routes[-1], hold_number, difficulty, APE)

            routes.append(new_route)
            print('showing new image')
            img = print_route(new_route)
    
    usr_input = input('Would you like to save the route? (y/n) ').lower()
    if (usr_input == 'y'):
        name = input('What would you like to name the route: ')
        cv2.imwrite(f"{name}.jpg", img)

if __name__ == '__main__':
    main()
