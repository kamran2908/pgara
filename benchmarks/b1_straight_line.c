int compute_arithmetic(int a, int b, int c) {
    int x = a + b;
    int y = x * c;
    int z = y - a;
    int w = z / (b + 1);
    return w + x + y + z;
}
