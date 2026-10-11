"""Known-plaintext check for No. 2, No. 3 and No. 4.

The solver (known_solve.c) treats the ROW ORDER and the COLUMN ORDER as two independent unknowns
(10! x 10! combinations) and finds every combination that turns the plaintext into the transmitted
ciphertext with at most E mismatches. If the solution is unique and the column order turns out to be
the inverse of the row order, both are given by ONE ten-digit key, the key used in dabis.py.

It also shows that Käthe's handwritten notes, taken literally, do NOT fit: the encrypted text is
Dabis's abbreviated version (VILE, MURXE, LIBSTE, ...).

  make && python known_solve.py
"""
import os, re, subprocess
from dabis import load

BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'known_solve')

def letters(s):
    s = s.upper().replace('Ä', 'AE').replace('Ö', 'OE').replace('Ü', 'UE').replace('ß', 'SS')
    return re.sub('[^A-Z]', '', s)

def solve(pt, ct, E):
    out = subprocess.run([BIN, pt, ct, str(E)], capture_output=True, text=True).stdout
    sols = re.findall(r'row_order=(\d{10}) column_order=(\d{10}) mismatches=(\d+)', out)
    return sols, out.strip().splitlines()[-1]

def inverse(seq):
    inv = [0] * 10
    for i, v in enumerate(map(int, seq)): inv[v] = i
    return ''.join(map(str, inv))

# 55-letter versions of Käthe's note proposed in 2021 (one VIELE shortened to VIEL); neither fits
ALTERNATIVES = {'4': ['KLEINEBLONDEFRAUNOCHVIELEJAHREMITDIRVIELFROHEMURXVONDIR',
                      'KLEINEBLONDEFRAUNOCHVIELJAHREMITDIRVIELEFROHEMURXVONDIR']}

def main():
    if not os.path.exists(BIN):
        raise SystemExit('build first: make   (or: cc -O3 -o known_solve known_solve.c)')
    T = load()
    for k, E in (('3', 1), ('4', 1), ('2', 2)):
        t = T[k]
        sols, summary = solve(t['plaintext'], t['ct'], E)
        print(f'No. {k}: plaintext as enciphered by Dabis, up to {E} mismatch(es): {summary}')
        best = min(int(m) for _, _, m in sols) if sols else None
        for ro, co, m in sols:
            tag = '  <- best' if int(m) == best else ''
            print(f'   row order {ro}  column order {co}  mismatches {m}  column order == inverse(row order): {co == inverse(ro)}{tag}')
            if int(m) == best:
                print(f'   => single key {ro} (dabis.py key for No. {k}: {t["key"]})')
        h = letters(t['handwritten'])
        print(f'   handwritten note has {len(h)} letters, so taken literally it cannot be the 55-letter enciphered text')
        for alt in ALTERNATIVES.get(k, []):
            _, asum = solve(alt, t['ct'], 3)
            print(f'   handwriting trimmed to 55 letters {alt}, up to 3 mismatches: {asum}')
        print()

if __name__ == '__main__':
    main()
