import socket, argparse, time

parser = argparse.ArgumentParser()
parser.add_argument("receiver_ip")
parser.add_argument("receiver_port", type=int)
parser.add_argument("total_frames", type=int)
parser.add_argument("window_size", type=int)
parser.add_argument("--timeout", type=float, default=1.0)
args = parser.parse_args()

addr = (args.receiver_ip, args.receiver_port)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.5)  # short recv timeout used inside loop

base = 0
nextseq = 0
N = args.window_size
total = args.total_frames
seq_space = N  # use seq numbers 0..N-1 as requested

frames = [f"DATA[{i}]" for i in range(total)]
start_time = time.time()

timer_start = None
retransmissions = 0
total_sent_packets = 0

while base < total:
    # send new frames while window not full
    while nextseq < base + N and nextseq < total:
        seq = nextseq % seq_space
        pkt = f"FRAME|{nextseq}|{seq}|{frames[nextseq]}".encode()
        sock.sendto(pkt, addr)
        total_sent_packets += 1
        print(f"[Sender] Sent frame idx={nextseq} seq={seq}")
        if timer_start is None:
            timer_start = time.time()
        nextseq += 1

    # wait for ACK or timeout
    try:
        raw, _ = sock.recvfrom(1024)
        msg = raw.decode().strip()
        if msg.startswith("ACK|"):
            next_expected = int(msg.split("|")[1])
            print(f"[Sender] Received cumulative ACK next_expected={next_expected}")
            if next_expected > base:
                base = next_expected
                # restart timer if there are outstanding frames
                if base != nextseq:
                    timer_start = time.time()
                else:
                    timer_start = None
    except socket.timeout:
        # check timer expiry
        if timer_start is not None and (time.time() - timer_start) >= args.timeout:
            print(f"[Sender] TIMEOUT. Retransmitting frames from {base} to {nextseq-1}")
            for i in range(base, nextseq):
                seq = i % seq_space
                pkt = f"FRAME|{i}|{seq}|{frames[i]}".encode()
                sock.sendto(pkt, addr)
                total_sent_packets += 1
                retransmissions += 1
            timer_start = time.time()
        # else, loop back to attempt receiving ACK again

end_time = time.time()
print("----- SUMMARY -----")
print(f"Total frames = {total}")
print(f"Window size = {N}")
print(f"Total packets sent = {total_sent_packets}")
print(f"Retransmissions (packets) = {retransmissions}")
print(f"Total time = {end_time - start_time:.3f} s")