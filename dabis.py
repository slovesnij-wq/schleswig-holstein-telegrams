"""The Dabis triangle cipher (1939) and shared helpers.

System
  1. The message is made exactly 55 letters long and written row by row, left to right,
     into a triangle of 10 rows holding 1, 2, ..., 10 cells. Cell (r, c), c <= r,
     receives letter number r(r+1)/2 + c (0-based).
  2. The key is the ten digits 0-9 in some order, written above the ten columns:
     key[c] is the digit above column c.
  3. Columns are taken in the order of their digits: first the column under 0, then under 1, ...
  4. Inside a column the rows are taken in the order in which the digits stand in the key,
     left to right (row key[0] first, then row key[1], ...). Rows shorter than the column are skipped.
     Equivalently: rearrange the rows by the key, then read each column from top to bottom.
  5. The 55 letters are sent in 11 groups of five.
"""
import json, os, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
N = 55

def load():
    d = json.load(open(os.path.join(HERE, 'data', 'telegrams.json'), encoding='utf-8'))['telegrams']
    for t in d.values():
        t['ct'] = t['ciphertext'].replace(' ', '')
    return d

def cell_pos(r, c):
    return r * (r + 1) // 2 + c

def order(key):
    """Plaintext position of each ciphertext letter, in ciphertext order."""
    L = [int(ch) for ch in key]
    assert sorted(L) == list(range(10)), 'key must use each digit 0-9 once'
    col_of_digit = {d: c for c, d in enumerate(L)}
    out = []
    for d in range(10):
        c = col_of_digit[d]
        for r in L:
            if r >= c:
                out.append(cell_pos(r, c))
    return out

def encrypt(pt, key):
    assert len(pt) == N
    return ''.join(pt[j] for j in order(key))

def decrypt(ct, key):
    assert len(ct) == N
    p = [''] * N
    for k, j in enumerate(order(key)):
        p[j] = ct[k]
    return ''.join(p)

def groups(s):
    return ' '.join(s[i:i + 5] for i in range(0, len(s), 5))

def triangle(s, indent='    '):
    return '\n'.join(indent + ' ' * (9 - r) + ' '.join(s[cell_pos(r, 0):cell_pos(r, 0) + r + 1]) for r in range(10))

def load_lm():
    return np.fromfile(os.path.join(HERE, 'lm', 'quad.f32'), dtype=np.float32)

def lm_score(text, LM=None):
    LM = load_lm() if LM is None else LM
    a = [ord(ch) - 65 for ch in text]
    return float(sum(LM[((a[i] * 26 + a[i + 1]) * 26 + a[i + 2]) * 26 + a[i + 3]] for i in range(len(a) - 3)))

def bruteforce(ct, top=5, chunk=200000, LM=None):
    """Try all 10! = 3,628,800 keys; score each decryption with the quadgram model (numpy, a few seconds)."""
    LM = load_lm() if LM is None else LM
    c = np.frombuffer(ct.encode(), np.uint8).astype(np.int64) - 65
    perms = itertools.permutations(range(10)); best = []
    while True:
        Ls = np.array(list(itertools.islice(perms, chunk)), dtype=np.int64)
        if len(Ls) == 0: break
        B = len(Ls)
        inv = np.argsort(Ls, axis=1)                 # inv[:, d] = column carrying digit d
        cols = np.repeat(inv, 10, axis=1)            # (B, 100): t-th column read, repeated for each row slot
        rows = np.tile(Ls, (1, 10))                  # (B, 100): rows in key order
        valid = rows >= cols
        pos = rows * (rows + 1) // 2 + cols
        kidx = np.cumsum(valid, axis=1) - 1
        P = np.zeros((B, N), np.int64)
        bi = np.nonzero(valid)
        P[bi[0], pos[bi]] = c[kidx[bi]]
        q = ((P[:, :-3] * 26 + P[:, 1:-2]) * 26 + P[:, 2:-1]) * 26 + P[:, 3:]
        sc = LM[q].sum(1)
        for i in np.argsort(-sc)[:top]:
            best.append((float(sc[i]), ''.join(map(str, Ls[i])), ''.join(chr(65 + x) for x in P[i])))
        best = sorted(best, reverse=True)[:top]
    return best
