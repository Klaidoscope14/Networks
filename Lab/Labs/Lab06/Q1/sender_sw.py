import socket, argparse, time

parser = argparse.ArgumentParser()
parser.add_argument("receiver_ip")
parser.add_argument("receiver_port", type=int)
parser.add_argument("num_frames", type=int)
parser.add_argument("--timeout", type=float, default=1.0, help="seconds")
args = parser.parse_args()

addr = (args.receiver_ip, args.receiver_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(args.timeout)

total_sent = 0
retransmissions = 0

start_time = time.time()

for frame_no in range(args.num_frames):
    seq = frame_no % 2  # 0 or 1
    packet = f"FRAME|{frame_no}|{seq}".encode()
    attempt = 0

    while True:
        attempt += 1
        total_sent += 1
        sock.sendto(packet, addr)
        print(f"[Sender] Sent frame {frame_no} (seq={seq}), attempt {attempt}")
        try:
            raw, _ = sock.recvfrom(1024)
            resp = raw.decode().strip()
            if resp.startswith("ACK|"):
                ack_seq = int(resp.split("|")[1])
                print(f"[Sender] Received ACK seq={ack_seq}")
                if ack_seq == seq:
                    # success, go to next frame
                    if attempt > 1:
                        retransmissions += (attempt - 1)
                    break
                else:
                    print("[Sender] Wrong ACK seq — ignoring")
            else:
                print("[Sender] Unknown response:", resp)
        except socket.timeout:
            print(f"[Sender] Timeout waiting for ACK for frame {frame_no}; will retransmit")
            # loop to retransmit

end_time = time.time()
print("----- SUMMARY -----")
print(f"Total frames requested: {args.num_frames}")
print(f"Total UDP packets SENT: {total_sent}")
print(f"Retransmissions (count): {retransmissions}")
print(f"Total time: {end_time - start_time:.3f} seconds")