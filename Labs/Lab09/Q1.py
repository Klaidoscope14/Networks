def get_ip_class(first_octet):
    if 1 <= first_octet <= 126:
        return 'A'
    elif 128 <= first_octet <= 191:
        return 'B'
    elif 192 <= first_octet <= 223:
        return 'C'
    elif 224 <= first_octet <= 239:
        return 'D'
    elif 240 <= first_octet <= 254:
        return 'E'
    else:
        return 'Invalid'

def is_private_ip(ip):
    first, second, *_ = map(int, ip.split('.'))

    if first == 10:
        return True

    if first == 172 and 16 <= second <= 31:
        return True

    if first == 192 and second == 168:
        return True

    return False

def classify_ip(ip):
    first_octet = int(ip.split('.')[0])

    if first_octet == 127:
        return "Loopback Address"

    ip_class = get_ip_class(first_octet)
    if ip_class == 'Invalid':
        return f"{ip} → Invalid IP"

    privacy = "Private" if is_private_ip(ip) else "Public"
    return f"{ip} → Class {ip_class}, {privacy}"

ips = ["10.0.0.1", "172.16.5.4", "192.168.1.10", "8.8.8.8", "224.0.0.1"]

for ip in ips:
    print(classify_ip(ip))