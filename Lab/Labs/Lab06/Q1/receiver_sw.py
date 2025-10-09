import socket, argparse, random, time

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="0.0.0.0")
parser.add_argument("--port", type=int, required=True)
parser.add_argument("--num", type=int, default=20, help="total frames expected")
parser.add_argument("--drop_prob", type=float, default=0.2, help="probability to DROP an incoming frame")
parser.add_argument("--ack_drop_prob", type=float, default=0.1, help="probability to DROP an ACK")
args = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((args.host, args.port))
print(f"[Receiver] Listening on {args.host}:{args.port}")

expected_frame = 0
received_count = 0
start = time.time()

while received_count < args.num:
    data, addr = sock.recvfrom(2048)
    msg = data.decode().strip()
    parts = msg.split("|")
    if len(parts) < 3 or parts[0] != "FRAME":
        print("[Receiver] Bad packet:", msg)
        continue

    frame_no = int(parts[1])
    seq = int(parts[2])

    # simulate drop
    if random.random() < args.drop_prob:
        print(f"[Receiver] Simulated DROP of frame {frame_no} (seq={seq})")
        continue

    if frame_no == expected_frame:
        print(f"[Receiver] Received in-order frame {frame_no} (seq={seq})")
        expected_frame += 1
        received_count += 1
    else:
        print(f"[Receiver] Received out-of-order/duplicate frame {frame_no} (expected {expected_frame}) — discarded")

    # prepare ACK: send ACK with seq (for SW ack is the seq of last received frame)
    ack_msg = f"ACK|{seq}"
    if random.random() < args.ack_drop_prob:
        print(f"[Receiver] Simulated DROP of ACK for seq={seq}")
        continue

    sock.sendto(ack_msg.encode(), addr)
    print(f"[Receiver] Sent ACK for seq={seq}")

end = time.time()
print(f"[Receiver] Done. Received {received_count}/{args.num} frames. Elapsed {end-start:.3f}s")