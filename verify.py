"""Check the solution: decrypt each telegram with its key, re-encrypt the recovered plaintext,
compare with the transmitted ciphertext, and compare letter counts with Käthe Dabis's handwritten notes.

  python verify.py                 # all four telegrams
  python verify.py --search 1      # independent exhaustive search over all 10! keys (numpy, a few seconds); 1..4 or all
"""
import sys, re
from collections import Counter
from dabis import load, decrypt, encrypt, groups, triangle, bruteforce, N

def letters(s):
    s = s.upper().replace('Ä', 'AE').replace('Ö', 'OE').replace('Ü', 'UE').replace('ß', 'SS')
    return re.sub('[^A-Z]', '', s)

def diff(a, b):
    return ''.join(sorted((Counter(a) - Counter(b)).elements())) or '-'

def show():
    T = load(); total = 0
    for k in ('1', '2', '3', '4'):
        t = T[k]; ct, key, pt = t['ct'], t['key'], t['plaintext']
        dec = decrypt(ct, key); enc = encrypt(pt, key)
        bad = [(i, ct[i], enc[i]) for i in range(N) if ct[i] != enc[i]]
        total += len(bad)
        print(f'=== No. {k}   sent {t["sent"]}   key {key}')
        print('  transmitted   ', groups(ct))
        print('  decrypted     ', dec)
        print(triangle(dec))
        print('  plaintext     ', t['plaintext_words'])
        print('  re-encrypted  ', groups(enc))
        print('  differences   ', bad if bad else 'none', '(position, transmitted, by key)')
        if t['handwritten']:
            h = letters(t['handwritten'])
            print(f'  handwritten    {t["handwritten"]}  ({len(h)} letters)')
            print(f'  plaintext vs handwritten: only in plaintext [{diff(pt, h)}], only in handwritten [{diff(h, pt)}]')
        print()
    print(f'Total differences between transmitted and re-encrypted text: {total} of 220 letters')

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--search':
        T = load()
        for k in (('1', '2', '3', '4') if sys.argv[2] == 'all' else (sys.argv[2],)):
            print(f'No. {k}: best keys out of 3,628,800 (score = sum of log10 quadgram probabilities)')
            for s, key, p in bruteforce(T[k]['ct']):
                print(f'  {s:9.2f}  {key}  {p}')
    else:
        show()
