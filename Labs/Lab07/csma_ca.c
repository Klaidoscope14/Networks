#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

double exp_rv(double lambda) {
    double u = rand() / (RAND_MAX + 1.0);
    if (u <= 0.0) u = 1e-12;
    return -log(u) / lambda;
}

int main() {
    srand((unsigned) time(NULL));

    const int N = 50;
    const double frame_time = 1.0;
    const double slot_time = 0.01;
    const int frame_slots = (int)round(frame_time / slot_time);
    const double G_min = 0.0;
    const double G_max = 3.0;
    const double G_step = 0.1;
    const int cw_values[] = {4, 8, 16, 32};
    const int CWcount = sizeof(cw_values) / sizeof(cw_values[0]);
    const double SIM_TIME_MAX = 200000.0;
    const long SUCCESS_TARGET = 20000;

    FILE *fp = fopen("csma_ca_output.csv", "w");
    if (!fp) { perror("fopen"); return 1; }
    fprintf(fp, "G,CW,Throughput_S\n");

    for (double G = G_min; G <= G_max + 1e-9; G += G_step) {
        if (G == 0.0) continue;
        for (int ci = 0; ci < CWcount; ++ci) {
            int CW = cw_values[ci];
            double lambda_station = (G / (double)N);

            double t = 0.0;
            double next_arrival[N];
            int backlog[N];
            int backoff[N];
            int transmitting[N];
            int tx_end_slot = -1;
            int current_slot = 0;
            long success = 0;
            for (int i = 0; i < N; ++i) {
                backlog[i] = 0;
                backoff[i] = -1;
                transmitting[i] = 0;
                next_arrival[i] = exp_rv(lambda_station);
            }

            // ----------- CSMA/CA simulation -----------
            while (t < SIM_TIME_MAX && success < SUCCESS_TARGET) {
                double slot_start_time = current_slot * slot_time;
                double slot_end_time = slot_start_time + slot_time;

                // process arrivals within this slot
                for (int i = 0; i < N; ++i) {
                    while (next_arrival[i] >= slot_start_time && next_arrival[i] < slot_end_time) {
                        backlog[i] = 1;
                        if (backoff[i] < 0) backoff[i] = rand() % CW;
                        next_arrival[i] += exp_rv(lambda_station);
                    }
                }

                // if channel free (no transmissions ongoing)
                int channel_busy = 0;
                for (int i = 0; i < N; ++i) if (transmitting[i]) { channel_busy = 1; break; }

                if (!channel_busy) {
                    // decrement backoff for stations that have a packet and a backoff set
                    for (int i = 0; i < N; ++i) {
                        if (backlog[i] && backoff[i] >= 0) {
                            if (backoff[i] > 0) backoff[i]--;
                        }
                    }

                    // collect transmitters whose backoff reached zero this slot
                    int starters_count = 0;
                    int starters_idx[N];
                    for (int i = 0; i < N; ++i) {
                        if (backlog[i] && backoff[i] == 0) {
                            starters_idx[starters_count++] = i;
                        }
                    }

                    if (starters_count > 0) {
                        // all starters begin transmission at slot boundary
                        for (int k = 0; k < starters_count; ++k) {
                            int s = starters_idx[k];
                            transmitting[s] = 1;
                            backoff[s] = -1; // cleared while transmitting
                        }
                        tx_end_slot = current_slot + frame_slots;

                        if (starters_count == 1) {
                            int s = starters_idx[0];
                            backlog[s] = 0;
                            success++;
                        } else {
                            // collision: all colliding stations will attempt retransmission later
                            for (int k = 0; k < starters_count; ++k) {
                                int s = starters_idx[k];
                                // packet remains (assume retransmit) -> assign new backoff in next idle
                                backlog[s] = 1;
                                backoff[s] = rand() % CW;
                                transmitting[s] = 1; // still mark as transmitting for occupied slots
                            }
                        }
                    }
                }

                if (tx_end_slot == current_slot + 1) {
                    for (int i = 0; i < N; ++i) transmitting[i] = 0;
                    tx_end_slot = -1;
                } 

                else if (tx_end_slot == current_slot) {
                    for (int i = 0; i < N; ++i) transmitting[i] = 0;
                    tx_end_slot = -1;
                }

                current_slot++;
                t = current_slot * slot_time;
            }

            double S = (t > 0.0) ? ((double)success / t) : 0.0;
            fprintf(fp, "%.3f,%d,%.6f\n", G, CW, S);
            fflush(fp);
            printf("G=%.2f CW=%d S=%.4f\n", G, CW, S);
        }
    }

    fclose(fp);
    printf("CSMA/CA simulation finished. Results saved to csma_ca_output.csv\n");
    return 0;
}