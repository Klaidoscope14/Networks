# Ping Utility Assignment

## Overview

This assignment focuses on understanding and using the `ping` utility for network diagnostics, analyzing its output, exploring its options, and developing a custom ping-like tool using Python's **Scapy** library.

---

## 1. Ping Basics

### Purpose of the Ping Utility

The `ping` command checks the connectivity between your device and another network device (e.g., a server). It sends **ICMP Echo Request** packets and waits for **ICMP Echo Reply** packets.

**Basic Syntax:**

```bash
ping [OPTIONS] destination
```

**Example 1: Test connectivity to a website**

```bash
ping google.com
```

**Example 2: Test connectivity to localhost**

```bash
ping 127.0.0.1
```

---

## 2. Ping Output Analysis

### Example Output:

```bash
PING google.com (142.250.193.206): 56 data bytes
64 bytes from 142.250.193.206: icmp_seq=0 ttl=117 time=24.8 ms
64 bytes from 142.250.193.206: icmp_seq=1 ttl=117 time=23.9 ms
64 bytes from 142.250.193.206: icmp_seq=2 ttl=117 time=25.1 ms

--- google.com ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 23.9/24.6/25.1/0.5 ms
```

### Explanation:

* **PING google.com ...** → Target domain/IP and packet size.
* **64 bytes from ...** → Packet reply received.
* **icmp\_seq** → Sequence number of ICMP request.
* **ttl** → Time-To-Live (max hops allowed before being discarded).
* **time** → Round-trip time in milliseconds.
* **Packet statistics** → Sent, received, lost packets, and total test duration.
* **rtt** → Minimum, average, maximum, and mean deviation of response times.

---

## 3. Ping Options

| Option     | Description                            | Example                  |
| ---------- | -------------------------------------- | ------------------------ |
| `-c COUNT` | Number of packets to send              | `ping -c 5 google.com`   |
| `-s SIZE`  | Packet size in bytes                   | `ping -s 128 google.com` |
| `-t TTL`   | Set Time-To-Live value                 | `ping -t 64 google.com`  |
| `-W TIME`  | Timeout in seconds to wait for a reply | `ping -W 2 google.com`   |

---

## 4. Troubleshooting with Ping

**Scenario:** Slow internet browsing.

**Steps:**

1. Test local network:

   ```bash
   ping -c 4 192.168.1.1
   ```
2. Test an external site:

   ```bash
   ping -c 4 google.com
   ```
3. If local ping works but external fails, it’s likely an ISP or DNS issue.
4. Use `-s` to test large packet sizes (for MTU issues) and `-t` to check hop limits.

---

## 5. Developing a Ping-Type Utility with Scapy

### Basic Scapy Ping Code

```python
from scapy.all import *
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

# Example usage
custom_ping("8.8.8.8", count=5, ttl=64, packet_size=64, timeout=1)
```

### Features Implemented:

* **Custom TTL**
* **Custom packet size**
* **Custom timeout**
* **Error handling** for invalid inputs
* **Output formatting** with packet loss and RTT stats

---

## Conclusion

* **Ping** is a fundamental network diagnostic tool.
* It helps identify connectivity issues, packet loss, and latency.
* By building a custom ping with Scapy, you gain deeper insight into ICMP behavior and network troubleshooting.

---

## References

* [Ping Manual (Linux man page)](https://man7.org/linux/man-pages/man8/ping.8.html)
* [Scapy Documentation](https://scapy.readthedocs.io/en/latest/)