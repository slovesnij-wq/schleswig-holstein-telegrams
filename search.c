/* Exhaustive search over all 10! = 3,628,800 keys of the Dabis triangle cipher (see dabis.py).
   Modes:
     search lm LMFILE CIPHERTEXT [TOP]        score every decryption with the quadgram model, print TOP best
     search tmpl CIPHERTEXT TEMPLATE [TOP]    score = number of letters equal to TEMPLATE ('?' matches anything)
     search enc PLAINTEXT KEY                 encrypt (KEY = ten digits, e.g. 0931276845)
     search dec CIPHERTEXT KEY                decrypt
   Build: cc -O3 -o search search.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define N 55
#define TMAX 1000

static float *LM;
static int pos_rc(int r, int c) { return r * (r + 1) / 2 + c; }

/* ord[k] = plaintext position of the k-th ciphertext letter */
static void build_order(const int *L, int *ord) {
    int col_of_digit[10], k = 0;
    for (int c = 0; c < 10; c++) col_of_digit[L[c]] = c;
    for (int d = 0; d < 10; d++) {
        int c = col_of_digit[d];
        for (int s = 0; s < 10; s++) { int r = L[s]; if (r >= c) ord[k++] = pos_rc(r, c); }
    }
}
static int parse_key(const char *s, int *L) {
    int n = 0, seen = 0;
    for (; *s && n < 10; s++) if (*s >= '0' && *s <= '9') { L[n] = *s - '0'; seen |= 1 << L[n]; n++; }
    return n == 10 && seen == 1023;
}
static int nextperm(int *a, int m) {
    int i = m - 2; while (i >= 0 && a[i] >= a[i + 1]) i--;
    if (i < 0) return 0;
    int j = m - 1; while (a[j] <= a[i]) j--;
    int t = a[i]; a[i] = a[j]; a[j] = t;
    for (int l = i + 1, r = m - 1; l < r; l++, r--) { t = a[l]; a[l] = a[r]; a[r] = t; }
    return 1;
}
static double tsc[TMAX]; static int tkey[TMAX][10]; static int nt, TOP;
static void push(double s, const int *L) {
    if (nt < TOP) { tsc[nt] = s; memcpy(tkey[nt], L, sizeof(int) * 10); nt++; return; }
    int w = 0; for (int i = 1; i < nt; i++) if (tsc[i] < tsc[w]) w = i;
    if (s > tsc[w]) { tsc[w] = s; memcpy(tkey[w], L, sizeof(int) * 10); }
}
static int usage(void) {
    fprintf(stderr, "usage: search lm LMFILE CT [TOP] | search tmpl CT TEMPLATE [TOP] | search enc PT KEY | search dec CT KEY\n");
    return 1;
}
int main(int argc, char **argv) {
    if (argc < 4) return usage();
    const char *mode = argv[1];
    int L[10], ord[N]; char out[N + 1]; out[N] = 0;
    if (!strcmp(mode, "enc") || !strcmp(mode, "dec")) {
        if (strlen(argv[2]) != N || !parse_key(argv[3], L)) return usage();
        build_order(L, ord);
        const char *s = argv[2];
        if (!strcmp(mode, "enc")) for (int k = 0; k < N; k++) out[k] = s[ord[k]];
        else for (int k = 0; k < N; k++) out[ord[k]] = s[k];
        printf("%s\n", out); return 0;
    }
    const char *ct, *tmpl = NULL;
    if (!strcmp(mode, "lm")) {
        FILE *f = fopen(argv[2], "rb"); if (!f) { perror(argv[2]); return 1; }
        LM = malloc(sizeof(float) * 456976);
        if (fread(LM, sizeof(float), 456976, f) != 456976) { fprintf(stderr, "bad LM file\n"); return 1; }
        fclose(f); ct = argv[3]; TOP = argc > 4 ? atoi(argv[4]) : 10;
    } else if (!strcmp(mode, "tmpl")) {
        if (argc < 4) return usage();
        ct = argv[2]; tmpl = argv[3]; TOP = argc > 4 ? atoi(argv[4]) : 10;
        if (strlen(tmpl) != N) return usage();
    } else return usage();
    if (strlen(ct) != N) return usage();
    if (TOP > TMAX) TOP = TMAX; if (TOP < 1) TOP = 1;
    for (int i = 0; i < 10; i++) L[i] = i;
    do {
        build_order(L, ord);
        for (int k = 0; k < N; k++) out[ord[k]] = ct[k];
        double s = 0;
        if (LM) {
            int a = out[0] - 65, b = out[1] - 65, c = out[2] - 65;
            for (int k = 3; k < N; k++) { int d = out[k] - 65; s += LM[((a * 26 + b) * 26 + c) * 26 + d]; a = b; b = c; c = d; }
        } else for (int k = 0; k < N; k++) s += (tmpl[k] == '?' || tmpl[k] == out[k]);
        push(s, L);
    } while (nextperm(L, 10));
    for (int i = 0; i < nt; i++) for (int j = i + 1; j < nt; j++) if (tsc[j] > tsc[i]) {
        double t = tsc[i]; tsc[i] = tsc[j]; tsc[j] = t;
        int a[10]; memcpy(a, tkey[i], sizeof a); memcpy(tkey[i], tkey[j], sizeof a); memcpy(tkey[j], a, sizeof a);
    }
    for (int i = 0; i < nt; i++) {
        build_order(tkey[i], ord); for (int k = 0; k < N; k++) out[ord[k]] = ct[k];
        printf("%.3f ", tsc[i]); for (int k = 0; k < 10; k++) printf("%d", tkey[i][k]); printf(" %s\n", out);
    }
    return 0;
}
