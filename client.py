"""
CMPT 371 A3: Multiplayer Connect 4 - Client
Architecture: JSON over TCP Protocol
References: - Mariam's Tic-Tac-Toe Tutorial
            - Python Network Programming: TCP/IP Socket Programming (YouTube Playlist linked in A3 Instructions)
"""

import socket
import json
import sys

# connection settings (match server.py)
HOST = '127.0.0.1'
PORT = 5050


# display connect-four board
def displayBoard():

# REMOVE temp test initial board state
    board = []

    for row in range(6):
        row = []

        for col in range(7):
            row.append('.')
        
        board.append(row)

    for row in board: 
        print (" ".join(row))

"""
# Code from CMPT 371 Python Socket Programming Tutorial
# client execution loop
def startClient(): 
    # initialize IPv4 and TCP socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # initiate TCP handshake and send a connection request to server
    client.sendall(json.dumps({"type": "CONNECT"}).encode('utf-8'))
    print("Connected to game. Waiting for Player 2 to join")
    
    playerRole = None

    while True: 
        # wait for session data 
        data = client.recv(1024).decode('utf-8')
        
        # fix TCP stream buffering by spliting JSON packets 
        for chunk in data.strip().split('\n'):
            if not chunk: continue

            # deserialize JSON packet into messages
            msg = json.loads(chunk)

            # assign player roles
            if msg["type"] == "WELCOME":
    
                # payload format is "Player 1" or "Player 2"
                player = msg["payload"][-1]
                print(f"Match found. You are Player {playerRole}.")
            
            # update game state
            elif msg["type"] == "UPDATE":
                displayBoard(msg["board"])
            
                # check for terminating conditions from server
                if msg["type"] != "ongoing"
                    print(f"Game Over: {msg['status']}")
                    client.close()
                    sys.exit(0)

                # print player turn
                if msg["turn"] == playerRole:
                    print("Your turn.")
                    
                    # validate game state 
                    r_str, c_str = input("Enter row and column number to drop token (e.g. '1 1'): ".split()
                    
                    
                    # package player's move coordinates into MOVE packet
                    moveMsg = json.dumps({"type": "MOVE", "row": int(r_str), "col": int(c_str) + '\n'
                    client.sendall(moveMsg.encode('utf-8')
                    
                    else: 
                        print("Waiting for opponent's move.")

    client.close()
"""

if __name__=="__main__": 
    displayBoard()
    # startClient()
