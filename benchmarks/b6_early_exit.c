int find_value(int n, int *data, int target) {
    int index = -1;
    for (int i = 0; i < n; i++) {
        if (data[i] == target) {
            index = i;
            break;
        }
    }
    return index;
}
