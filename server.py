"""
CMPT 371 A3: Multiplayer Connect 4 - Server
Architecture: TCP Sockets with Multithreaded Session Management
References: - Mariam's Tic-Tac-Toe Tutorial
            - Python Network Programming: TCP/IP Socket Programming (YouTube Playlist linked in A3 Instructions)
            - https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python
"""

import socket
import threading
import json

# server configuration
HOST = '127.0.0.1'
PORT = 5050

# board dimensions
ROWS = 6
COLS = 7

# holds connected client sockets until opponent joins
matchQueue = []

# board functions
def createBoard():
    board = []

    for row in range(ROWS):
        row = []

        for col in range(COLS):
            row.append('.')
        
        board.append(row)
    
    return board

def dropToken(board, col, symbol):
    row = ROWS - 1

    # move up until top is reached
    while row >= 0:
        if board[row][col] == '.':
            board[row][col] = symbol
            return row
        
        row -= 1

    return -1 # full column

def isColumnValid(board, col):
    if col < 0 or col >= COLS:
        return False
    
    # if top row of column is empty then it's valid
    return board[0][col] == '.'

def checkWinner(board):

    # check horizontally
    for r in range(ROWS):
        for c in range(COLS - 3): # stop 3 from the right so c+3 stays in bounds
            cell = board[r][c]
            if cell == '.':
                continue # skip empty cells

            if (cell == board[r][c+1] and
                cell == board[r][c+2] and
                cell == board[r][c+3]):
                return cell # horizontal winner

    # check vertically
    for r in range(ROWS - 3): # stop 3 from the bottom so r+3 stays in bounds
        for c in range(COLS):
            cell = board[r][c]
            if cell == '.':
                continue

            if (cell == board[r+1][c] and
                cell == board[r+2][c] and
                cell == board[r+3][c]):
                return cell # vertical winner

    # check diagonally (down-right)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            cell = board[r][c]
            if cell == '.':
                continue

            if (cell == board[r+1][c+1] and
                cell == board[r+2][c+2] and
                cell == board[r+3][c+3]):
                return cell # diagonal winner

    # check diagonally (down-left)
    for r in range(ROWS - 3):
        for c in range(3, COLS): # start at col 3 so c-3 stays in bounds
            cell = board[r][c]
            if cell == '.':
                continue

            if (cell == board[r+1][c-1] and
                cell == board[r+2][c-2] and
                cell == board[r+3][c-3]):
                return cell # diagonal winner

    # check for a draw
    # connect 4 fills from the bottom up, so if the entire top row is filled,
    # the whole board must be full, so that means it's a draw
    top_row_full = all(board[0][c] != '.' for c in range(COLS))
    if top_row_full:
        return 'Draw'

    # nobody has won yet, so keep playing
    return None

# game session
# referenced demo code mainly
def gameSession(connR, connY):
 
    def send(conn, data: dict):
        message = json.dumps(data) + '\n'
        conn.sendall(message.encode('utf-8'))
 
    def broadcast(data: dict):
        send(connR, data)
        send(connY, data)
 
    # tell each player who they are: red or yellow
    send(connR, {"type": "WELCOME", "payload": "Player R"})
    send(connY, {"type": "WELCOME", "payload": "Player Y"})
 
    # initialize game state
    board = createBoard()
    turn = 'R' # red goes first
 
    # send empty board to both players so they can see it
    broadcast({"type": "UPDATE", "board": board, "turn": turn, "status": "ongoing"})
 
    # map player symbols to their sockets
    sockets = {'R': connR, 'Y': connY}
 
    # game loop
    while True:
        activeConn = sockets[turn]
 
        # block here and wait for the current player to send a move
        raw = activeConn.recv(1024).decode('utf-8')
 
        # if multiple messages got buffered by TCP, only take the first one
        firstMessage = raw.strip().split('\n')[0]
 
        try:
            msg = json.loads(firstMessage)
        except json.JSONDecodeError:
            continue
 
        # process a move message
        if msg.get("type") == "MOVE":
            col = msg.get("col", -1) # the column the player wants to drop into
 
            # validate move before applying it
            if not isColumnValid(board, col):
                # send error only to the player who made the bad move
                send(activeConn, {"type": "ERROR", "payload": "Invalid column. Try again."})
                # re-broadcast the current state so they can try again
                broadcast({"type": "UPDATE", "board": board, "turn": turn, "status": "ongoing"})
                continue  # don't advance the turn, same player tries again
 
            dropToken(board, col, turn)
 
            # check if this move ended the game
            winner = checkWinner(board)
            status = "ongoing"
 
            if winner == 'Draw':
                status = "It's a draw!"
            elif winner:
                # winner is R or Y
                status = f"Player {winner} wins!"
            else:
                # no winner yet, swap turns
                turn = 'Y' if turn == 'R' else 'R'
 
            # broadcast the new board to both players
            broadcast({"type": "UPDATE", "board": board, "turn": turn, "status": status})
 
            # if the game is over, exit the loop
            if winner:
                break
 
    # close both sockets when the game ends
    connR.close()
    connY.close()
    print("[SESSION] Game over. Sockets closed.")
 
 
# main loop 
# referenced demo code mainly
def start_server():

    # create a TCP socket (AF_INET = IPv4, SOCK_STREAM = TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT)) # attach the socket to our IP and port
    server.listen() # start listening for incoming connections
    print(f"[STARTING] Connect 4 server listening on {HOST}:{PORT}")
 
    try:
        while True:
            # block until a new client connects
            conn, addr = server.accept()
            print(f"[CONNECTION] New client from {addr}")
 
            # read the client's initial handshake message
            data = conn.recv(1024).decode('utf-8')
 
            # only accept clients that send the proper connect handshake
            if "CONNECT" in data:
                matchQueue.append(conn)
                print(f"[QUEUE] Player added. Queue size: {len(matchQueue)}")
 
                # once we have 2 players, match them and start a game thread
                if len(matchQueue) >= 2:
                    player_r = matchQueue.pop(0)
                    player_y = matchQueue.pop(0)
                    print("[MATCH] Two players found. Starting game session...")
 
                    t = threading.Thread(target=gameSession, args=(player_r, player_y))
                    t.start()
 
    except KeyboardInterrupt:
        # ctrl + c shutdown
        print("\n[SHUTDOWN] Server is shutting down...")
    finally:
        server.close()
 
 
if __name__ == "__main__":
    start_server()
