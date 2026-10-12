# The Schleswig-Holstein telegrams (1939): cipher recovered

Between January and March 1939 Günther Dabis, serving on the German battleship *Schleswig-Holstein* (the ship that opened fire on Westerplatte on 1 September 1939), sent four encrypted telegrams to his wife Käthe in Kiel. Klaus Schmeh published them as unsolved on his blog Cipherbrain in [2017](https://scienceblogs.de/klausis-krypto-kolumne/2017/09/02/who-can-decipher-this-encrypted-telex-from-a-famous-battle-ship/) and [2021](https://scienceblogs.de/klausis-krypto-kolumne/2021/01/03/drei-weitere-ungeloeste-verschluesselte-nachrichten-vom-kriegsschiff-schleswig-holstein/). For three of them Käthe's handwritten decryption survives on the form; for No. 1 it does not, and No. 1 had never been read.

This repository contains the recovered system, the four keys, the plaintexts and code to check all of it independently.

[Русская версия](README.ru.md)

## Result

| No. | Sent | Key | Text as enciphered by Dabis | Translation |
|---|---|---|---|---|
| 1 | 5 Jan 1939, 18:28 | `0931276845` | ZUR GROSSEN STUNDE HALS UND BEINBRUCH UND X GLATTEN STAPELLAUF M X | "For the great hour, break a leg, and a smooth launch!" |
| 2 | 11 Jan 1939, 20:00 | `1093276548` | LIBSTE KLEINE FRAU BIN SO GLUKLICH U DANKBAR ES LEBE MURX U DIE MUTI | "Dearest little wife, I am so happy and grateful. Long live Murx and Mummy!" |
| 3 | 16 Feb 1939, 19:40 | `2193076458` | BISHER AHNUNGSLOS FEIN DASS ALLES GUT SEHR STOLZ AUF TAPFERE FRAU | "Unaware until now. Good that all is well. Very proud of brave wife." |
| 4 | 13 Mar 1939, 20:15 | `1590276348` | KLEINE BLONDE FRAU NOCH VILE JAHRE MIT DIR VILE FROHE MURXE VON DIR | "Little blonde wife, many more years with you, many happy Murxes from you." |

"Murks"/"Murx" was the family nickname of the expected child. *Stapellauf* is the launch of a new ship; on 5 January the sailor is most likely joking about the coming birth (see *Not established* below).

## The system

1. The message is made exactly 55 letters long (Dabis shortened words or added X) and written row by row, left to right, into a triangle of 10 rows with 1, 2, …, 10 cells.
2. The key is the ten digits 0–9 in some order, written above the ten columns.
3. The columns are taken in the order of their digits: first the column under 0, then the column under 1, and so on.
4. Inside each column the rows are taken in the order in which the digits stand in the key, left to right. Equivalently: rearrange the rows by the key, then read each column from top to bottom. Empty cells are skipped.
5. The 55 letters are sent in 11 groups of five.

Hand check for No. 1, key `0 9 3 1 2 7 6 8 4 5`: the digit 0 stands above column 0, so that column comes first. Taking its cells in the row order 0, 9, 3, 1, 2, 7, 6, 8, 4, 5 gives `Z A S U G R N G S E`, the first two groups of the telegram (`ZASUG RNGSE`). Digit 1 stands above column 3; its rows in key order (9, 3, 7, 6, 8, 4, 5) give `L N H E T N L`, the next letters.

```
             Z
            U R
           G R O
          S S E N
         S T U N D
        E H A L S U
       N D B E I N B
      R U C H U N D X
     G L A T T E N S T
    A P E L L A U F M X
```

## Check it yourself

Requirements: Python 3.8+ with `numpy`; a C compiler for the fast tools (`make`).

```bash
make                          # builds ./search and ./known_solve
python verify.py              # decrypt, re-encrypt, compare
python known_solve.py         # known-plaintext solver with two independent orders
python checks.py blind        # ciphertext-only search over all 10! keys
python checks.py control 30   # control on synthetic German texts
python checks.py null 100     # noise: shuffled No. 1
python discovery.py           # the test that revealed the triangle
python verify.py --search all # the exhaustive search again, pure numpy, no compiler (about 6 s per telegram)
```

What you should see:

1. **`verify.py`.** Re-encrypting the four plaintexts with their keys reproduces the transmitted ciphertexts with 4 differences in 220 letters: none in No. 1; in No. 2 two adjacent letters are swapped (group 9 sent `EEIKO`, the key gives `EEKIO`); in No. 3 an N went out as H; in No. 4 an L went out as I. The H and the I were already noticed as "extra letters" by blog readers in 2021.
2. **`known_solve.py`.** The solver treats the row order and the column order as two independent unknowns and tries all 3,628,800 row orders with any column order. For No. 2, No. 3 and No. 4 there is exactly one solution each, and in all three the column order is the inverse of the row order, i.e. both come from one ten-digit key. Käthe's note for No. 4, trimmed to 55 letters in either of the two ways proposed in 2021, has no solution at all.
3. **`checks.py blind`.** Without any plaintext, scoring every decryption with a German quadgram model puts the correct key first for all four telegrams (No. 3 and No. 4 lead the runner-up by 23 points).
4. **`checks.py control 30`.** 29 of 30 synthetic German 55-letter texts with random keys are solved the same way.
5. **`checks.py null 100`.** For 100 shuffles of the letters of No. 1, the best of all 10! keys is gibberish with a score of −284.2 (median) and −274.6 at most. The real No. 1 scores −228.8, far outside the noise. (The gap between the first and second key is not a useful statistic: on shuffles it reaches 12.8.)
6. **`discovery.py`.** Cut the ciphertext into consecutive blocks with the letters of whole triangle columns (ignoring the order inside each column): No. 2, No. 3 and No. 4 leave 0, 1 and 1 letters unplaced; 1000 shuffled plaintexts leave 22–24 (median) and never fewer than 17. The 5 × 11 and 11 × 5 tables are at noise level. Earlier attempts read the triangle along fixed routes; the key also shuffles the rows inside each column, so every fixed route fails.

## Why Käthe's notes do not match letter for letter

The cipher contains exactly the letters Dabis wrote into the triangle. Käthe wrote the words out in full:

| No. | Cipher | Dabis | Käthe | Difference |
|---|---|---|---|---|
| 2 | 55 | 55 | 60 | Dabis: LIBSTE, GLUKLICH, MURX, MUTI; Käthe: liebste, glücklich, murks, mutti |
| 3 | 55 | 55 | 50 | Käthe omitted SEHR and wrote DAS for DASS (the missing E, H, R, S, S) |
| 4 | 55 | 55 | 56 | Dabis: VILE twice and MURXE; Käthe: viele, viele, murx |

On top of this, each of No. 2–4 has the single transmission defect listed above. Whether a letter was garbled on the telegraph line or by Dabis while copying cannot be decided.

## Not established

- **How the keys were chosen.** All four keys differ. They share features (digits 7 and 6 always in places 6 and 7; in No. 2–4 a 9 in place 3 and an 8 at the end; the first digits of No. 1–3 are 0, 1, 2), but no word, name, date or telegram number we tried produces them. They were probably agreed in advance.
- **The final M X of No. 1.** The words take 52 letters; the remaining three cells hold the X after the second UND (X was the usual full stop in German military radio traffic) and M X at the end, most likely fillers. What M stands for is unknown.
- **The reading of *Stapellauf* as the birth.** It rests on the dates (good wishes on 5 January, "es lebe Murx und die Mutti" on 11 January) and on a blog comment by a reader of the letters ([H.B., 5 Jan 2021](https://scienceblogs.de/klausis-krypto-kolumne/2021/01/03/drei-weitere-ungeloeste-verschluesselte-nachrichten-vom-kriegsschiff-schleswig-holstein/#comment-1721839)) that the child was born in January 1939. The letters themselves (153 scanned pages from Patrick Hayes's collection) are no longer online.
- **Transcription.** BXLTU is the first of the 11 groups of No. 2 (not a header). The second letter of group NLLUI in No. 1 is faint on the scan; the decryption confirms L (HALS).

## Files

| File | Purpose |
|---|---|
| `data/telegrams.json` | ciphertexts, headers, dates, handwritten notes, plaintexts, keys, transmission defects |
| `dabis.py` | the cipher (encrypt, decrypt), quadgram scoring, pure-numpy exhaustive search |
| `verify.py` | decrypt, re-encrypt and compare; letter counts against the handwritten notes |
| `known_solve.c`, `known_solve.py` | known-plaintext solver with independent row and column orders |
| `search.c` | fast exhaustive search over all 10! keys (quadgram model or template); `enc` / `dec` |
| `checks.py` | blind search, control on synthetic texts, noise on shuffled ciphertexts |
| `discovery.py` | column-composition test for the triangle and two tables |
| `lm/quad.f32`, `lm/heldout.txt`, `lm/build_lm.py` | German quadgram model, held-out control sentences, rebuild script |

## Data and licences

- Ciphertexts, headers and handwritten notes were transcribed from the scans published on Cipherbrain. The scans are not included; they belong to Tobias Schrödel (No. 1) and Patrick Hayes (No. 2–4) and can be seen in the posts linked above.
- `lm/quad.f32` and `lm/heldout.txt` are derived from the [Leipzig Corpora Collection](https://wortschatz.uni-leipzig.de/en/download) (`deu_mixed-typical_2011_100K`, `deu_news_2023_100K`; CC BY; D. Goldhahn, T. Eckart, U. Quasthoff, *Building Large Monolingual Dictionaries at the Leipzig Corpora Collection: From 100 to 200 Languages*, LREC 2012) and from [Tatoeba](https://tatoeba.org) (CC BY 2.0 FR). `lm/build_lm.py` rebuilds both files byte for byte from these corpora.
- Code: MIT licence (`LICENSE`).

## Acknowledgements

Klaus Schmeh for publishing the telegrams; Tobias Schrödel and Patrick Hayes for the documents; the Cipherbrain readers whose comments laid the groundwork, in particular Norbert, who suggested the triangle in 2017, Michael (BGNC), Gerd and Gerry for comparing the handwritten notes with the ciphertexts, and Norman K. for the dates.
