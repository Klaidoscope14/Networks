from scapy.all import *
from scapy.layers.inet import ICMP, IP
import time

def custom_ping(dest_ip, count=4, ttl=64, packet_size=56, timeout=2):
    try:
        rtt_list = []
        for seq in range(count):
            packet = IP(dst=dest_ip, ttl=ttl)/ICMP()/Raw(load="X"*packet_size)
            start = time.time()
            reply = sr1(packet, timeout=timeout, verbose=False)
            end = time.time()
            if reply:
                rtt = (end - start) * 1000
                rtt_list.append(rtt)
                print(f"{len(reply)} bytes from {dest_ip}: icmp_seq={seq} ttl={reply.ttl} time={rtt:.2f} ms")
            else:
                print(f"Request timeout for icmp_seq {seq}")

        if rtt_list:
            print("\n--- Ping statistics ---")
            print(f"{count} packets transmitted, {len(rtt_list)} received, {((count - len(rtt_list))/count)*100:.1f}% packet loss")
            print(f"rtt min/avg/max = {min(rtt_list):.2f}/{sum(rtt_list)/len(rtt_list):.2f}/{max(rtt_list):.2f} ms")
    except Exception as e:
        print(f"Error: {e}")

custom_ping("8.8.8.8", count=5, ttl=64, packet_size=64, timeout=1)
