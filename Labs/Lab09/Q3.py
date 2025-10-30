import sys

def ip_to_int(ip_str: str) -> int:
    parts = ip_str.split('.')
    if len(parts) != 4:
        raise ValueError("Invalid IPv4 address")
    val = 0
    for p in parts:
        n = int(p)
        if n < 0 or n > 255:
            raise ValueError("IPv4 octet out of range")
        val = (val << 8) | n
    return val

def int_to_ip(x: int) -> str:
    return '.'.join(str((x >> (8 * i)) & 0xFF) for i in reversed(range(4)))

def mask_from_prefix(prefix: int) -> int:
    if prefix < 0 or prefix > 32:
        raise ValueError("Prefix must be between 0 and 32")
    if prefix == 0:
        return 0
    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF

def cidr_info(cidr: str) -> dict:
    if '/' not in cidr:
        raise ValueError("Input must be in CIDR format, e.g. 192.168.10.0/28")
    ip_part, prefix_part = cidr.split('/', 1)
    prefix = int(prefix_part)
    ip_int = ip_to_int(ip_part)

    mask = mask_from_prefix(prefix)
    network_int = ip_int & mask
    broadcast_int = network_int | (~mask & 0xFFFFFFFF)

    total_addresses = 1 << (32 - prefix)  # 2^(32-prefix)

    # Usable hosts: conventional approach
    if prefix == 31:
        # /31 per RFC3021 uses both addresses for point-to-point links.
        usable_hosts = 0
        usable_range = "No usable host addresses ( /31 - point-to-point )"
    elif prefix == 32:
        usable_hosts = 0
        usable_range = "No usable host addresses ( /32 - single address )"
    else:
        usable_hosts = max(total_addresses - 2, 0)
        if usable_hosts == 0:
            usable_range = "No usable host addresses"
        else:
            first_host = network_int + 1
            last_host = broadcast_int - 1
            usable_range = f"{int_to_ip(first_host)} - {int_to_ip(last_host)}"

    return {
        "Network Address": int_to_ip(network_int),
        "Broadcast Address": int_to_ip(broadcast_int),
        "Usable Host Range": usable_range,
        "Number of Hosts": usable_hosts
    }

def main():
    if len(sys.argv) >= 2:
        cidr = sys.argv[1]
    else:
        cidr = input("Enter IPv4 in CIDR notation (e.g. 192.168.10.0/28): ").strip()

    try:
        info = cidr_info(cidr)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

    print(f"Network Address: {info['Network Address']}")
    print(f"Broadcast Address: {info['Broadcast Address']}")
    print(f"Usable Host Range: {info['Usable Host Range']}")
    print(f"Number of Hosts: {info['Number of Hosts']}")

if __name__ == "__main__":
    main()