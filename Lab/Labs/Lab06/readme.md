# CN Lab Assignment

## Overview

This assignment demonstrates two **Automatic Repeat reQuest (ARQ)** protocols used in Computer Networks to ensure reliable data transmission over an unreliable channel:

1. **Stop-and-Wait ARQ**
2. **Go-Back-N ARQ**

Both protocols were implemented in Python using UDP sockets. Random packet loss and ACK loss were simulated to observe how retransmissions and total transmission time are affected under unreliable conditions.

---

## 1. Stop-and-Wait ARQ

* The sender transmits one frame at a time and waits for an acknowledgment (ACK).
* Frames are numbered using 1-bit sequence numbers (`0` or `1`).
* If the ACK is not received within a timeout period, the frame is retransmitted.
* Receiver simulates:

  * Frame drops (packet loss)
  * ACK drops
* At the end, total transmission time and retransmissions are displayed.

**Files:**

* `sender_sw.py`
* `receiver_sw.py`

**Example Run:**

```bash
# Receiver
python receiver_sw.py --port 12000 --num 20 --drop_prob 0.2 --ack_drop_prob 0.1

# Sender
python sender_sw.py 127.0.0.1 12000 20 --timeout 1.0
```

---

## 2. Go-Back-N ARQ

* The sender maintains a **sliding window** of size `N`.
* It can send multiple frames before waiting for ACKs.
* Receiver only accepts **in-order frames** and discards out-of-order ones.
* Cumulative ACKs are sent indicating the **next expected frame number**.
* On timeout, the sender retransmits all frames in the window.
* Random loss of frames and ACKs is simulated.

**Files:**

* `sender_gbn.py`
* `receiver_gbn.py`

**Example Run:**

```bash
# Receiver
python receiver_gbn.py --port 13000 --num 50 --drop_prob 0.2 --ack_drop_prob 0.1

# Sender
python sender_gbn.py 127.0.0.1 13000 50 4 --timeout 1.0
```

---

## Key Observations

* With **no loss** (`drop_prob=0.0`), all frames are delivered with **zero retransmissions**.
* With higher packet/ACK drop probabilities, **retransmissions increase**, and total transmission time grows.
* **Stop-and-Wait** is simple but inefficient for high-latency or lossy networks.
* **Go-Back-N** improves throughput using pipelining but can suffer from multiple retransmissions when losses occur.

---

## Deliverables

* Source code files (`sender_sw.py`, `receiver_sw.py`, `sender_gbn.py`, `receiver_gbn.py`).
* This README file.
* Sample run outputs/screenshots for both protocols.