"""How the triangle was found: a test that ignores the order of letters inside each line.

If the plaintext is written row by row into a figure and the ciphertext is read out line by line
(whole columns, in some order, in ANY order inside each column), then the ciphertext can be cut into
consecutive blocks whose letters are exactly the letters of the figure's columns. We compute the minimum
number of letters that do not fit over all ways of cutting the ciphertext (dynamic programming over
subsets of lines) and compare with shuffled plaintexts (same letters, random order).

Figures: the triangle 1+2+...+10 (read by columns), the 5 x 11 table (read by columns) and
the 11 x 5 table (read by columns).

  python discovery.py [N_SHUFFLES]      (default 1000)
"""
import sys, random
from collections import Counter
from dabis import load, N

def figures():
    tri = [[r * (r + 1) // 2 + c for r in range(c, 10)] for c in range(10)]
    t511 = [[r * 11 + c for r in range(5)] for c in range(11)]
    t115 = [[r * 5 + c for r in range(11)] for c in range(5)]
    return {'triangle 1..10, columns': tri, '5 x 11, columns': t511, '11 x 5, columns': t115}

def misfit(ct, pt, lines):
    """Minimum number of ciphertext letters that are not in their block's line, over all block orders."""
    n = len(lines); L = [len(x) for x in lines]
    want = [Counter(pt[j] for j in x) for x in lines]
    cost = {}
    for l in range(n):
        for st in range(N - L[l] + 1):
            cost[l, st] = sum((Counter(ct[st:st + L[l]]) - want[l]).values())
    INF = 10 ** 9; dp = [INF] * (1 << n); dp[0] = 0; pos = [0] * (1 << n)
    for s in range(1 << n):
        if dp[s] == INF: continue
        for l in range(n):
            if s >> l & 1: continue
            t = s | 1 << l; pos[t] = pos[s] + L[l]
            v = dp[s] + cost[l, pos[s]]
            if v < dp[t]: dp[t] = v
    return dp[-1]

def main():
    ns = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    T = load(); rng = random.Random(7)
    for k in ('3', '4', '2'):
        ct, pt = T[k]['ct'], T[k]['plaintext']
        print(f'No. {k} (plaintext as enciphered by Dabis)')
        for name, lines in figures().items():
            real = misfit(ct, pt, lines)
            noise = sorted(misfit(ct, ''.join(rng.sample(pt, N)), lines) for _ in range(ns))
            print(f'   {name:24s} misfit letters: {real:2d}    shuffled plaintext ({ns}x): min {noise[0]}, median {noise[ns // 2]}, max {noise[-1]}')
        print()

if __name__ == '__main__':
    main()
