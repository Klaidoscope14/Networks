#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
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
    const double G_min = 0.0;
    const double G_max = 3.0;
    const double G_step = 0.1;
    const double a_values[] = {0.0, 0.01, 0.05, 0.1, 0.2, 0.5};
    const int Acount = sizeof(a_values) / sizeof(a_values[0]);
    const double SIM_TIME_MAX = 200000.0;
    const int SUCCESS_TARGET = 20000;

    FILE *fp = fopen("csma_output.csv", "w");
    if (!fp) {
        perror("fopen");
        return 1;
    }
    fprintf(fp, "G,a,CSMA_throughput,CSMA_CD_throughput\n");

    printf("Running CSMA / CSMA-CD simulation...\n");

    for (double G = G_min; G <= G_max + 1e-9; G += G_step) {
        if (G == 0.0) continue;
        for (int ai = 0; ai < Acount; ++ai) {
            double a = a_values[ai];
            double tau = a * frame_time;
            double lambda_station = (G / (double)N) / frame_time;

            double t = 0.0;
            double last_tx_start = -1e18;
            int channel_busy = 0;
            double channel_free_time = 0.0;
            double channel_last_start = -1e18;
            int ongoing_tx_count = 0;
            double next_arrival[N];
            int backlog[N];
            int i;
            for (i = 0; i < N; ++i) {
                backlog[i] = 0;
                next_arrival[i] = exp_rv(lambda_station);
            }

            double sim_time_csma = 0.0;
            double sim_time_cd = 0.0;
            long success_csma = 0;
            long success_cd = 0;

            double next_arrival_cd[N];
            int backlog_cd[N];
            for (i = 0; i < N; ++i) {
                next_arrival_cd[i] = next_arrival[i];
                backlog_cd[i] = backlog[i];
            }

            // ----------- CSMA (no CD) simulation -----------
            {
                t = 0.0;
                channel_busy = 0;
                channel_free_time = 0.0;
                last_tx_start = -1e18;
                channel_last_start = -1e18;
                ongoing_tx_count = 0;
                double next_a[N];
                int b[N];
                for (i = 0; i < N; ++i) { next_a[i] = next_arrival[i]; b[i] = backlog[i]; }

                while ((t < SIM_TIME_MAX) && (success_csma < SUCCESS_TARGET)) {
                    double t_next = 1e300;
                    int ev_type = -1;
                    int ev_station = -1;
                    for (i = 0; i < N; ++i) {
                        if (next_a[i] < t_next) { t_next = next_a[i]; ev_type = 0; ev_station = i; }
                    }
                    if (channel_busy && channel_free_time < t_next) {
                        t_next = channel_free_time;
                        ev_type = 1;
                    }
                    if (t_next == 1e300) break;
                    t = t_next;

                    if (ev_type == 1) {
                        channel_busy = 0;
                        ongoing_tx_count = 0;
                        channel_free_time = 1e300;
                        continue;
                    } else {
                        int s = ev_station;
                        b[s] = 1;
                        next_a[s] = t + exp_rv(lambda_station);
                        int perceives_idle;
                        if (!channel_busy) perceives_idle = 1;
                        else {
                            if (t >= channel_last_start + tau) perceives_idle = 0;
                            else perceives_idle = 1;
                        }
                        if (b[s] && perceives_idle) {
                            double start = t;
                            double end = start + frame_time;
                            channel_busy = 1;
                            channel_last_start = start;
                            ongoing_tx_count = 1;
                            channel_free_time = end;
                            for (i = 0; i < N; ++i) {
                                if (i == s) continue;
                                if (next_a[i] > start && next_a[i] <= start + tau) {
                                    double t_other = next_a[i];
                                    b[i] = 0;
                                    ongoing_tx_count++;
                                    next_a[i] = t_other + exp_rv(lambda_station);
                                }
                            }
                            b[s] = 0;
                        }
                    }

                    if (channel_busy && fabs(channel_free_time - t) < 1e-12) {
                        if (ongoing_tx_count == 1) success_csma++;
                        channel_busy = 0;
                        ongoing_tx_count = 0;
                        channel_free_time = 1e300;
                    }
                }
                sim_time_csma = t;
            }

            // ----------- CSMA/CD simulation -----------
            {
                double t2 = 0.0;
                channel_busy = 0;
                channel_free_time = 0.0;
                last_tx_start = -1e18;
                channel_last_start = -1e18;
                ongoing_tx_count = 0;
                double next_a2[N];
                int b2[N];
                for (i = 0; i < N; ++i) { next_a2[i] = next_arrival_cd[i]; b2[i] = backlog_cd[i]; }

                while ((t2 < SIM_TIME_MAX) && (success_cd < SUCCESS_TARGET)) {
                    double t_next = 1e300;
                    int ev_type = -1;
                    int ev_station = -1;
                    for (i = 0; i < N; ++i) {
                        if (next_a2[i] < t_next) { t_next = next_a2[i]; ev_type = 0; ev_station = i; }
                    }
                    if (channel_busy && channel_free_time < t_next) {
                        t_next = channel_free_time;
                        ev_type = 1;
                    }
                    if (t_next == 1e300) break;
                    t2 = t_next;

                    if (ev_type == 1) {
                        if (ongoing_tx_count == 1) success_cd++;
                        channel_busy = 0;
                        ongoing_tx_count = 0;
                        channel_free_time = 1e300;
                        continue;
                    } else {
                        int s = ev_station;
                        b2[s] = 1;
                        next_a2[s] = t2 + exp_rv(lambda_station);
                        int perceives_idle;
                        if (!channel_busy) perceives_idle = 1;
                        else {
                            if (t2 >= channel_last_start + tau) perceives_idle = 0;
                            else perceives_idle = 1;
                        }
                        if (b2[s] && perceives_idle) {
                            double start = t2;
                            double intended_end = start + frame_time;
                            channel_busy = 1;
                            channel_last_start = start;
                            ongoing_tx_count = 1;
                            channel_free_time = intended_end;
                            int collision = 0;
                            for (i = 0; i < N; ++i) {
                                if (i == s) continue;
                                if (next_a2[i] > start && next_a2[i] <= start + tau) {
                                    double t_other = next_a2[i];
                                    b2[i] = 0;
                                    ongoing_tx_count++;
                                    next_a2[i] = t_other + exp_rv(lambda_station);
                                    collision = 1;
                                }
                            }
                            if (ongoing_tx_count > 1) {
                                double abort_time = start + 2.0 * tau;
                                if (abort_time < channel_free_time) channel_free_time = abort_time;
                            }
                            b2[s] = 0;
                        }
                    }

                    if (channel_busy && fabs(channel_free_time - t2) < 1e-12) {
                        if (ongoing_tx_count == 1) success_cd++;
                        channel_busy = 0;
                        ongoing_tx_count = 0;
                        channel_free_time = 1e300;
                    }
                }
                sim_time_cd = t2;
            }

            double S_csma = (sim_time_csma > 0.0) ? ((double)success_csma / sim_time_csma) : 0.0;
            double S_cd   = (sim_time_cd   > 0.0) ? ((double)success_cd   / sim_time_cd)   : 0.0;
            fprintf(fp, "%.3f,%.3f,%.6f,%.6f\n", G, a, S_csma, S_cd);
            fflush(fp);
            printf("G=%.2f a=%.3f  CSMA S=%.4f  CSMA/CD S=%.4f\n", G, a, S_csma, S_cd);
        }
    }

    fclose(fp);
    printf("Simulation finished. Results saved to csma_output.csv\n");
    return 0;
}