from scapy.all import *
from scapy.layers.inet import ICMP, IP
import time
import socket

def custom_ping(dest_ip, count=4, ttl=64, packet_size=56, timeout=2):
    try:
        if count <= 0:
            raise ValueError("Invalid count value. Count must be a positive integer.")
        if ttl <= 0 or ttl > 255:
            raise ValueError("Invalid TTL value. TTL must be between 1 and 255.")

        try:
            socket.gethostbyname(dest_ip)
        except socket.gaierror:
            raise ValueError(f"Invalid destination IP or hostname: {dest_ip}")

        rtt_list = []
        for seq in range(count):
            try:
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

            except socket.timeout:
                print(f"Timeout occurred for icmp_seq {seq}")
            except Exception as pkt_err:
                print(f"Error sending packet {seq}: {pkt_err}")

        if rtt_list:
            print("\n--- Ping statistics ---")
            print(f"{count} packets transmitted, {len(rtt_list)} received, {((count - len(rtt_list))/count)*100:.1f}% packet loss")
            print(f"rtt min/avg/max = {min(rtt_list):.2f}/{sum(rtt_list)/len(rtt_list):.2f}/{max(rtt_list):.2f} ms")

    except ValueError as ve:
        print(f"[Value Error] {ve}")
    except Exception as e:
        print(f"[Unexpected Error] {e}")

custom_ping("8.8.8.8", count=5, ttl=64, packet_size=64, timeout=1)