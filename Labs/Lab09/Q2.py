def ip_to_int(ip: str) -> int:
    """Converts dotted-decimal IPv4 string into 32-bit integer."""
    parts = list(map(int, ip.split('.')))
    result = 0
    for p in parts:
        result = (result << 8) | p
    return result


def parse_cidr(cidr: str):
    """Parses CIDR (e.g., 192.168.1.0/24) into (network_int, mask_length)."""
    ip, prefix_len = cidr.split('/')
    prefix_len = int(prefix_len)
    ip_int = ip_to_int(ip)
    mask = (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF
    network = ip_int & mask
    return network, mask, prefix_len


def find_best_route(dest_ip: str, routes: list):
    """Finds the best matching route for a given destination IP."""
    dest_int = ip_to_int(dest_ip)
    best_match = None
    longest_prefix = -1

    for route in routes:
        network, mask, prefix_len = parse_cidr(route["network"])
        if (dest_int & mask) == network:
            if prefix_len > longest_prefix:
                longest_prefix = prefix_len
                best_match = route["interface"]

    return best_match if best_match else "No route"


def main():
    routes = [
        {"network": "192.168.0.0/16", "interface": "eth0"},
        {"network": "192.168.2.0/24", "interface": "eth1"},
        {"network": "10.0.0.0/8", "interface": "eth2"},
        {"network": "0.0.0.0/0", "interface": "eth3"}
    ]

    dest_ips = ["192.168.1.10", "192.168.2.5", "10.1.2.3", "8.8.8.8"]

    for ip in dest_ips:
        interface = find_best_route(ip, routes)
        print(f"{ip} -> {interface}")


if __name__ == "__main__":
    main()