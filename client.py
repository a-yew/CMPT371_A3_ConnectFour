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
import queue
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
            - https://tkdocs.com/tutorial/text.html
            - https://docs.python.org/3/library/tk.html
            - https://stackoverflow.com/questions/70298196/how-can-i-use-tkinter-to-make-an-animation
            - https://pypi.org/project/tk-animations/
            - https://python-course.eu/tkinter/canvas-widgets-in-tkinter.php
"""

# sizing
ROWS = 6
COLS = 7
CELL_SIZE = 80
BOARD_PAD = 24
TOKEN_PAD = 10

# colours
BG = "#0a0a14"
BOARD_BG = "#0d1b3e"
BOARD_DARK = "#081230"
EMPTY_COLOUR = "#0a1428"
RED_COLOUR = "#e70a33"
RED_GLOW = "#ff6b81"
YEL_COLOUR = "#ffd500"
YEL_GLOW = "#ffe566"
GRID_COLOUR = "#1557dd"
TEXT_LIGHT = "#e8eaf6"
TEXT_DULL = "#4d67b4"
HIGHLIGHT = "#f158ff"

# animations
STEPS = 10
DELAY = 14


class ConnectFourGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CMPT 371 - Connect 4")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # game state
        self.playerRole = None
        self.myTurn = False
        self.client = None
        self.board = None
        self.animating = False
        self.hover_col = None

        # thread-safe queue: recv thread to main thread
        self.msgQueue = queue.Queue()

        # draw UI
        self.drawStatBar()
        self.drawBoard()
        self.drawColBtns()

        # connect to server in background so the GUI doesn't freeze
        threading.Thread(target=self.connectToServer, daemon=True).start()

        # start polling the message queue every 50 ms
        self.root.after(50, self.pollQueue)

        # dot animation for waiting status
        self.numDots = 0
        self.root.after(500, self.movingDots)


    def drawStatBar(self):
        # title banner
        titleFrame = tk.Frame(self.root, bg=BG)
        titleFrame.pack(pady=(24, 0))

        tk.Label(titleFrame, text="CONNECT 4", bg=BG, fg=TEXT_LIGHT, font=("Courier New", 28, "bold"),
            ).pack(side="left")

        # player tag
        tags = tk.Frame(self.root, bg=BG)
        tags.pack(pady=(8, 0))

        self.tagRed = tk.Label(tags, text="RED", bg=BG, fg=TEXT_DULL,
                                font=("Courier New", 12, "bold"))
        self.tagRed.pack(side="left", padx=12)

        tk.Label(tags, text="VS", bg=BG, fg=TEXT_DULL,
                 font=("Courier New", 11)).pack(side="left")

        self.tagYellow = tk.Label(tags, text="YELLOW", bg=BG, fg=TEXT_DULL,
                                font=("Courier New", 12, "bold"))
        self.tagYellow.pack(side="left", padx=12)

        # status labels
        statusFrame = tk.Frame(self.root, bg=BG)
        statusFrame.pack(pady=(12, 0))

        self.statusVar = tk.StringVar(value="Connecting to server…")
        self.statusLabel = tk.Label(
            statusFrame,
            textvariable=self.statusVar,
            bg=BG, fg=HIGHLIGHT,
            font=("Courier New", 13, "bold"),
        )
        self.statusLabel.pack()

        self.subStatusVar = tk.StringVar(value="")
        tk.Label(
            statusFrame,
            textvariable=self.subStatusVar,
            bg=BG, fg=TEXT_DULL,
            font=("Courier New", 10),
        ).pack()

    def drawBoard(self):
        canvasWidth = COLS * CELL_SIZE + 20
        canvasHeight = ROWS * CELL_SIZE + 20

        boardWrapper = tk.Frame(
            self.root, bg=BOARD_BG, bd=0,
            highlightthickness=3, highlightbackground=GRID_COLOUR,
        )
        boardWrapper.pack(padx=BOARD_PAD, pady=16)

        self.canvas = tk.Canvas(
            boardWrapper,
            width=canvasWidth, height=canvasHeight,
            bg=BOARD_BG, highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack()

        # draw static grid + piece ovals + hover preview
        self.drawGrid()

        # mouse movements
        # https://python-course.eu/tkinter/events-and-binds-in-tkinter.php
        self.canvas.bind("<Motion>", self.hover)
        self.canvas.bind("<Leave>", self.mouseLeave)
        self.canvas.bind("<Button-1>", self.click)

    def drawColBtns(self):
        btnFrame = tk.Frame(self.root, bg=BG)
        btnFrame.pack(pady=(0, BOARD_PAD))

        self.colButtons = []
        for col in range(COLS):
            btn = tk.Button(
                btnFrame,
                text=str(col), width=4,
                font=("Courier New", 12, "bold"),
                bg=RED_COLOUR, fg=TEXT_LIGHT,
                activebackground=YEL_COLOUR, activeforeground=BG,
                relief=tk.FLAT, state=tk.DISABLED,
                command=lambda c=col: self.sendMove(c),
            )
            btn.pack(side=tk.LEFT, padx=6)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=YEL_COLOUR, fg=BG))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=RED_COLOUR, fg=TEXT_LIGHT))
            self.colButtons.append(btn)

    # board helpers
    def cellPos(self, row, col):
        return col * CELL_SIZE + 10, row * CELL_SIZE + 10

    def tokenBounds(self, row, col):
        x, y = self.cellPos(row, col)
        return (x + TOKEN_PAD, y + TOKEN_PAD,
                x + CELL_SIZE - TOKEN_PAD, y + CELL_SIZE - TOKEN_PAD)

    def drawGrid(self):
        for r in range(ROWS):
            for c in range(COLS):
                x, y = self.cellPos(r, c)
                self.canvas.create_rectangle(
                    x, y, x + CELL_SIZE, y + CELL_SIZE,
                    fill=BOARD_BG, outline=GRID_COLOUR, width=1,
                )
                self.canvas.create_oval(
                    *self.tokenBounds(r, c),
                    fill=BOARD_DARK, outline=BOARD_DARK, width=0,
                    tags=f"hole_{r}_{c}",
                )

        # token circles drawn above holes
        for r in range(ROWS):
            for c in range(COLS):
                self.canvas.create_oval(
                    *self.tokenBounds(r, c),
                    fill=EMPTY_COLOUR, outline=EMPTY_COLOUR, width=0,
                    tags=f"piece_{r}_{c}",
                )

        # hover preview circle
        self.canvas.create_oval(
            0, 0, 1, 1,
            fill="", outline="", width=2,
            tags="hover_preview",
        )



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
        # same as TCP stream-splitting logic as startClient() but uses queue instead of calling UI methods directly
        buffer = ""
        while True:
            try:
                raw = self.client.recv(4096).decode('utf-8')
                if not raw:
                    break
                buffer += raw
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            msg = json.loads(line)
                            self.msgQueue.put(msg)
                        except json.JSONDecodeError:
                            pass
            except (ConnectionResetError, OSError):
                break

    def pollQueue(self):
        # drains the message queue on the main thread every 50 ms
        while not self.msgQueue.empty():
            msg = self.msgQueue.get_nowait()
            self.handleMsg(msg)
        self.root.after(50, self.pollQueue)

    def handleMsg(self, msg):
        # route each message type
        # UI updates go via root.after() cause Tkinter isn't thread-safe
        if msg["type"] == "WELCOME":
            self.playerRole = msg["payload"][-1]
            color = RED_COLOUR if self.playerRole == 'R' else YEL_COLOUR

            # light up the matching badge
            if self.playerRole == 'R':
                self.tagRed.config(fg=RED_COLOUR)
            else:
                self.tagYellow.config(fg=YEL_COLOUR)

            self.setStat(f"You are Player {self.playerRole}. Match found!",
                         sub="Red goes first. Get ready!", color=color)

        elif msg["type"] == "UPDATE":
            self.update(msg)

        elif msg["type"] == "ERROR":
            self.setStat("Invalid move, please try again.", sub="", color="red")

    def update(self, msg):
        # redraws board + flips turn state
        # same logic as the UPDATE block in startClient()
        self.board = msg["board"]
        self.redrawBoard(self.board)

        status = msg.get("status", "ongoing")
        turn = msg.get("turn")

        if status != "ongoing":
            if "wins" in status:
                winner = status.split()[1]
                color  = RED_COLOUR if winner == 'R' else YEL_COLOUR
                self.setStat(f"{status}", color=color,
                             sub="Thank you for playing! Close the window to exit.")
            else:
                self.setStat("It's a Draw!", color=HIGHLIGHT,
                             sub="Maybe someone will win next time.")
            self.myTurn = False
            self.disableAllBtns()
            messagebox.showinfo("Game Over", status)
            self.client.close()
            return

        self.myTurn = (turn == self.playerRole)
        if self.myTurn:
            color = RED_COLOUR if self.playerRole == 'R' else YEL_COLOUR
            self.setStat("YOUR TURN", color=color,
                         sub="Click a column or press a button to drop your piece.")
            self.enableBtn()
        else:
            other = 'Red' if turn == 'R' else 'Yellow'
            self.setStat(f"Waiting for {other}", color=TEXT_DULL, sub="")
            self.disableAllBtns()

    # board rendering
    def redrawBoard(self, board):
        colourMap = {
            '.': (EMPTY_COLOUR, EMPTY_COLOUR),
            'R': (RED_COLOUR, RED_GLOW),
            'Y': (YEL_COLOUR, YEL_GLOW),
        }
        for row in range(ROWS):
            for col in range(COLS):
                fill, outline = colourMap[board[row][col]]
                self.canvas.itemconfig(
                    f"piece_{row}_{col}",
                    fill=fill, outline=outline,
                )

    # hover preview
    def colFromX(self, x):
        col = (x - 10) // CELL_SIZE
        return col if 0 <= col < COLS else None

    def landingRow(self, col):
        if self.board is None:
            return -1
        for row in range(ROWS - 1, -1, -1):
            if self.board[row][col] == '.':
                return row
        return -1

    def showHover(self, col):
        if not self.myTurn or self.animating or col is None:
            self.canvas.itemconfig("hover_preview", fill="", outline="")
            return
        if self.landingRow(col) == -1:
            self.canvas.itemconfig("hover_preview", fill="", outline=TEXT_DULL)
            return
        x, y = self.cellPos(0, col)
        bbox  = (x + TOKEN_PAD, y + TOKEN_PAD,
                 x + CELL_SIZE - TOKEN_PAD, y + CELL_SIZE - TOKEN_PAD)
        color = RED_COLOUR if self.playerRole == 'R' else YEL_COLOUR
        self.canvas.coords("hover_preview", *bbox)
        self.canvas.itemconfig("hover_preview", fill="", outline=color, width=3)

    def hover(self, event):
        col = self.colFromX(event.x)
        if col != self.hover_col:
            self.hover_col = col
            self.showHover(col)

    def mouseLeave(self, _event):
        self.hover_col = None
        self.canvas.itemconfig("hover_preview", fill="", outline="")

    # coin drop animation
    def dropCoin(self, col, targetRow, symbol, callback):
        self.animating = True
        color = RED_COLOUR if symbol == 'R' else YEL_COLOUR
        glow = RED_GLOW  if symbol == 'R' else YEL_GLOW

        x, y = self.cellPos(0, col)
        animId = self.canvas.create_oval(
            x + TOKEN_PAD, y + TOKEN_PAD,
            x + CELL_SIZE - TOKEN_PAD, y + CELL_SIZE - TOKEN_PAD,
            fill=color, outline=glow, width=2,
            tags="anim_piece",
        )

        stepSize = CELL_SIZE / STEPS
        totalPixels = targetRow * CELL_SIZE
        moved = [0]

        def step():
            if moved[0] < totalPixels:
                remaining = totalPixels - moved[0]
                delta = min(stepSize * 2, remaining)
                self.canvas.move(animId, 0, delta)
                moved[0] += delta
                self.root.after(DELAY, step)
            else:
                self.canvas.delete(animId)
                self.animating = False
                callback()

        self.root.after(DELAY, step)

    # canvas click handler
    def click(self, event):
        if not self.myTurn or self.animating or self.client is None:
            return
        col = self.colFromX(event.x)
        if col is None:
            return
        targetRow = self.landingRow(col)
        if targetRow == -1:
            self.setStat("This column is full!", sub="Please choose another column.", color="red")
            return

        self.myTurn = False
        self.canvas.itemconfig("hover_preview", fill="", outline="")
        self.disableAllBtns()

        def afterAnim():
            self.sendMove(col)

        self.dropCoin(col, targetRow, self.playerRole, afterAnim)

    # player actions
    def sendMove(self, col):
        if self.client is None:
            return
        self.setStat("Move sent. Waiting for server…", sub="", color=HIGHLIGHT)
        moveMsg = json.dumps({"type": "MOVE", "col": col}) + '\n'
        try:
            self.client.sendall(moveMsg.encode('utf-8'))
        except OSError:
            pass

    # helpers
    def setStat(self, text, sub="", color=HIGHLIGHT):
        self.statusVar.set(text)
        self.subStatusVar.set(sub)
        self.statusLabel.config(fg=color)

    def enableBtn(self):
        for btn in self.colButtons:
            btn.config(state=tk.NORMAL)

    def disableAllBtns(self):
        for btn in self.colButtons:
            btn.config(state=tk.DISABLED)

    # dot animation
    def movingDots(self):
        current = self.statusVar.get()
        if "Waiting" in current or "waiting" in current:
            dots = "." * ((self.numDots % 3) + 1)
            base = current.rstrip(".")
            self.statusVar.set(base + dots)
            self.numDots += 1
        self.root.after(500, self.movingDots)


def startGUIClient():
    root = tk.Tk()
    ConnectFourGUI(root)
    root.mainloop()


if __name__=="__main__": 
    if "--gui" in sys.argv:
        startGUIClient()
    else:
        startClient()
