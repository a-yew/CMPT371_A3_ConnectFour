"""
CMPT 371 A3: Multiplayer Connect 4 - Server
Architecture: TCP Sockets with Multithreaded Session Management
References: - Mariam's Tic-Tac-Toe Tutorial
            - Python Network Programming: TCP/IP Socket Programming (YouTube Playlist linked in A3 Instructions)
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