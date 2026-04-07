# CMPT 371 A3 Socket Programming Connect-4

**Course: **CMPT 371 - Data Communications & Networking  
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
        `for chunk in data.strip().split('\n'):
            if not chunk: continue`
  
Limitation: Our solution is limited as it does not account for additional messages received in the same packet. To improve our solution further, we could iteratively process incoming JSON payloads.

- Input Validation and Security
Limitation: As our application assumes the user is well-behaved, it is vulnerable to exploits from users that send invalid data types or malformed JSON data. To improve our solution further, we could implement validation on the client-side to ensure data is well-formatted. 

# 3. Video Demo
Our 2-minute video demonstration covering connection establishment, data exchange, real-time gameplay, and process termination can be viewed below: 

# 4. Prerequisites (Fresh Environment)
To run this project, you need:
- Python 3.10 or higher.
- No external pip installations are required (uses standard socket, threading, json, sys libraries).
- (Optional) VS Code or Terminal.

# 5. Step-by-Step Run Guide
# 6. Technical Protocol Details (JSON over TCP)
We designed a custom application-layer protocol for data exchange usin JSON over TCP:
- Message Format:
- Handshake Phase:
- Gameplay Phase:
  
# 7. Academic Integrity & References
- Code Origin:
- GenAI Usage: 
- References:
