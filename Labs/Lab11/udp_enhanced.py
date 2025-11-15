#!/usr/bin/env python3
"""
udp_enhanced.py

Usage:
    python udp_enhanced.py server
    python udp_enhanced.py client

Server:
 - listens on 127.0.0.1:6060
 - for every datagram prints the data and address
 - replies with "ACK <HH:MM:SS>"
 - if receives "exit" from a client, stops the server

Client:
 - sends datagrams to 127.0.0.1:6060
 - waits up to 3 seconds for an ACK
 - on timeout prints "Packet lost (timeout)"
 - typing "exit" will send exit then stop the client
"""
import socket
import sys
from datetime import datetime

HOST = '127.0.0.1'
PORT = 6060
ENC = 'utf-8'
TIMEOUT_SECONDS = 3
BUFFER = 4096


def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"[UDP Server] Listening on {HOST}:{PORT}...")
        while True:
            try:
                data, addr = s.recvfrom(BUFFER)
            except KeyboardInterrupt:
                print("\n[UDP Server] Interrupted by user. Stopping.")
                break
            msg = data.decode(ENC).strip()
            print(f"[UDP Server] Received from {addr}: {msg}")
            # prepare ACK
            now = datetime.now().strftime("%H:%M:%S")
            ack = f"ACK {now}"
            try:
                s.sendto(ack.encode(ENC), addr)
            except Exception as e:
                print(f"[UDP Server] Error sending ACK: {e}")
            if msg.lower() == "exit":
                print("[UDP Server] 'exit' received. Stopping server.")
                break
        print("[UDP Server] Server stopped.")


def run_client():
    server_addr = (HOST, PORT)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        print(f"[UDP Client] Ready. Sending to {HOST}:{PORT}. Type 'exit' to stop.")
        while True:
            try:
                msg = input()
            except EOFError:
                msg = "exit"
                print()
            if not msg:
                continue
            try:
                s.sendto(msg.encode(ENC), server_addr)
            except Exception as e:
                print(f"[UDP Client] Send error: {e}")
                continue

            # wait for ACK with timeout
            s.settimeout(TIMEOUT_SECONDS)
            try:
                data, addr = s.recvfrom(BUFFER)
            except socket.timeout:
                print("Packet lost (timeout).")
            except Exception as e:
                print(f"[UDP Client] Receive error: {e}")
            else:
                print(data.decode(ENC).strip())
            finally:
                s.settimeout(None)  # remove timeout

            if msg.lower() == "exit":
                print("[UDP Client] Exiting.")
                break


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("server", "client"):
        print("Usage: python udp_enhanced.py [server|client]")
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "server":
        run_server()
    else:
        run_client()