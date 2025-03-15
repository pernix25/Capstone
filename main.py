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
HEIGHT = 70

# moonboard database stuff
# keys: row, col, hold_type, img_coords

# routes database stuff
# keys: name, start, intermidiates, finish

# functions

def query() -> None:
    # returns all enteries in moonBoard database

    # connect to database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["Capstone"]
    collection = db["moonBoard"]

    print('starting query')
    data = collection.find()
    for item in data:
        print(item)

def within_reach(curr_row_col, potential_row_col, ape_index, height) -> bool:
    # determines weather a hold is within reach based on 50% of ape index and 115% of height
    curr_row = curr_row_col[0]
    curr_col = curr_row_col[1]
    potential_row = potential_row_col[0]
    potential_col = potential_row_col[1]
    
    row_diff = round(potential_row - curr_row)
    col_diff = round(potential_col - curr_col)

    # calculate differnece between holds and if its grater than 50% ape index, 115% height return false
    if ((abs(col_diff * HORIZONTAL) > (ape_index * 0.5)) and (abs(row_diff * VERTICAL) > height * 1.15)):
        return False
    else:
        return True

def create_route(hold_type, num_routes=1) -> list:
    def pick_next_hold(hold_type, row_num, col_num, ape_index, height):
        # pick next hold based on current row and column

        # currently the algorithim starts with choosing a hold 2 rows above previous row
        next_row = row_num + 2
        
        # loop until a next hold has been picked or you've reached the finsih row (18)
        while (next_row < 18):
            # query holds based on current row and holdtype
            possible_holds = list(collection.find({'$and': [{'row': {'$eq': next_row}}, {'hold_type': f'{hold_type}'}]}))
            
            # if query returns a list of hodls -> shuffle list -> loop list and find hold within reach of previous hold
            if (possible_holds):
                r.shuffle(possible_holds)
                for chosen_hold in possible_holds:
                    if (within_reach((row_num, col_num), (chosen_hold['row'], chosen_hold['col']), ape_index, height)):
                        return chosen_hold
            next_row += 1

        # did not find hold -> return False
        return False
    
    # connect to database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["Capstone"]
    collection = db["moonBoard"]

    route = []

    # query all possible start holds based on holds type -> pick one and then append to routes list
    possible_starting_holds = list(collection.find({'$and': [{'row': {'$gte': 5}}, {'row': {'$lte': 7}}, {'hold_type': f'{hold_type}'}]})) 
    random_start = r.choice(possible_starting_holds)
    start_row = random_start['row']
    route.append(random_start)

    # set current and topmost hold info
    curr_row = start_row
    curr_col = random_start['col']
    top_most_hold = random_start

    # loop through rows picking holds unitl you reach row 17
    while (curr_row <= 17):
        # get next hold
        next_hold = pick_next_hold(hold_type, curr_row, curr_col, APE, HEIGHT)
        
        if (next_hold):            
            route.append(next_hold)
            
            # set new current and topmost hold info
            curr_row = next_hold['row']
            curr_col = next_hold['col']
            top_most_hold = next_hold
        else:
            # the algorithim has reached finsih holds row -> break loop
            break

    # set current hold row and column in a tuple
    curr_row_col = (top_most_hold['row'], top_most_hold['col'])
    
    # query all possible finish holds based on hold type and shuffle list
    possible_finish_holds = list(collection.find({'$and': [{'row': {'$eq': 18}}, {'hold_type': f'{hold_type}'}]}))
    r.shuffle(possible_finish_holds)

    random_finish = None

    # loop over finish holds and find one that is within reach of previous hold
    for hold in possible_finish_holds:
        if (within_reach(curr_row_col, (hold['row'], hold['col']), APE, HEIGHT)):
            random_finish = hold
            break
    
    # didn't find hold within reach -> pick finish hold at random (within reach)
    if not random_finish:
        all_finish_holds = list(collection.find({'row': {'$eq': 18}}))
        r.shuffle(all_finish_holds)

        for hold in all_finish_holds:
            if (within_reach(curr_row_col, (hold['row'], hold['col']), APE, HEIGHT)):
                random_finish = hold
                break
        

    route.append(random_finish)

    # disconnect from database
    client.close()

    return route

def print_route(holds):
    # cerates an image of the route created
    def get_radius(row_num):
        # get the radius of circle for drrawing on image based on row number
        if row_num >= 13:
            return 100
        elif row_num >= 7:
            return 75
        else:
            return 50
    
    route_length = len(holds) - 1
    img = cv2.imread("moonBoard.jpg")

    # iterate over input list and draw circles around the holds
    for index, hold in enumerate(holds):
        hold_coords = hold['img_coords']

        # draw green circle for start hold
        if index == 0:
            img = draw(img, hold_coords, get_radius(hold['row']), (0,255,0))
        # draw blue circles for intermidiates
        elif index == route_length:
            img = draw(img, hold_coords, get_radius(hold['row']), (0,0,255))
        # draw red circle for finish hold
        else:
            img = draw(img, hold_coords, get_radius(hold['row']))
    
    # Display the image
    cv2.imshow("Image with Circle", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return img

def alter_route(route, hold_num, difficulty, ape_index, height) -> list:
    # alters the route list and picks a new hold

    def pick_hold(curr_hold, difficulty, ape_index, height, next_hold=None, previous_hold=None) -> dict:
        """ figure out a way to find new hold when you're at the most difficult or easiest hold already """
        # picks new hold based on type

        # create hold dicts based on categoery and dificulty (0 = easy, 5 = hard)
        categories_by_name = {'jug': 0, 'edge': 1, 'pinch': 2, 'crimp': 3, 'small pinch': 4, 'small crimp': 5}
        categories_by_number = {0: 'jug', 1: 'edge', 2: 'pinch', 3: 'crimp', 4: 'small pinch', 5: 'small crimp'}
        
        # set current hold type, row, and column
        curr_hold_type = curr_hold['hold_type']
        curr_row = curr_hold['row']
        curr_col = curr_hold['col']

        # connect to database
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["Capstone"]
        collection = db["moonBoard"]

        if (next_hold and previous_hold):
            # pick a new intermidiate hold, still within reach of other holds
            if (difficulty):
                # make hold more difficult
                new_hold_type = curr_hold_type

                # loop until new hold is found or return same route
                while (True):
                    # set temporary row number that resests every iteration
                    temp_curr_row = curr_row

                    try:
                        # change hold type to a more difficult one
                        new_hold_type = categories_by_number[categories_by_name[new_hold_type] + 1]
                    except KeyError:
                        # already at max difficulty -> return route
                        client.close()
                        return route
                    
                    # create a list of future rows to find possible replacement holds
                    row_stack = [curr_row - 1, curr_row + 1]

                    for _ in range(len(row_stack) + 1):
                        # find row of holds based on new row number and new hold type -> shuffle list
                        row = list(collection.find({'$and': [{'row': {'$eq': temp_curr_row}}, {'hold_type': f'{new_hold_type}'}]}))
                        r.shuffle(row)

                        for hold in row:
                            previous_hold_row_col = (previous_hold['row'], previous_hold['col'])
                            next_hold_row_col = (next_hold['row'], next_hold['col'])

                            # returns new hold if it's within reach of previous and next hold
                            if (within_reach((hold['row'], hold['col']), next_hold_row_col, ape_index, height) and within_reach(previous_hold_row_col, (hold['row'], hold['col']), ape_index, height)):
                                client.close()
                                return hold
                            
                        # new hold hasn't been found -> redo proccess with new row number
                        if (len(row_stack) > 0):
                            temp_curr_row = row_stack.pop()
                    # didn't find a new hold, repeat proccess with harder hold type
            else:
                # make hold easier
                new_hold_type = curr_hold_type

                # loop until new hold is found or return same route
                while (True):
                    # set temporary row number that resests every iteration
                    temp_curr_row = curr_row
                    
                    try:
                        # change hold type to an easier one
                        new_hold_type = categories_by_number[categories_by_name[new_hold_type] - 1]
                    except KeyError:
                        # already at easiest difficulty -> return route
                        client.close()
                        return route
                    
                    # create a list of future rows to find possible replacement holds
                    row_stack = [curr_row + 1, curr_row - 1]

                    for _ in range(len(row_stack) + 1):
                        # find row of holds based on new row number and new hold type -> shuffle list
                        row = list(collection.find({'$and': [{'row': {'$eq': temp_curr_row}}, {'hold_type': f'{new_hold_type}'}]}))
                        r.shuffle(row)

                        for hold in row:
                            previous_hold_row_col = (previous_hold['row'], previous_hold['col'])
                            next_hold_row_col = (next_hold['row'], next_hold['col'])

                            # returns new hold if it's within reach of previous and next hold
                            if (within_reach((hold['row'], hold['col']), next_hold_row_col, ape_index, height) and within_reach(previous_hold_row_col, (hold['row'], hold['col']), ape_index, height)):
                                client.close()
                                return hold
                            
                        # new hold hasn't been found -> redo proccess with new row number
                        if (len(row_stack) > 0):
                            temp_curr_row = row_stack.pop()
                    # didn't find a new hold, repeat proccess with easier hold type

        elif (next_hold):
            # pick a new start hold, still within reach of next hold
            if (difficulty):
                # make start more difficult
                new_hold_type = curr_hold_type

                # loop until new hold is found or return same route
                while (True):
                    # set temporary row number that resests every iteration
                    temp_curr_row = curr_row

                    try:
                        # change hold type to a more difficult one
                        new_hold_type = categories_by_number[categories_by_name[new_hold_type] + 1]
                    except KeyError:
                        # already at max difficulty -> return route
                        client.close()
                        return route

                    # create a list of future rows to find possible replacement holds
                    row_stack = [curr_row - 1, curr_row + 1]

                    for _ in range(len(row_stack) + 1):
                        # find row of holds based on new row number and new hold type -> shuffle list
                        row = list(collection.find({'$and': [{'row': {'$eq': temp_curr_row}}, {'hold_type': f'{new_hold_type}'}]}))
                        r.shuffle(row)

                        for hold in row:
                            next_hold_row_col = (curr_row, curr_col)
                            # returns new hold if it's within reach of next hold
                            if (within_reach((hold['row'], hold['col']), next_hold_row_col, ape_index, height)):
                                client.close()
                                return hold
                        
                        # new hold hasn't been found -> redo proccess with new row number
                        if (len(row_stack) > 0):
                            temp_curr_row = row_stack.pop()
                    # didn't find a new hold, repeat proccess with harder hold type
            else:
                # make start easier
                new_hold_type = curr_hold_type

                # loop until new hold is found or return same route
                while (True):
                    # set temporary row number that resests every iteration
                    temp_curr_row = curr_row

                    try:
                        # change hold type to an easier one
                        new_hold_type = categories_by_number[categories_by_name[new_hold_type] - 1]
                    except KeyError:
                        # already at easiest difficulty -> return route
                        client.close()
                        return route

                    # create a list of future rows to find possible replacement holds
                    row_stack = [curr_row + 1, curr_row - 1]

                    for _ in range(len(row_stack) + 1):
                        # find row of holds based on new row number and new hold type -> shuffle list
                        row = list(collection.find({'$and': [{'row': {'$eq': temp_curr_row}}, {'hold_type': f'{new_hold_type}'}]}))
                        r.shuffle(row)

                        for hold in row:
                            next_hold_row_col = (curr_row, curr_col)
                            # returns new hold if it's within reach of next hold
                            if (within_reach((hold['row'], hold['col']), next_hold_row_col, ape_index, height)):
                                client.close()
                                return hold
                            
                        # new hold hasn't been found -> redo proccess with new row number
                        if (len(row_stack) > 0):
                            temp_curr_row = row_stack.pop()
                    # didn't find a new hold, repeat proccess with easier hold type            
        
        elif (previous_hold):
            # pick a new finish hold, still within reach of next hold
            if (difficulty):
                # make hold more difficult
                new_hold_type = curr_hold_type

                # loop until new hold is found or return same route
                while (True):
                    try:
                        # change hold type to a more difficult one
                        new_hold_type = categories_by_number[categories_by_name[new_hold_type] + 1]
                    except KeyError:
                        # already at max difficulty -> return route
                        client.close()
                        return route

                    # query last row based on new hold type -> shuffle row
                    row = list(collection.find({'$and': [{'row': {'$eq': 18}}, {'hold_type': f'{new_hold_type}'}]}))
                    r.shuffle(row)

                    for hold in row:
                        previous_hold_row_col = (previous_hold['row'], previous_hold['col'])
                        # returns new hold if it's within reach of previous hold
                        if (within_reach((hold['row'], hold['col']), previous_hold_row_col, ape_index, height)):
                            client.close()
                            return hold
                    # didn't find a new hold, repeat proccess with harder hold type
            else:
                # make hold easier
                new_hold_type = curr_hold_type

                # loop until new hold is found or return same route
                while (True):
                    try:
                        # change hold type to an easier one
                        new_hold_type = categories_by_number[categories_by_name[new_hold_type] - 1]
                    except KeyError:
                        # already at easiest difficulty -> return route
                        client.close()
                        return route

                    # query last row based on new hold type -> shuffle row
                    row = list(collection.find({'$and': [{'row': {'$eq': 18}}, {'hold_type': f'{new_hold_type}'}]}))
                    r.shuffle(row)

                    for hold in row:
                        previous_hold_row_col = (previous_hold['row'], previous_hold['col'])
                        # returns new hold if it's within reach of previous hold
                        if (within_reach((hold['row'], hold['col']), previous_hold_row_col, ape_index, height)):
                            client.close()
                            return hold
                    # didn't find a new hold, repeat proccess with easier hold type

        else:
            # wrong input raise error
            client.close()
            raise ValueError

    hold_index = hold_num - 1
    curr_hold = route[hold_index]
    
    if (hold_index == 0):
        # changes the start hold
        next_hold = route[hold_index + 1]
        new_hold = pick_hold(curr_hold, difficulty, ape_index, height, next_hold=next_hold)
        route.pop(0)
        route.insert(0, new_hold)
    elif (hold_num == len(route)):
        # changes the finish hold
        previous_hold = route[hold_index - 1]
        new_hold = pick_hold(curr_hold, difficulty, ape_index, height, previous_hold=previous_hold)
        route.pop()
        route.append(new_hold)
    else:
        # changes an intermidiate hold
        previous_hold = route[hold_index - 1]
        next_hold = route[hold_index + 1]
        new_hold = pick_hold(curr_hold, difficulty, ape_index, height, next_hold, previous_hold)
        route.pop(hold_index)
        route.insert(hold_index, new_hold)

    return route

def load_route(route_name) -> list:
    # creates a list of holds based on route name
    route = []

    # connect to routes database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["Capstone"]
    routes_collection = db["routes"]
    moonBoard_collection = db['moonBoard']

    # get hold id's based on route name form routes database
    ids = routes_collection.find({'name': route_name})
    # if route doesn't exist in database return None
    if not ids:
        print(f'{route_name} is not a saved route')
        client.close()
        return None
    start_id = ids['start']
    intermidiate_ids = ids['intermidiates']
    finish_id = ids['finish']

    # get the equivalent holds based on ids
    route.append(moonBoard_collection.find({'_id': start_id}))
    for i in intermidiate_ids:
        route.append(moonBoard_collection.find({'_id': i}))
    route.append(moonBoard_collection.find({'_id': finish_id}))

    client.close()
    return route

def upload_route(route_name, hold_list) -> None:
    # save holds by name, start, intermidiates, and finsih

    # connect to routes database
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["Capstone"]
    collection = db["routes"]

    # get start hold, finish hold, and list of intermidiates
    start = hold_list.pop(0)['_id']
    finish = hold_list.pop()['_id']
    intermidiates = [x['_id'] for x in hold_list]

    # insert into routes database
    collection.insert_one({'name': route_name, 'start': start, 'finish': finish, 'intermidiates': intermidiates})

    # disconnect from db
    client.close()

def main():
    usr_input = input('would you like to load or create a route? (l/c) ').lower()

    if (usr_input == 'c'):
        routes = [create_route('crimp')]
        img = print_route(routes[-1])

        # user input prompts
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
        
        name = input('What would you like to name the route: ')

        upload_route(name, routes[-1])

        # saves image to laptop
        usr_input = input('Would you like to save the route image? (y/n) ').lower()
        if (usr_input == 'y'):
            cv2.imwrite(f"{name}.jpg", img)

    elif (usr_input == 'l'):
        name = input('what is the name of the route you wish to load? ')

        route = load_route(name)

        if (route):
            print_route(route)

    else:
        print('you chose poorly')

if __name__ == '__main__':
    main()
