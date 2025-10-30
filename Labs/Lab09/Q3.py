from typing import Tuple, List, Dict

def ip_to_int(ip: str) -> int:
    parts = ip.split('.')
    if len(parts) != 4:
        raise ValueError("Invalid IPv4 address format")
    val = 0
    for p in parts:
        try:
            n = int(p)
        except ValueError:
            raise ValueError("Invalid IPv4 octet")
        if n < 0 or n > 255:
            raise ValueError("IPv4 octet out of range 0-255")
        val = (val << 8) | n
    return val

def _mask_from_prefix(prefix: int) -> int:
    if prefix < 0 or prefix > 32:
        raise ValueError("Prefix must be 0..32")
    if prefix == 0:
        return 0
    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF

def cidr_to_range(cidr: str) -> Tuple[int, int, int]:
    if '/' not in cidr:
        raise ValueError("CIDR must contain '/'")
    ip_part, prefix_part = cidr.split('/', 1)
    prefix = int(prefix_part)
    ip_int = ip_to_int(ip_part)
    mask = _mask_from_prefix(prefix)
    network = ip_int & mask
    broadcast = network | (~mask & 0xFFFFFFFF)
    return (network, broadcast, prefix)

def route_lookup(routes: List[Dict[str, str]], dest_ips: List[str]) -> Dict[str, str]:
    processed = []
    for r in routes:
        cidr = r.get("network")
        iface = r.get("interface")
        if cidr is None or iface is None:
            continue
        net, bcast, prefix = cidr_to_range(cidr)
        processed.append((net, bcast, prefix, iface))

    result: Dict[str, str] = {}
    for dest in dest_ips:
        ip_int = ip_to_int(dest)
        best_prefix = -1
        best_iface = None
        for net, bcast, prefix, iface in processed:
            if net <= ip_int <= bcast:
                if prefix > best_prefix:
                    best_prefix = prefix
                    best_iface = iface
        result[dest] = best_iface
    return result


if __name__ == "__main__":
    routes = [
        {"network": "192.168.0.0/16", "interface": "eth0"},
        {"network": "192.168.1.0/24", "interface": "eth1"},
        {"network": "10.0.0.0/8", "interface": "eth2"},
        {"network": "0.0.0.0/0", "interface": "eth3"},
    ]

    dest_ips = ["192.168.1.10", "192.168.2.5", "10.1.2.3", "8.8.8.8"]

    mapping = route_lookup(routes, dest_ips)
    for ip in dest_ips:
        iface = mapping[ip] or "No route"
        print(f"{ip} -> {iface}")