from scapy.all import *
from scapy.layers.inet import ICMP, IP
import time
import socket

def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def is_valid_ttl(ttl):
    return isinstance(ttl, int) and 1 <= ttl <= 255

def is_valid_packet_size(size):
    return isinstance(size, int) and 28 <= size <= 1500  

def is_valid_timeout(timeout):
    return isinstance(timeout, (int, float)) and timeout > 0

def is_valid_src_ip(src_ip):
    try:
        local_ips = [i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None)]
        return src_ip in local_ips
    except Exception:
        return False

def scapy_traceroute(dest, max_hops=30, pings_per_hop=3, timeout=2, packet_size=56, src_ip=None, delay=0, output_file=None):
    if not is_valid_ip(dest):
        print("Error: Invalid destination IP address.")
        return
    if not is_valid_ttl(max_hops):
        print("Error: Invalid max TTL value. Must be between 1 and 255.")
        return
    if not is_valid_packet_size(packet_size):
        print("Error: Invalid packet size. Must be between 28 and 1500 bytes.")
        return
    if not is_valid_timeout(timeout):
        print("Error: Invalid timeout value. Must be positive.")
        return
    if src_ip and not is_valid_src_ip(src_ip):
        print("Error: Source IP not configured on this system.")
        return

    output_lines = []
    header = f"{'Hop':<5}{'IP Address':<20}{'RTT (ms)':<30}{'Loss (%)':<10}"
    print(header)
    output_lines.append(header)

    for ttl in range(1, max_hops + 1):
        hop_ips = []
        rtts = []
        lost = 0
        for _ in range(pings_per_hop):
            payload = b'X' * (packet_size - 28)  # 28 bytes for IP+ICMP header
            pkt = IP(dst=dest, ttl=ttl)
            if src_ip:
                pkt.src = src_ip
            pkt /= ICMP() / Raw(load=payload)
            start = time.time()
            try:
                reply = sr1(pkt, verbose=0, timeout=timeout)
            except Exception as e:
                reply = None
            end = time.time()
            if reply:
                hop_ips.append(reply.src)
                rtts.append(round((end - start) * 1000, 2))
                if reply.type == 0:  
                    reached = True
                else:
                    reached = False
            else:
                lost += 1
                hop_ips.append("*")
                rtts.append(None)
            time.sleep(delay)

        ip_set = set([ip for ip in hop_ips if ip != "*"])
        ip_str = ", ".join(ip_set) if ip_set else "*"
        avg_rtt = f"{sum([rtt for rtt in rtts if rtt is not None])/max(1, len([rtt for rtt in rtts if rtt is not None])):.2f}" if any(rtts) else "-"
        loss_pct = f"{(lost/pings_per_hop)*100:.0f}"
        line = f"{ttl:<5}{ip_str:<20}{avg_rtt:<30}{loss_pct:<10}"
        print(line)
        output_lines.append(line)
        if any([ip != "*" and reply and reply.type == 0 for ip, reply in zip(hop_ips, [sr1(IP(dst=dest, ttl=ttl)/ICMP(), verbose=0, timeout=timeout) if ip != "*" else None for ip in hop_ips])]):
            print("Destination reached.")
            break

    if output_file:
        try:
            with open(output_file, "w") as f:
                for l in output_lines:
                    f.write(l + "\n")
            print(f"Output saved to {output_file}")
        except Exception as e:
            print(f"Error saving output to file: {e}")

if __name__ == "__main__":
    scapy_traceroute(
        dest="8.8.8.8",
        max_hops=10,
        pings_per_hop=2,
        timeout=2,
        packet_size=64,
        src_ip=None,
        delay=0.5,
        output_file=None
    )