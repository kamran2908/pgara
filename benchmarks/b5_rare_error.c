extern void log_error(int i);
void log_error(int i) {} // Dummy implementation to ensure it links/compiles without issues

int compute(int n, int *data) {
    int sum = 0;          // v1: touched every loop iteration
    int errCount = 0;     // v2: touched only on a rare, data-dependent branch
    for (int i = 0; i < n; i++) {
        if (data[i] < 0) {        // taken in well under 1% of iterations
            errCount++;
            log_error(i);
        }
        sum += data[i] * 2;
    }
    return sum + errCount;
}
