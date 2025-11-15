# Socket Programming 

## Overview

Contains two Python programs demonstrating TCP and UDP socket communication. Each program supports both server and client modes.

## Files

* **tcp_chat.py** – TCP-based chat system.
* **udp_enhanced.py** – UDP-based timestamped ACK system.

## TCP Program (tcp_chat.py)

* Server listens on **127.0.0.1:5050**.
* Client connects and exchanges messages with the server.
* Server replies with `Server Received: <message>`.
* Sending `exit` closes the connection gracefully.

### How to Run

**Start TCP Server:**

```
python tcp_chat.py server
```

**Start TCP Client:**

```
python tcp_chat.py client
```

## UDP Program (udp_enhanced.py)

* Server listens on **127.0.0.1:6060**.
* Client sends messages and waits for timestamped ACK: `ACK <HH:MM:SS>`.
* If no ACK is received within 3 seconds, client prints `Packet lost (timeout)`.
* Sending `exit` stops both client and server.

### How to Run

**Start UDP Server:**

```
python udp_enhanced.py server
```

**Start UDP Client:**

```
python udp_enhanced.py client
```

## Summary

These programs demonstrate:

* Persistent TCP connections
* Connectionless UDP messaging
* Timeout handling
* Graceful shutdown using the `exit` command