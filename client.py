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