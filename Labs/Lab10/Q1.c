// dv_multithread.c
// Distance Vector routing with one thread per router.
// Reads topology.txt from current directory.

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <limits.h>
#include <unistd.h>

#define INF 1000000000
#define MAX_NAME 32
#define CHECK_INTERVAL_USEC 200000  // 0.2s

typedef struct {
    int sender;       // index of sender
    int *vector;      // distance vector (length n)
} Message;

typedef struct MsgNode {
    Message *msg;
    struct MsgNode *next;
} MsgNode;

typedef struct {
    MsgNode *head, *tail;
    pthread_mutex_t m;
    pthread_cond_t c;
    int size;
} Queue;

typedef struct {
    int id;               // router index
    char name[MAX_NAME];
    int n;
    int *dist;            // own distance vector
    int *next_hop;        // next hop for each dest
    int *neighbors;       // neighbor cost (INF if not neighbor)
} Router;

int nrouters = 0;
char **names = NULL;
int **adj = NULL;          // adjacency cost matrix
Router *routers = NULL;
Queue *queues = NULL;
volatile int global_updates = 0; // incremented when a router makes an update
pthread_mutex_t global_updates_m = PTHREAD_MUTEX_INITIALIZER;
int max_rounds = 2000;

///////////////////// Queue helpers /////////////////////
void queue_init(Queue *q) {
    q->head = q->tail = NULL;
    q->size = 0;
    pthread_mutex_init(&q->m, NULL);
    pthread_cond_init(&q->c, NULL);
}
void queue_push(Queue *q, Message *m) {
    MsgNode *node = malloc(sizeof(MsgNode));
    node->msg = m;
    node->next = NULL;
    pthread_mutex_lock(&q->m);
    if (q->tail) q->tail->next = node; else q->head = node;
    q->tail = node;
    q->size++;
    pthread_cond_signal(&q->c);
    pthread_mutex_unlock(&q->m);
}
Message* queue_pop_nonblock(Queue *q) {
    pthread_mutex_lock(&q->m);
    MsgNode *node = q->head;
    if (!node) {
        pthread_mutex_unlock(&q->m);
        return NULL;
    }
    q->head = node->next;
    if (!q->head) q->tail = NULL;
    q->size--;
    pthread_mutex_unlock(&q->m);
    Message *m = node->msg;
    free(node);
    return m;
}
int queue_empty(Queue *q) {
    pthread_mutex_lock(&q->m);
    int e = (q->size == 0);
    pthread_mutex_unlock(&q->m);
    return e;
}
void queue_destroy(Queue *q) {
    pthread_mutex_lock(&q->m);
    MsgNode *cur = q->head;
    while (cur) {
        MsgNode *tmp = cur;
        cur = cur->next;
        // free message contents
        if (tmp->msg) {
            if (tmp->msg->vector) free(tmp->msg->vector);
            free(tmp->msg);
        }
        free(tmp);
    }
    q->head = q->tail = NULL;
    q->size = 0;
    pthread_mutex_unlock(&q->m);
    pthread_mutex_destroy(&q->m);
    pthread_cond_destroy(&q->c);
}

/////////////////////// Messaging ////////////////////////
void send_vector_to(int from_idx, int to_idx) {
    // prepare message: copy sender's dist
    Message *m = malloc(sizeof(Message));
    m->sender = from_idx;
    m->vector = malloc(sizeof(int) * nrouters);
    memcpy(m->vector, routers[from_idx].dist, sizeof(int) * nrouters);
    queue_push(&queues[to_idx], m);
}

void broadcast_if_changed(int from_idx, int *changed_flags) {
    // send updated vector to all neighbors if changed_flags[from_idx] is true
    for (int j = 0; j < nrouters; ++j) {
        if (adj[from_idx][j] < INF && j != from_idx) {
            send_vector_to(from_idx, j);
        }
    }
}

/////////////////////// Router thread ////////////////////
void *router_thread(void *arg) {
    Router *r = (Router *)arg;
    int id = r->id;
    int n = r->n;

    // initially send own vector to neighbors
    for (int j = 0; j < n; ++j) {
        if (adj[id][j] < INF && j != id) {
            send_vector_to(id, j);
        }
    }

    int local_rounds = 0;
    while (1) {
        // Process all messages currently in queue (non-blocking)
        int any_msg = 0;
        Message *m;
        while ((m = queue_pop_nonblock(&queues[id])) != NULL) {
            any_msg = 1;
            // integrate message (distance-vector update)
            int sender = m->sender;
            for (int d = 0; d < n; ++d) {
                long via_cost = (long)adj[id][sender] + (long)m->vector[d];
                if (m->vector[d] >= INF) via_cost = INF;
                if (via_cost < 0) via_cost = INF; // overflow safety

                if (via_cost < r->dist[d]) {
                    r->dist[d] = (int)via_cost;
                    r->next_hop[d] = (d == sender) ? sender : r->next_hop[sender];
                    // mark global update
                    pthread_mutex_lock(&global_updates_m);
                    global_updates++;
                    pthread_mutex_unlock(&global_updates_m);
                    // send updated vector to neighbors (flood)
                    for (int nb = 0; nb < n; ++nb) {
                        if (adj[id][nb] < INF && nb != id) {
                            send_vector_to(id, nb);
                        }
                    }
                }
            }
            // free message
            free(m->vector);
            free(m);
        }

        // small sleep to avoid busy spin; allow other threads to run
        usleep(1000);

        // termination condition check done by main thread (it will cancel)
        local_rounds++;
        if (local_rounds > max_rounds) break;
    }
    return NULL;
}

/////////////////////// Utilities ////////////////////////
int name_to_idx(const char *s) {
    for (int i = 0; i < nrouters; ++i) if (strcmp(names[i], s) == 0) return i;
    return -1;
}

void print_routing_tables() {
    printf("\nFinal routing tables:\n");
    for (int i = 0; i < nrouters; ++i) {
        Router *r = &routers[i];
        printf("Router %s:\n", r->name);
        printf(" Dest\tCost\tNext\n");
        for (int d = 0; d < nrouters; ++d) {
            if (r->dist[d] >= INF) {
                printf(" %s\tINF\t-\n", names[d]);
            } else {
                printf(" %s\t%d\t%s\n", names[d], r->dist[d], (r->next_hop[d] >=0 ? names[r->next_hop[d]] : "-"));
            }
        }
        printf("\n");
    }
}

/////////////////////// Topology parsing ////////////////////////
int read_topology(const char *fname) {
    FILE *f = fopen(fname, "r");
    if (!f) {
        perror("topology.txt open");
        return -1;
    }
    if (fscanf(f, "%d", &nrouters) != 1) { fclose(f); return -1; }
    // read newline then names line (use fgets)
    char line[1024];
    fgets(line, sizeof(line), f); // consume rest of line
    if (!fgets(line, sizeof(line), f)) { fclose(f); return -1; }

    // parse names
    names = malloc(sizeof(char*) * nrouters);
    char *tok = strtok(line, " \t\r\n");
    int idx = 0;
    while (tok && idx < nrouters) {
        names[idx] = strdup(tok);
        idx++;
        tok = strtok(NULL, " \t\r\n");
    }
    if (idx != nrouters) {
        fprintf(stderr, "Error: number of names doesn't match n\n");
        fclose(f);
        return -1;
    }

    // allocate adjacency matrix
    adj = malloc(sizeof(int*) * nrouters);
    for (int i = 0; i < nrouters; ++i) {
        adj[i] = malloc(sizeof(int) * nrouters);
        for (int j = 0; j < nrouters; ++j) adj[i][j] = (i==j?0:INF);
    }

    // read edges lines
    while (fgets(line, sizeof(line), f)) {
        // ignore comments/empty lines
        char a[64], b[64];
        int cost;
        if (sscanf(line, " %63s %63s %d", a, b, &cost) == 3) {
            int ia = name_to_idx(a);
            int ib = name_to_idx(b);
            if (ia >=0 && ib >=0) {
                adj[ia][ib] = cost;
                adj[ib][ia] = cost; // undirected
            } else {
                fprintf(stderr, "Unknown name in edge: %s %s\n", a, b);
            }
        }
        // else ignore malformed line
    }

    fclose(f);
    return 0;
}

int main(int argc, char **argv) {
    const char *fname = "topology.txt";
    if (argc > 1) fname = argv[1];

    if (read_topology(fname) != 0) {
        fprintf(stderr, "Failed to read topology file '%s'\n", fname);
        return 1;
    }

    // allocate routers and queues
    routers = malloc(sizeof(Router) * nrouters);
    queues = malloc(sizeof(Queue) * nrouters);
    pthread_t *tids = malloc(sizeof(pthread_t) * nrouters);

    for (int i = 0; i < nrouters; ++i) {
        queue_init(&queues[i]);
    }

    // initialize routers
    for (int i = 0; i < nrouters; ++i) {
        routers[i].id = i;
        routers[i].n = nrouters;
        strncpy(routers[i].name, names[i], MAX_NAME-1);
        routers[i].name[MAX_NAME-1] = 0;
        routers[i].dist = malloc(sizeof(int) * nrouters);
        routers[i].next_hop = malloc(sizeof(int) * nrouters);
        routers[i].neighbors = malloc(sizeof(int) * nrouters);
        for (int j = 0; j < nrouters; ++j) {
            routers[i].neighbors[j] = adj[i][j];
            if (i == j) {
                routers[i].dist[j] = 0;
                routers[i].next_hop[j] = i;
            } else if (adj[i][j] < INF) {
                routers[i].dist[j] = adj[i][j];
                routers[i].next_hop[j] = j; // direct neighbor
            } else {
                routers[i].dist[j] = INF;
                routers[i].next_hop[j] = -1;
            }
        }
    }

    // create threads
    for (int i = 0; i < nrouters; ++i) {
        pthread_create(&tids[i], NULL, router_thread, &routers[i]);
    }

    // initial flood: each router sends its vector to neighbors (already done by router_thread at start)
    // monitor convergence: when global_updates remains zero for some interval and queues empty, stop
    int stable_cycles = 0;
    while (1) {
        usleep(CHECK_INTERVAL_USEC);
        pthread_mutex_lock(&global_updates_m);
        int updates = global_updates;
        global_updates = 0;
        pthread_mutex_unlock(&global_updates_m);

        int all_empty = 1;
        for (int i = 0; i < nrouters; ++i) {
            if (!queue_empty(&queues[i])) { all_empty = 0; break; }
        }
        if (updates == 0 && all_empty) {
            stable_cycles++;
        } else {
            stable_cycles = 0;
        }
        // require a few stable cycles to avoid racing
        if (stable_cycles >= 3) break;
    }

    // signal threads to stop by cancel (we used max_rounds safety but cancel is fine)
    // Alternative: threads will time out due to max_rounds; here we cancel them.
    for (int i = 0; i < nrouters; ++i) {
        pthread_cancel(tids[i]); // threads are mostly in usleep/loop; cancellation is okay
    }
    for (int i = 0; i < nrouters; ++i) {
        pthread_join(tids[i], NULL);
    }

    print_routing_tables();

    // cleanup
    for (int i = 0; i < nrouters; ++i) {
        queue_destroy(&queues[i]);
        free(routers[i].dist);
        free(routers[i].next_hop);
        free(routers[i].neighbors);
        free(adj[i]);
        free(names[i]);
    }
    free(routers);
    free(queues);
    free(tids);
    free(adj);
    free(names);
    pthread_mutex_destroy(&global_updates_m);

    return 0;
}