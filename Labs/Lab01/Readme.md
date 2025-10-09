# 🖧 TCP Socket Programming in C

This project demonstrates a simple TCP socket-based communication between a **client** and a **server** written in the C programming language using the POSIX socket API.

---

## 📂 Files

- `server.c` – The TCP server that listens for incoming connections and sends a response.
- `client.c` – The TCP client that connects to the server and sends a message.

---

## ⚙️ How It Works

### Server:
1. Creates a TCP socket.
2. Binds to `0.0.0.0:8080`.
3. Listens for a connection.
4. Accepts a client.
5. Receives data from the client.
6. Sends a response to the client.
7. Closes the connection.

### Client:
1. Creates a TCP socket.
2. Connects to the server at `127.0.0.1:8080`.
3. Sends a message to the server.
4. Receives a response.
5. Closes the connection.

---

## 🧪 How to Compile & Run

### 1. Compile

```bash
gcc server.c -o server
gcc client.c -o client