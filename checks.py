"""Control and noise for the ciphertext-only search (needs the compiled ./search).

  python checks.py blind            # search all four telegrams without any plaintext: is the right key first?
  python checks.py control 30       # 30 German 55-letter texts (held-out sentences), random keys: how often is the true key first?
  python checks.py null 100 [1]     # 100 random shuffles of telegram No. 1 (same letters): best score and gap to second best
"""
import os, sys, random, subprocess
from dabis import load, encrypt, N, HERE

BIN = os.path.join(HERE, 'search'); LM = os.path.join(HERE, 'lm', 'quad.f32')

def search(ct, top=2):
    out = subprocess.run([BIN, 'lm', LM, ct, str(top)], capture_output=True, text=True).stdout
    rows = []
    for l in out.splitlines():
        s, key, pt = l.split()
        rows.append((float(s), key, pt))
    return rows

def main():
    if not os.path.exists(BIN):
        raise SystemExit('build first: make   (or: cc -O3 -o search search.c)')
    mode = sys.argv[1]
    T = load()
    if mode == 'blind':
        for k in ('1', '2', '3', '4'):
            r = search(T[k]['ct'], 3)
            ok = r[0][1] == T[k]['key']
            print(f'No. {k}: best {r[0][1]} ({r[0][0]:.1f}) {r[0][2]}   second {r[1][0]:.1f}   gap {r[0][0] - r[1][0]:.1f}   '
                  f'{"= key in data/telegrams.json" if ok else "differs from data key"}')
    elif mode == 'control':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        rng = random.Random(55)
        held = [l.strip() for l in open(os.path.join(HERE, 'lm', 'heldout.txt')) if len(l.strip()) >= N]
        hits = 0
        for t in range(n):
            p = rng.choice(held); s = rng.randrange(len(p) - N + 1); p = p[s:s + N]
            L = list(range(10)); rng.shuffle(L); key = ''.join(map(str, L))
            r = search(encrypt(p, key))
            hit = r[0][1] == key or r[0][2] == p
            hits += hit
            print(f'{t:3d} {"OK  " if hit else "MISS"} best {r[0][0]:.1f} second {r[1][0]:.1f}  {p}  ->  {r[0][2]}')
        print(f'control: true key ranked first in {hits} of {n}')
    elif mode == 'null':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        k = sys.argv[3] if len(sys.argv) > 3 else '1'
        rng = random.Random(1939); best, gaps = [], []
        for t in range(n):
            c = ''.join(rng.sample(T[k]['ct'], N))
            r = search(c); best.append(r[0][0]); gaps.append(r[0][0] - r[1][0])
            print(f'{t:3d} best {r[0][0]:.1f} gap {gaps[-1]:.1f}  {r[0][2]}', flush=True)
        real = search(T[k]['ct'])
        best.sort(); gaps.sort()
        print(f'shuffled No. {k}: best score median {best[n // 2]:.1f}, max {best[-1]:.1f}; gap median {gaps[n // 2]:.1f}, max {gaps[-1]:.1f}')
        print(f'real No. {k}:     best score {real[0][0]:.1f}, gap {real[0][0] - real[1][0]:.1f}   {real[0][2]}')
    else:
        print(__doc__)

if __name__ == '__main__':
    main()
