# CMPT 371 A3 Socket Programming Connect-4

**Course:** CMPT 371 - Data Communications & Networking  
**Instructor:** Mirza Zaeem Baig  
**Semester:** Spring 2026  

Group Members
-
| Name |  Student ID  | Email |
|:-----|:--------:|------:|
| Jien Lynn Yew (Alexis) | 301576314| jly4@sfu.ca |
| Emily Quan |  301584703 | enq@sfu.ca |

# 1. Project Overview & Description
This project is a multiplayer Connect-4 game built using Python's Socket API (TCP). It allows two distinct clients to connect to a central server, be matched into a game lobby, and play against each other in real-time. The server handles the game logic, board state validation, and win-condition checking, ensuring that clients cannot cheat by modifying their local game state.

# 2. System Limitations & Edge Cases
- Tkinter Thread Safety

Limitation: Our application's client interface utilizes `tkinter` which runs GUI updates on the main thread. As network operations are ran on background threads, this can cause unpredicatable behavior if the GUI is updated directly on these threads. To improve our solution, it would be better if we handled all network communication on a separate thread rather than on the main thread. 

- Handling Multiple Concurrent Clients

Solution: The server uses Python’s threading module to support concurrent clients. Incoming clients are placed into a shared `matchQueue`, and once two players join the queue, they are assigned to a dedicated `gameSession` thread. Each thread maintains its own board state, turn logic, and socket communication. This ensures that multiple matches can run simultaneously without blocking the main server loop.

Limitation: As each session requires a dedicated OS-level thread, it would not scale efficiently for high loads due to memory usage. On the enterprise level, we would need to utilize thread pools, or asychronous I/O. 

- TCP Buffering
  
Solution: As message boundaries are not preserved due to TCP's data streaming, we could encounter buffering during packet transmission. Our application implements a newline \n to JSON messages to ensure that incoming data is split.

```
for chunk in data.strip().split('\n'):
        if not chunk: continue
```
Limitation: Our solution is limited as it does not account for additional messages received in the same packet. To improve our solution further, we could iteratively process incoming JSON payloads.

- Input Validation and Security

Limitation: As our application assumes the user is well-behaved, it is vulnerable to exploits from users that send malformed JSON data to the server. To improve our solution further, we could implement validation on the client-side to ensure data is well-formatted. 

# 3. Video Demo
Our 2-minute video demonstration covering connection establishment, data exchange, real-time gameplay, and process termination can be viewed below: 

[Link to Connect-4 Video Demo](https://youtu.be/kGqRFVNWuCs)

# 4. Prerequisites (Fresh Environment)
To run this project, you need:
- Python 3.10 or higher.
- No external pip installations are required (uses standard socket, threading, json, sys, tkinter libraries).
- (Optional) VS Code or Terminal.

# 5. Step-by-Step Run Guide
## Step 1: Start Connect-4 Server
Download the project folder, open your terminal and navigate to the project folder. `cd CMPT371_A3_ConnectFour` The server connection settings binds to HOST '127.0.0.1' on PORT 5050. 



```
python server.py
# Console output: "[STARTING] Connect 4 server listening on 127.0.0.1:5050"
```

## Step 2: Connect Player 1 (R)
Keep the server running and open a new terminal window. Navigate to the project folder and run the client script to start the first client (ensure the GUI flag is used), a GUI window should popup.

```
python client.py --gui 
# GUI output: "Waiting for Player 2 to join..." 
```

## Step 3: Connect Player 2 (Y)
Keep the server and first client running and open a second terminal window. Navigate to the project folder and run the client script again to start the second client (ensure the GUI flag is used), a GUI window should popup.

```
python client.py --gui 
# GUI output: "Waiting for opponent's move..."
```
## Step 4: Gameplay
1. Player R selects a column and drop their token
2. The server updates the board on both screens to reflect the player's selection
3. Player Y takes their turn
4. Gameplay loop continues until win or draw states are achieved
5. The popup "Player {Role} wins!" appears once either player places four tokens in row (horizontally/ diagonally) and client sessions terminates

To terminate server session use Ctrl-C in terminal. 

# 6. Technical Protocol Details (JSON over TCP)
We designed a custom application-layer protocol for data exchange usin JSON over TCP:
- Message Format: {"type": <string>, "payload": <data>}
- Handshake Phase:
    - Client sends: {"type": "CONNECT"}
    - Server responds: {"type": "WELCOME", "payload": "Player R"}
- Gameplay Phase:
    - Client sends: {"type": "MOVE", "col": 0}
    - Server broadcasts: {"type": "UPDATE", "board": board, "turn": turn, "status": status}
  
# 7. Academic Integrity & References
- Code Origin: The socket boilerplate was adapted from Mariam's Tic-Tac-Toe CMPT371_A3_Socket_Programming repository and TA-guided tutorials. The GUI, core multithreaded game logic, protocol, and state management were written by the group.
- GenAI Usage: Claude was used to assist in polishing the coin drop animation and UI.
- References:
    - [Mariam's Socket Programming Repository](https://github.com/mariam-bebawy/CMPT371_A3_Socket_Programming)
    - [Mariam's Socket Programming Tic-Tac-Toe Tutorial Playlist](https://www.youtube.com/playlist?list=PL-8C2cUhmkO1yWLTCiqf4mFXId73phvdx&si=FIq3OxypbBeWHhYm)
    - [Python Network Programming - TCP/IP Socket Programming Playlist](https://www.youtube.com/playlist?list=PLhTjy8cBISErYuLZUvVOYsR1giva2payF)
    - [A Complete Guide to Socket Programming in Python](https://www.datacamp.com/tutorial/a-complete-guide-to-socket-programming-in-python)
    - [Create a GUI Using Tkinter and Python](https://www.pythonguis.com/tutorials/create-gui-tkinter/)
    - [Python GUI Programming: Your Tkinter Tutorial](https://realpython.com/python-gui-tkinter/)
    - [Tk Docs](https://tkdocs.com/tutorial/text.html)
    - [Graphical user interfaces with Tk](https://docs.python.org/3/library/tk.html)
    - [Stack Overflow - How can I use tkinter to make an animation?](https://stackoverflow.com/questions/70298196/how-can-i-use-tkinter-to-make-an-animation)
    - [PyPI - Tk Animations](https://pypi.org/project/tk-animations/)
    - [Python Course - Canvas Widgets in Tkinter](https://python-course.eu/tkinter/canvas-widgets-in-tkinter.php)