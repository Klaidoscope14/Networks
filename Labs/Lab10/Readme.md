# Distance Vector Routing (Multithreaded)

## 📌 Overview

This project implements the **Distance Vector Routing Algorithm** using **multithreading**, where each router runs as an independent thread and exchanges routing tables with its neighbors until convergence.

## 🚀 Features

* One thread per router
* Message passing via synchronized inbox queues
* Bellman–Ford updates
* Automatic convergence detection
* Marks updated entries using `*` during each iteration
* Detects disconnected topologies
* Clean formatted C++17 code

## 📂 Files Included

* **dv_routing.cpp** – Main implementation
* **topology.txt** – Input graph file (must be provided)
* **README.md** – This documentation

## 🛠 Requirements

* C++17 or above
* POSIX threads support (Linux/macOS)
* A topology input file

## 📄 Input Format (topology.txt)

```
N
<router1> <router2> ... <routerN>
A B cost
A C cost
...
END
```

### Example:

```
3
A B C
A B 5
A C 2
END
```

## 🧵 How the Program Works

1. Reads topology from `topology.txt`
2. Creates **N router threads**
3. Initializes routing tables
4. Each iteration:

   * Routers send their distance vectors to neighbors
   * Receive vectors from neighbors
   * Apply Bellman–Ford updates
   * Update table entries and mark changes
5. Stops when no router has any update in an iteration

## ▶️ How to Compile

```
g++ -std=c++17 -pthread dv_routing.cpp -o dv_routing
```

## ▶️ How to Run

Place your `topology.txt` in the same directory, then run:

```
./dv_routing
```

## 📊 Output Example

The program prints routing tables for each iteration:

```
==================== Iteration 1 ====================
Router A
Dest   Dist   Next
A      0      A
B      5      B *
C      2      C *
```

## 📍 Notes

* If topology is **disconnected**, program stops immediately.
* Add delays required as per the assignment (already implemented).
* Routers exits after convergence.

---

Feel free to extend this for simulations, animation-visualization, or GUI-based routing table displays.