/* Known-plaintext solver for a triangle transposition with TWO independent orders:
   ROW ORDER (the order in which rows are taken inside every column) and COLUMN ORDER.
   For every one of the 10! row orders it builds the ten column strings and checks whether
   the ciphertext can be cut into those strings in some column order, allowing up to E mismatches.
   '?' in the plaintext matches any letter.
   Output: one line per solution  "row_order=... column_order=... mismatches=..."
   Build: cc -O3 -o known_solve known_solve.c
   Usage: known_solve PLAINTEXT CIPHERTEXT E [MAXOUT] */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define N 55

static char P[N + 1], C[N + 1], colstr[10][11];
static int collen[10], used[10], ord[10], E, mism;
static long nodes;

static inline int eqc(char a, char b) { return a == b || a == '?' || b == '?'; }
static int tile(int pos, int depth, int budget) {
    if (pos == N) { mism = E - budget; return 1; }
    if (++nodes > 200000) return 0;
    for (int c = 0; c < 10; c++) {
        if (used[c] || pos + collen[c] > N) continue;
        int b = budget, ok = 1;
        for (int r = 0; r < collen[c]; r++) if (!eqc(colstr[c][r], C[pos + r])) { if (--b < 0) { ok = 0; break; } }
        if (!ok) continue;
        used[c] = 1; ord[depth] = c;
        if (tile(pos + collen[c], depth + 1, b)) { used[c] = 0; return 1; }
        used[c] = 0;
    }
    return 0;
}
static int nextperm(int *a, int m) {
    int i = m - 2; while (i >= 0 && a[i] >= a[i + 1]) i--;
    if (i < 0) return 0;
    int j = m - 1; while (a[j] <= a[i]) j--;
    int t = a[i]; a[i] = a[j]; a[j] = t;
    for (int l = i + 1, r = m - 1; l < r; l++, r--) { t = a[l]; a[l] = a[r]; a[r] = t; }
    return 1;
}
int main(int argc, char **argv) {
    if (argc < 4 || strlen(argv[1]) != N || strlen(argv[2]) != N) {
        fprintf(stderr, "usage: known_solve PLAINTEXT(55) CIPHERTEXT(55) E [MAXOUT]\n"); return 1;
    }
    strcpy(P, argv[1]); strcpy(C, argv[2]); E = atoi(argv[3]);
    int maxout = argc > 4 ? atoi(argv[4]) : 20;
    int pi[10]; long found = 0;
    for (int i = 0; i < 10; i++) pi[i] = i;
    do {
        /* column c: rows r >= c, taken in the order they appear in pi */
        for (int c = 0; c < 10; c++) {
            int L = 0;
            for (int s = 0; s < 10; s++) { int r = pi[s]; if (r >= c) colstr[c][L++] = P[r * (r + 1) / 2 + c]; }
            collen[c] = L; colstr[c][L] = 0;
        }
        nodes = 0;
        if (tile(0, 0, E)) {
            if (found < maxout) {
                printf("row_order=");
                for (int i = 0; i < 10; i++) printf("%d", pi[i]);
                printf(" column_order=");
                for (int i = 0; i < 10; i++) printf("%d", ord[i]);
                printf(" mismatches=%d\n", mism);
            }
            found++;
        }
    } while (nextperm(pi, 10));
    printf("searched=3628800 solutions=%ld\n", found);
    return 0;
}
