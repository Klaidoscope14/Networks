#include <stdio.h>
#include <math.h>
#define STEP 0.05   // increment in offered load (G)
#define MAX_G 5.0   // maximum offered load

// Throughput functions for Pure and Slotted ALOHA
double pure_aloha(double g) {
    return g * exp(-2 * g);
}

double slotted_aloha(double g) {
    return g * exp(-g);
}

int main() {
    double g;
    FILE *fp;

    fp = fopen("aloha_output.csv", "w");
    if (fp == NULL) {
        printf("Error opening file!\n");
        return 1;
    }

    fprintf(fp, "Offered_Load(G),Pure_ALOHA,Slotted_ALOHA\n");

    printf("\n--- Pure vs Slotted ALOHA Simulation ---\n");
    printf("G\tPure_Aloha(S)\tSlotted_Aloha(S)\n");

    for (g = 0.0; g <= MAX_G; g += STEP) {
        double s_pure = pure_aloha(g);
        double s_slotted = slotted_aloha(g);

        fprintf(fp, "%.2f,%.6f,%.6f\n", g, s_pure, s_slotted);
        printf("%.2f\t%.6f\t%.6f\n", g, s_pure, s_slotted);
    }

    fclose(fp);
    printf("\nData saved to 'aloha_output.csv'\n");
    printf("Plot this CSV using Python, Excel, or MATLAB for Throughput vs Offered Load.\n");
    return 0;
}