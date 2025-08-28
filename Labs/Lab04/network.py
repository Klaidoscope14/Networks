from scapy.all import *
from scapy.layers.inet import ICMP, IP
import time

def scapy_traceroute(dest, max_hops=30, pings_per_hop=3, timeout=2):
    print(f"Tracing route to {dest} with max {max_hops} hops...\n")
    for ttl in range(1, max_hops + 1):
        print(f"TTL={ttl} ", end="")
        success = False
        for _ in range(pings_per_hop):
            pkt = IP(dst=dest, ttl=ttl) / ICMP()
            start = time.time()
            reply = sr1(pkt, verbose=0, timeout=timeout)
            end = time.time()
            if reply:
                rtt = round((end - start) * 1000, 2)
                print(f"{reply.src} RTT={rtt}ms", end="  ")
                success = True
                if reply.type == 0:  # Destination reached
                    print("\nDestination reached.")
                    return
            else:
                print("*", end="  ")
        if not success:
            print("Request timed out")
        else:
            print()

if __name__ == "__main__":
    scapy_traceroute("8.8.8.8", max_hops=10, pings_per_hop=2)