#include <bits/stdc++.h>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
using namespace std;

const int INF = 1e9;

struct Message {
    int sender;
    vector<int> dist;
};

class Router {
public:
    int id;
    string name;
    vector<int> dist;
    vector<int> nextHop;
    vector<int> linkCost;
    vector<bool> updated;
    vector<int> neighbors;
    deque<Message> inbox;

    mutex inbox_mtx, start_mtx;
    condition_variable inbox_cv, start_cv;

    bool start_flag = false;
    atomic<bool> finished{false};

    Router(int _id = 0) : id(_id) {}

    void push_message(const Message &m) {
        unique_lock<mutex> lk(inbox_mtx);
        inbox.push_back(m);
        inbox_cv.notify_one();
    }

    vector<Message> wait_and_collect_msgs(int count) {
        vector<Message> collected;
        unique_lock<mutex> lk(inbox_mtx);
        inbox_cv.wait(lk, [&](){ return (int)inbox.size() >= count; });
        for (int i = 0; i < count; ++i) {
            collected.push_back(inbox.front());
            inbox.pop_front();
        }
        return collected;
    }
};

vector<Router> routers;
vector<thread> threads_global;
vector<vector<int>> adjMatrix;

int N = 0;
mutex main_mtx;
condition_variable main_cv;
atomic<int> routers_done{0};
atomic<int> global_iteration{0};

void display_tables(int iter) {
    cout << "==================== Iteration " << iter << " ====================\n";
    for (int i = 0; i < N; ++i) {
        Router &r = routers[i];
        cout << "Router " << r.name << " (id=" << i << ")\n";
        cout << "Dest\tDist\tNext\n";
        for (int d = 0; d < N; ++d) {
            cout << routers[d].name << "\t";
            if (r.dist[d] >= INF) cout << "INF\t";
            else cout << r.dist[d] << "\t";
            if (r.nextHop[d] == -1) cout << "-";
            else cout << routers[r.nextHop[d]].name;
            if (r.updated[d]) cout << " *";
            cout << "\n";
        }
        cout << "-------------------------------------\n";
    }
}

bool is_connected(const vector<vector<int>> &mat) {
    int n = mat.size();
    vector<char> vis(n, 0);
    queue<int> q;

    q.push(0);
    vis[0] = 1;

    while (!q.empty()) {
        int u = q.front(); q.pop();
        for (int v = 0; v < n; ++v) {
            if (!vis[v] && mat[u][v] < INF) {
                vis[v] = 1;
                q.push(v);
            }
        }
    }

    for (int i = 0; i < n; ++i)
        if (!vis[i]) return false;
    return true;
}

void router_thread_func(int idx) {
    Router &me = routers[idx];

    while (true) {
        {
            unique_lock<mutex> lk(me.start_mtx);
            me.start_cv.wait(lk, [&](){ return me.start_flag == true; });
            me.start_flag = false;
        }

        if (me.finished.load()) return;

        Message m;
        m.sender = idx;
        m.dist = me.dist;

        for (int nb : me.neighbors) routers[nb].push_message(m);

        int need = me.neighbors.size();
        vector<Message> recvd = (need > 0) ? me.wait_and_collect_msgs(need) : vector<Message>{};

        vector<int> newDist = me.dist;
        vector<int> newNext = me.nextHop;
        vector<bool> updatedFlags(N, false);

        for (auto &msg : recvd) {
            int neighbor = msg.sender;
            int costToNeighbor = me.linkCost[neighbor];
            for (int dest = 0; dest < N; ++dest) {
                if (msg.dist[dest] >= INF) continue;
                long long candidate = (long long)costToNeighbor + msg.dist[dest];
                if (candidate < newDist[dest]) {
                    newDist[dest] = (int)candidate;
                    newNext[dest] = neighbor;
                    updatedFlags[dest] = true;
                }
            }
        }

        newDist[idx] = 0;
        newNext[idx] = idx;

        me.dist = newDist;
        me.nextHop = newNext;
        me.updated = updatedFlags;

        routers_done.fetch_add(1);
        main_cv.notify_one();
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    ifstream fin("topology.txt");
    if (!fin) {
        cerr << "Error: topology.txt not found.\n";
        return 1;
    }

    vector<string> file_words;
    string line;

    while (getline(fin, line)) {
        if (line.find_first_not_of(" \t\r\n") == string::npos) continue;
        stringstream ss(line);
        string token;
        while (ss >> token) file_words.push_back(token);
    }
    fin.close();

    if (file_words.size() < 3) {
        cerr << "Invalid topology.txt format.\n";
        return 1;
    }

    int pos = 0;
    N = stoi(file_words[pos++]);

    vector<string> names;
    for (int i = 0; i < N; ++i) names.push_back(file_words[pos++]);

    vector<tuple<string,string,int>> edges;
    while (pos < file_words.size()) {
        string a = file_words[pos++];
        if (a == "END") break;
        string b = file_words[pos++];
        int cost = stoi(file_words[pos++]);
        edges.emplace_back(a, b, cost);
    }

    unordered_map<string,int> idxOf;
    for (int i = 0; i < N; ++i) idxOf[names[i]] = i;

    routers.resize(N);
    adjMatrix.assign(N, vector<int>(N, INF));

    for (int i = 0; i < N; ++i) {
        routers[i] = Router(i);
        routers[i].name = names[i];
        for (int j = 0; j < N; ++j) adjMatrix[i][j] = (i == j ? 0 : INF);
    }

    for (auto &t : edges) {
        string a,b; int c;
        tie(a,b,c) = t;
        int u = idxOf[a], v = idxOf[b];
        adjMatrix[u][v] = c;
        adjMatrix[v][u] = c;
    }

    if (!is_connected(adjMatrix)) {
        cout << "Input topology is disconnected.\n";
        return 0;
    }

    for (int i = 0; i < N; ++i) {
        Router &r = routers[i];
        r.dist.assign(N, INF);
        r.nextHop.assign(N, -1);
        r.linkCost.assign(N, INF);
        r.updated.assign(N, false);

        for (int j = 0; j < N; ++j) {
            r.linkCost[j] = adjMatrix[i][j];
            if (adjMatrix[i][j] < INF && i != j) r.neighbors.push_back(j);

            if (adjMatrix[i][j] < INF) {
                r.dist[j] = adjMatrix[i][j];
                if (i == j) r.nextHop[j] = i;
                else if (i != j) r.nextHop[j] = j;
            }
        }
    }

    display_tables(0);

    threads_global.resize(N);
    for (int i = 0; i < N; ++i)
        threads_global[i] = thread(router_thread_func, i);

    this_thread::sleep_for(chrono::seconds(3));

    bool converged = false;
    int iteration = 0;

    while (!converged) {
        iteration++;
        routers_done.store(0);
        global_iteration.store(iteration);

        for (int i = 0; i < N; ++i) {
            unique_lock<mutex> lk(routers[i].start_mtx);
            routers[i].start_flag = true;
            routers[i].start_cv.notify_one();
        }

        unique_lock<mutex> lk(main_mtx);
        main_cv.wait(lk, [&](){ return routers_done.load() == N; });

        display_tables(iteration);

        bool any_update = false;
        for (int i = 0; i < N; ++i)
            for (int d = 0; d < N; ++d)
                if (routers[i].updated[d]) any_update = true;

        if (!any_update) {
            cout << "No updates in iteration " << iteration << ". Converged.\n";
            converged = true;

            for (int i = 0; i < N; ++i) {
                routers[i].finished.store(true);
                unique_lock<mutex> lk2(routers[i].start_mtx);
                routers[i].start_flag = true;
                routers[i].start_cv.notify_one();
                routers[i].inbox_cv.notify_one();
            }
        } else {
            this_thread::sleep_for(chrono::seconds(2));
        }
    }

    for (int i = 0; i < N; ++i)
        if (threads_global[i].joinable()) threads_global[i].join();

    cout << "Final routing tables above.\n";
}