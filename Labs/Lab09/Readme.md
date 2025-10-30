# Lab 09 — IP Utilities (README)

This folder contains three small Python utilities for IPv4 address handling and routing examples.

Files:
- [Q1.py](Q1.py)  
  - Functions: [`Q1.get_ip_class`](Q1.py), [`Q1.is_private_ip`](Q1.py), [`Q1.classify_ip`](Q1.py)  
  - Purpose: Classify single IPv4 addresses by class (A–E), detect private addresses and identify loopback (127.*). The script prints classification for a small example list. Use `classify_ip(ip)` to get a human-readable string like `192.168.1.10 → Class C, Private`.

- [Q2.py](Q2.py)  
  - Functions: [`Q2.ip_to_int`](Q2.py), [`Q2.parse_cidr`](Q2.py), [`Q2.find_best_route`](Q2.py)  
  - Purpose: Helper utilities for route lookup. `ip_to_int` converts dotted IP to 32-bit integer. `parse_cidr` turns a CIDR string into (network_int, mask, prefix_len). `find_best_route(dest_ip, routes)` implements longest-prefix match over a route table and returns the outgoing interface (or `"No route"`). The module includes a small `main()` demonstrating route selection.

- [Q3.py](Q3.py)  
  - Functions: [`Q3.ip_to_int`](Q3.py), [`Q3.int_to_ip`](Q3.py), [`Q3.mask_from_prefix`](Q3.py), [`Q3.cidr_info`](Q3.py), `main()`  
  - Purpose: CIDR calculator. Converts IPs to integers and back, computes network and broadcast addresses, number of hosts and usable host range for a given CIDR. Run as a script to prompt for a CIDR (or pass it as argv) and print network/broadcast/usable range and host counts.

Quick usage examples:
- Classify an IP:
  - from [Q1.py](Q1.py) call `classify_ip("192.168.1.10")`.
- Find route:
  - from [Q2.py](Q2.py) call `find_best_route("192.168.2.5", routes)`.
- CIDR info:
  - run [Q3.py](Q3.py) or call `cidr_info("192.168.10.0/28")` to get network/broadcast/usable hosts.

Notes:
- All modules include small demo `main()` or example lists for quick testing.
- Input parsing is minimal; feed valid IPv4 and CIDR strings to avoid exceptions.