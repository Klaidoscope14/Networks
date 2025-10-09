import socket, argparse, random, time

parser = argparse.ArgumentParser()
parser.add_argument("--host", default="0.0.0.0")
parser.add_argument("--port", type=int, required=True)
parser.add_argument("--num", type=int, default=50, help="total frames expected")
parser.add_argument("--drop_prob", type=float, default=0.2)
parser.add_argument("--ack_drop_prob", type=float, default=0.1)
args = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((args.host, args.port))
print(f"[GBN Receiver] Listening on {args.host}:{args.port}")

expected = 0
start = time.time()
while expected < args.num:
    data, addr = sock.recvfrom(4096)
    msg = data.decode().strip()
    # FRAME|<index>|<seq>|<payload>
    parts = msg.split("|")
    if len(parts) < 4 or parts[0] != "FRAME":
        print("[Receiver] bad pkt:", msg); continue

    index = int(parts[1])
    seq = int(parts[2])

    if random.random() < args.drop_prob:
        print(f"[Receiver] Simulated DROP frame {index} (seq={seq})")
        continue

    if index == expected:
        print(f"[Receiver] Received in-order frame {index} (seq={seq})")
        expected += 1
    else:
        print(f"[Receiver] Out-of-order/dup frame {index} (expected {expected}) — discarded")

    # send cumulative ACK = next expected absolute index
    ack = f"ACK|{expected}"
    if random.random() < args.ack_drop_prob:
        print(f"[Receiver] Simulated DROP of ACK(next_expected={expected})")
        continue
    sock.sendto(ack.encode(), addr)
    print(f"[Receiver] Sent cumulative ACK next_expected={expected}")

end = time.time()
print(f"[Receiver] Done. Received up to {expected-1}. Time: {end-start:.3f}s")