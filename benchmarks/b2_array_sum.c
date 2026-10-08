int sum_array(int n, int *data) {
    int sum = 0;
    for (int i = 0; i < n; i++) {
        sum += data[i];
    }
    return sum;
}
