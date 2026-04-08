"""
CMPT 371 A3: Multiplayer Connect 4 - Client
Architecture: JSON over TCP Protocol
References: - Mariam's Tic-Tac-Toe Tutorial
            - Python Network Programming: TCP/IP Socket Programming (YouTube Playlist linked in A3 Instructions)
"""

import socket
import json
import sys
import threading
import tkinter as tk
from tkinter import messagebox

# connection settings (match server.py)
HOST = '127.0.0.1'
PORT = 5050


# display connect-four board
def displayBoard(board):
   
    for row in board: 
        print (" ".join(row))
    
    print("0 1 2 3 4 5 6\n")

# Code from CMPT 371 Python Socket Programming Tutorial
# client execution loop
def startClient(): 
    # initialize IPv4 and TCP socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

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
    
                # payload format is "Player R" or "Player Y"
                playerRole = msg["payload"][-1]
                print(f"Match found. You are Player {playerRole}.")
            
            # update game state
            elif msg["type"] == "UPDATE":
                displayBoard(msg["board"])
            
                # check for terminating conditions from server
                if msg["status"] != "ongoing":
                    print(f"Game Over: {msg['status']}")
                    client.close()
                    sys.exit(0)

                # print player turn
                if msg["turn"] == playerRole:
                    print("Your turn.")
                    
                    # validate game state 
                    col = input("Enter column number to drop token: ") 
                    
                    # package player's move coordinates into MOVE packet
                    moveMsg = json.dumps({"type": "MOVE", "col": int(col)}) + '\n'
                    client.sendall(moveMsg.encode('utf-8'))
                    
                else: 
                    print("Waiting for opponent's move.")

    client.close()



"""
GUI Implementation - Client
References: - https://www.pythonguis.com/tutorials/create-gui-tkinter/
            - https://realpython.com/python-gui-tkinter/
"""

# gui constants
ROWS = 6
COLS = 7
CELL_SIZE = 80
BOARD_PAD = 24
TOKEN_PAD = 8
COLOUR_BOARD = "#1a6fb5"
COLOUR_EMPTY = "#0d1117"
COLOUR_RED = "#e84855"
COLOUR_YELLOW = "#f9c846"
COLOUR_BTN_NORMAL = "#FF0000"
COLOUR_BTN_HOVER = "#000000"
COLOUR_BG = "#0d1117"
COLOUR_TEXT = "#FFFFFF"


class ConnectFourGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CMPT 371 - Connect 4")
        self.root.configure(bg=COLOUR_BG)
        self.root.resizable(False, False)

        self.playerRole = None
        self.myTurn = False
        self.client = None

        self.drawStatBar()
        self.drawBoard()
        self.drawColBtns()

        # connect to server in background so the GUI doesn't freeze
        threading.Thread(target=self.connectToServer, daemon=True).start()


    def drawStatBar(self):
        self.statusVar = tk.StringVar(value="Connecting to server…")
        tk.Label(
            self.root,
            textvariable=self.statusVar,
            bg=COLOUR_BG, fg=COLOUR_TEXT,
            font=("Courier New", 14, "bold"),
            pady=10,
        ).pack(fill=tk.X)

    def drawBoard(self):
        board_width  = COLS * CELL_SIZE + BOARD_PAD * 2
        board_height = ROWS * CELL_SIZE + BOARD_PAD * 2

        self.canvas = tk.Canvas(
            self.root,
            width=board_width, height=board_height,
            bg=COLOUR_BOARD, highlightthickness=0,
        )
        self.canvas.pack(padx=BOARD_PAD, pady=(0, 5))

        self.cells = []

        for row in range(ROWS):
            rowList = []
            for col in range(COLS):
                x1 = BOARD_PAD + col * CELL_SIZE + TOKEN_PAD
                y1 = BOARD_PAD + row * CELL_SIZE + TOKEN_PAD
                x2 = x1 + CELL_SIZE - TOKEN_PAD * 2
                y2 = y1 + CELL_SIZE - TOKEN_PAD * 2
                oval = self.canvas.create_oval(
                    x1, y1, x2, y2,
                    fill=COLOUR_EMPTY, outline=COLOUR_BOARD, width=2,
                )
                rowList.append(oval)
            self.cells.append(rowList)

    def drawColBtns(self):
        btnFrame = tk.Frame(self.root, bg=COLOUR_BG)
        btnFrame.pack(pady=(10, BOARD_PAD))

        self.colButtons = []
        for col in range(COLS):
            btn = tk.Button(
                btnFrame,
                text=str(col), width=4,
                font=("Courier New", 12, "bold"),
                bg=COLOUR_BTN_NORMAL, fg=COLOUR_TEXT,
                activebackground=COLOUR_BTN_HOVER, activeforeground=COLOUR_TEXT,
                relief=tk.FLAT, state=tk.DISABLED,
                command=lambda c=col: self.sendMove(c),
            )
            btn.pack(side=tk.LEFT, padx=6)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLOUR_BTN_HOVER))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLOUR_BTN_NORMAL))
            self.colButtons.append(btn)

    # networking
    def connectToServer(self):
        # mirrors startClient() but feeds messages into the GUI instead of print()
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((HOST, PORT))

            # same handshake as the CLI client
            self.client.sendall(json.dumps({"type": "CONNECT"}).encode('utf-8'))
            self.setStat("Waiting for Player 2 to join…")
            self.receiveLoop()

        except ConnectionRefusedError:
            self.root.after(0, lambda: messagebox.showerror(
                "Connection Failed",
                f"Could not connect to {HOST}:{PORT}.\nMake sure server.py is running."
            ))

    def receiveLoop(self):
        # same TCP stream splitting logic as startClient()
        while True:
            try:
                data = self.client.recv(1024).decode('utf-8')
                if not data:
                    break
                # fix TCP stream buffering (same approach as CLI client)
                for chunk in data.strip().split('\n'):
                    if chunk:
                        self.handleMsg(json.loads(chunk))
            except (ConnectionResetError, OSError):
                break

    def handleMsg(self, msg):
        # route each message type
        # UI updates go via root.after() cause Tkinter isn't thread-safe
        if msg["type"] == "WELCOME":
            self.playerRole = msg["payload"][-1]
            self.root.after(0, lambda: self.setStat(f"You are Player {self.playerRole}. Match found!"))

        elif msg["type"] == "UPDATE":
            self.root.after(0, lambda m=msg: self.update(m))

        elif msg["type"] == "ERROR":
            self.root.after(0, lambda: self.setStat(f"Invalid move — try again."))

    def update(self, msg):
        """Redraws board and flips turn state. Same logic as the UPDATE block in startClient()."""
        self.redrawBoard(msg["board"])

        status = msg.get("status", "ongoing")
        turn = msg.get("turn")

        if status != "ongoing":
            self.setStat(f"Game Over: {status}")
            self.disableAllBtns()
            messagebox.showinfo("Game Over", status)
            self.client.close()
            return

        self.myTurn = (turn == self.playerRole)
        if self.myTurn:
            self.setStat("Your turn! Pick a column ↓")
            self.enableBtn()
        else:
            self.setStat("Waiting for opponent's move…")
            self.disableAllBtns()

    # board rendering
    def redrawBoard(self, board):
        colourMap = {'.': COLOUR_EMPTY, 'R': COLOUR_RED, 'Y': COLOUR_YELLOW}
        for row in range(ROWS):
            for col in range(COLS):
                self.canvas.itemconfig(self.cells[row][col], fill=colourMap[board[row][col]])

    # player actions
    def sendMove(self, col):
        if not self.myTurn:
            return
        self.disableAllBtns()
        self.setStat("Move sent. Waiting for server…")
        moveMsg = json.dumps({"type": "MOVE", "col": col}) + '\n'
        self.client.sendall(moveMsg.encode('utf-8'))

    # helpers
    def setStat(self, text):
        self.statusVar.set(text)

    def enableBtn(self):
        for btn in self.colButtons:
            btn.config(state=tk.NORMAL)

    def disableAllBtns(self):
        for btn in self.colButtons:
            btn.config(state=tk.DISABLED)


def startGUIClient():
    root = tk.Tk()
    ConnectFourGUI(root)
    root.mainloop()


if __name__=="__main__": 
    if "--gui" in sys.argv:
        startGUIClient()
    else:
        startClient()
