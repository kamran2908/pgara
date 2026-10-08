int process_opcode(int opcode, int a, int b) {
    int result = 0;
    switch (opcode) {
        case 0: result = a + b; break;
        case 1: result = a - b; break;
        case 2: result = a * b; break;
        case 3: result = a / (b + 1); break;
        case 4: result = a & b; break;
        case 5: result = a | b; break;
        case 6: result = a ^ b; break;
        default: result = -1; break;
    }
    return result;
}
