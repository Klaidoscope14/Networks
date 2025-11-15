import socket
import sys

HOST = '127.0.0.1'
PORT = 5050
BUFFER = 4096
ENC = 'utf-8'

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)

        print(f"[TCP Server] Listening on {HOST}:{PORT}...")
        conn, addr = s.accept()

        with conn:
            print(f"[TCP Server] Connected by {addr}")
            while True:
                try:
                    data = conn.recv(BUFFER)
                except ConnectionResetError:
                    print("[TCP Server] Connection reset by peer.")
                    break
                if not data:
                    print("[TCP Server] No data received. Closing.")
                    break
                msg = data.decode(ENC).strip()

                print(f"[TCP Server] Received from {addr}: {msg}")
                if msg.lower() == "exit":
                    print("[TCP Server] 'exit' received. Closing connection.")
                    try:
                        conn.sendall("Server Received: exit".encode(ENC))
                    except Exception:
                        pass
                    break
                reply = f"Server Received: {msg}"

                try:
                    conn.sendall(reply.encode(ENC))
                except BrokenPipeError:
                    print("[TCP Server] Broken pipe while sending. Closing.")
                    break
        print("[TCP Server] Server stopped.")


def run_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            print(f"[TCP Client] Could not connect to {HOST}:{PORT}. Is the server running?")
            return
        print(f"[TCP Client] Connected to {HOST}:{PORT}. Type messages. Type 'exit' to quit.")

        while True:
            try:
                msg = input()
            except EOFError:
                msg = "exit"
                print()
            if not msg:
                continue
            try:
                s.sendall(msg.encode(ENC))
            except BrokenPipeError:
                print("[TCP Client] Broken pipe. Server may have closed connection.")
                break
            try:
                data = s.recv(BUFFER)
            except ConnectionResetError:
                print("[TCP Client] Connection reset by server.")
                break
            if not data:
                print("[TCP Client] Server closed connection.")
                break
            resp = data.decode(ENC).strip()
            print(resp)
            if msg.lower() == "exit":
                print("[TCP Client] Exiting.")
                break

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("server", "client"):
        print("Usage: python tcp_chat.py [server|client]")
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "server":
        run_server()
    else:
        run_client()