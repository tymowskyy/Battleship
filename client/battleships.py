import socketio

sio = socketio.Client()

CREATE_OR_JOIN_LOBBY_MESSAGE = '1 - Join Lobby\n2 - Create Lobby'
SHIPS = [5, 4, 3, 3, 2]
ships_to_place = None

@sio.event
def connect():
    print('connection established')

@sio.event
def disconnect():
    print('disconnected from server')

@sio.event
def oponent_joined(data):
    global after_input
    print('Oponent joined lobby!')
    print('Choose who to start:\n1 - You\n2 - Your oponent \nAnything else - Random')
    after_input = start_game

@sio.event
def oponent_left(data):
    print('Oponent left lobby!')
    print(f'Lobby ID: {current_lobby}')
    
@sio.event
def game_started(data):
    global after_input, ships_to_place
    print('Game started!')
    ships_to_place = SHIPS.copy()
    print(get_place_ship_message())
    after_input = place_ship

def create_or_join_lobby(user_input):
    global after_input, current_lobby

    if user_input == '1':
        lobby_id = input('Input Lobby ID: ')
        response = sio.call('join_lobby', {'lobby_id': lobby_id})
        if 'error' in response:
            print('ERROR', response['error'])
            print(CREATE_OR_JOIN_LOBBY_MESSAGE)
            return

        current_lobby = lobby_id
        print(f'Joined Lobby {current_lobby}')        
        after_input = None

    elif user_input == '2':
        response = sio.call('create_lobby', {})
        if 'error' in  response:
            print('ERROR', response['error'])
            print(CREATE_OR_JOIN_LOBBY_MESSAGE)
            return

        current_lobby = response['lobby_id']
        print(f'Your Lobby ID is {current_lobby}')
        after_input = None

    else:
        print('Invalid input!')
        print(CREATE_OR_JOIN_LOBBY_MESSAGE)

def start_game(user_data):
    global after_input

    who_starts = 0
    if user_data == '1':
        who_starts = 1
    elif user_data == '2':
        who_starts = 2
    after_input = None
    sio.emit('start_game', {'who_starts': who_starts})

def get_place_ship_message():
    global ships_to_place
    return f'Input position of ship with lenght {ships_to_place[0]}:'

def place_ship(user_data):
    global after_input

    try:
        if len(user_data) != 3 or not user_data[2] in ('v', 'h'):
            raise ValueError()
        x = int(ord(user_data[0]) - ord('a'))
        y = int(user_data[1])
        orientation = user_data[2] == 'v'
    except:
        print('Invalid format of position!')
        print('Should be one char for column (a-j), one char for row (0-9), and one char for orientation (h/v)')
        print(get_place_ship_message())
        return
    else:
        result = sio.call('place_ship', {'x': x, 'y': y, 'orientation': orientation, 'size': ships_to_place[0]})
        print(result)
        if result['success']:
            ships_to_place.pop(0)
            if not ships_to_place:
                print('All ships placed!')
                after_input = None
                return
    print(get_place_ship_message())

def main():
    global after_input

    sio.connect('http://localhost:5000')
    print('Input "quit" to quit the game, "leave" to leave the lobby')
    print(CREATE_OR_JOIN_LOBBY_MESSAGE)

    run = True
    while run:
        user_input = input()
        if user_input == 'exit':
            run = False
            break
        if user_input == 'leave':
            sio.emit('leave_lobby', {})
            after_input = create_or_join_lobby
            print(CREATE_OR_JOIN_LOBBY_MESSAGE)
            continue
        if not after_input is None:
            after_input(user_input)
    sio.disconnect()

after_input = create_or_join_lobby
current_lobby = None

if __name__ == '__main__':
    main()