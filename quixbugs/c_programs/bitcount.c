int bitcount(int n) {
    int count = 0;
    while (n) {
        n ^= n - 1;
        count += 1;
    }
    return count;
}

int main() {
}
