int count_tokens(const char *str) {
    int count = 0;
    int in_token = 0;
    for (int i = 0; str[i] != '\0'; i++) {
        char c = str[i];
        if (c == ' ' || c == '\t' || c == '\n') {
            in_token = 0;
        } else {
            if (!in_token) {
                count++;
                in_token = 1;
            }
        }
    }
    return count;
}
