"""Rebuild the German quadgram model lm/quad.f32 (log10 probabilities of 26^4 four-letter sequences, float32).

Corpora (download them yourself):
  - Leipzig Corpora Collection, deu_mixed-typical_2011_100K and deu_news_2023_100K
    (https://wortschatz.uni-leipzig.de/en/download/German, CC BY)
  - Tatoeba German sentences, deu_sentences.tsv.bz2 (https://tatoeba.org/en/downloads, CC BY 2.0 FR)
Normalisation as in the telegrams: Ä->AE, Ö->OE, Ü->UE, ß->SS, letters only, no spaces.
1 % of the sentences are held out (lm/heldout.txt) and used only for the control in checks.py.

  python lm/build_lm.py deu_mixed-typical_2011_100K.tar.gz deu_news_2023_100K.tar.gz deu_sentences.tsv.bz2
"""
import os, re, sys, tarfile, bz2, random
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))

def conv(s):
    s = s.upper().replace('Ä', 'AE').replace('Ö', 'OE').replace('Ü', 'UE').replace('ß', 'SS')
    return re.sub('[^A-Z]', '', s)

def sentences(paths):
    for p in paths:
        if p.endswith('.tar.gz'):
            with tarfile.open(p) as tf:
                for m in tf.getmembers():
                    if m.name.endswith('-sentences.txt'):
                        for l in tf.extractfile(m):
                            yield l.decode('utf-8', 'replace').split('\t', 1)[-1]
        else:
            for l in bz2.open(p, 'rt', encoding='utf-8'):
                yield l.rstrip('\n').split('\t')[-1]

def main():
    rng = random.Random(1939)
    cnt = np.zeros(26 ** 4, np.float64); held = []
    for s in sentences(sys.argv[1:]):
        t = conv(s)
        if len(t) < 4: continue
        if rng.random() < 0.01:
            held.append(t); continue
        a = np.frombuffer(t.encode(), np.uint8).astype(np.int64) - 65
        idx = ((a[:-3] * 26 + a[1:-2]) * 26 + a[2:-1]) * 26 + a[3:]
        np.add.at(cnt, idx, 1)
    tot = cnt.sum()
    np.log10((cnt + 0.5) / (tot + 0.5 * 26 ** 4)).astype(np.float32).tofile(os.path.join(OUT, 'quad.f32'))
    open(os.path.join(OUT, 'heldout.txt'), 'w').write('\n'.join(held))
    print('quadgrams', int(tot), 'held-out sentences', len(held))

if __name__ == '__main__':
    main()
