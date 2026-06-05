import csv
import os
import random
from collections import Counter, defaultdict
from decimal import Decimal, getcontext
from math import comb
from statistics import mean, median


CSV_PATH = "/Users/4c/Desktop/GHQ/data/loto7hh_4626_k44.csv"
N = 39
K = 7
RUNS = int(os.getenv("RUNS", "10000"))
SEED = int(os.getenv("SEED", "39"))
MODE = os.getenv("MODE", "history_only")


def read_combinations(path):
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            combo = tuple(int(row[f"Num{i}"]) for i in range(1, K + 1))
            rows.append(tuple(sorted(combo)))
    return rows


def lex_rank_1(combo):
    rank = 1
    previous = 0
    for i, x in enumerate(combo, start=1):
        for v in range(previous + 1, x):
            rank += comb(N - v, K - i)
        previous = x
    return rank


def lex_unrank_1(rank):
    combo = []
    previous = 0
    remaining_rank = rank

    for i in range(1, K + 1):
        for v in range(previous + 1, N + 1):
            block_size = comb(N - v, K - i)
            if remaining_rank > block_size:
                remaining_rank -= block_size
            else:
                combo.append(v)
                previous = v
                break

    return tuple(combo)


def draw_combo(rng):
    return tuple(sorted(rng.sample(range(1, N + 1), K)))


def percentile(sorted_values, p):
    idx = round((len(sorted_values) - 1) * p)
    return sorted_values[idx]


def simulate_next_duplicate(history_unique, runs, seed, mode):
    rng = random.Random(seed)
    results = []
    hit_counter = Counter()

    for _ in range(runs):
        steps = 0
        history_set = set(history_unique)
        seen = set(history_unique)

        while True:
            steps += 1
            combo = draw_combo(rng)

            if mode == "history_only":
                if combo in history_set:
                    results.append(steps)
                    hit_counter[combo] += 1
                    break
            elif mode == "timeline":
                if combo in seen:
                    results.append(steps)
                    hit_counter[combo] += 1
                    break
                seen.add(combo)
            else:
                raise ValueError("MODE mora biti history_only ili timeline")

    return results, hit_counter


def main():
    getcontext().prec = 40

    rows = read_combinations(CSV_PATH)
    positions_by_combo = defaultdict(list)
    for position, combo in enumerate(rows, start=1):
        positions_by_combo[combo].append(position)

    unique_combos = set(rows)
    duplicates_to_delete = len(rows) - len(unique_combos)
    full_space = comb(N, K)
    expected_duplicates = Decimal(comb(len(rows), 2)) / Decimal(full_space)
    next_hit_rate = Decimal(len(unique_combos)) / Decimal(full_space)

    print()
    print("izvlacenja:", len(rows))
    print("jedinstvenih kombinacija:", len(unique_combos))
    print("duplih za brisanje:", duplicates_to_delete)
    print("ceo prostor C(39,7):", full_space)
    print("ocekivani duplikati do sada:", expected_duplicates.quantize(Decimal("1.0000000000")))
    print("stopa sledeceg hita u istorijski skup:", next_hit_rate.quantize(Decimal("1.0000000000")))
    print()

    duplicate_groups = {combo: positions for combo, positions in positions_by_combo.items() if len(positions) > 1}
    print("postojeci duplikati:")
    for combo, positions in duplicate_groups.items():
        rank = lex_rank_1(combo)
        print("pozicije:", positions, "kombinacija:", combo, "lex_1:", rank)
        if lex_unrank_1(rank) != combo:
            raise RuntimeError("lex rank/unrank provera nije prosla")
    print()

    results, hit_counter = simulate_next_duplicate(unique_combos, RUNS, SEED, MODE)
    sorted_results = sorted(results)

    print("vremeplov mode:", MODE)
    print("runs:", RUNS)
    print("seed:", SEED)
    print("prosek koraka do sledeceg duplikata:", f"{mean(results):.10f}")
    print("medijana:", median(results))
    print("min:", sorted_results[0])
    print("p10:", percentile(sorted_results, 0.10))
    print("p25:", percentile(sorted_results, 0.25))
    print("p75:", percentile(sorted_results, 0.75))
    print("p90:", percentile(sorted_results, 0.90))
    print("max:", sorted_results[-1])
    print()

    print("top 10 pogodjenih istorijskih kombinacija u simulaciji:")
    for combo, count in hit_counter.most_common(10):
        print("count:", count, "lex_1:", lex_rank_1(combo), "kombinacija:", combo)
    print()


if __name__ == "__main__":
    main()



"""

izvlacenja: 4626
jedinstvenih kombinacija: 4625
duplih za brisanje: 1
ceo prostor C(39,7): 15380937
ocekivani duplikati do sada: 0.6955119184
stopa sledeceg hita u istorijski skup: 0.0003006969

postojeci duplikati:
pozicije: [2262, 4047] kombinacija: (8, 16, 19, 23, 29, 31, 37) lex_1: 12632941

vremeplov mode: history_only
runs: 10000
seed: 39
prosek koraka do sledeceg duplikata: 3369.9296000000
medijana: 2373.0
min: 2
p10: 344
p25: 971
p75: 4681
p90: 7673
max: 33534

top 10 pogodjenih istorijskih kombinacija u simulaciji:
count: 10 lex_1: 1764994 kombinacija: (1, 7, 12, 17, 18, 23, 39)
count: 9 lex_1: 1254492 kombinacija: (1, 5, 9, 12, 19, 26, 28)
count: 9 lex_1: 10621941 kombinacija: (6, 10, 20, 29, 30, 35, 39)
count: 9 lex_1: 248778 kombinacija: (1, 2, 8, 13, 15, 17, 36)
count: 8 lex_1: 6468686 kombinacija: (3, 10, 12, 17, 18, 20, 34)
count: 8 lex_1: 396671 kombinacija: (1, 2, 16, 19, 22, 29, 32)
count: 8 lex_1: 11410941 kombinacija: (7, 9, 21, 24, 25, 27, 37)
count: 8 lex_1: 4834583 kombinacija: (2, 13, 18, 29, 30, 35, 36)
count: 8 lex_1: 11022709 kombinacija: (6, 17, 21, 22, 23, 28, 35)
count: 8 lex_1: 3250433 kombinacija: (2, 4, 7, 16, 17, 25, 29)
"""






"""
Već duplirana kombinacija nema veću šansu za treći put — 
svih 4625 jedinstvenih su podjednako verovatne za sledeći duplikat. 
Simulator je ne preporučuje posebno.


Tačno za programski smisao: tih 10 su preporuke iz simulacije — 
kombinacije koje su u tom Monte Carlo izvršavanju najčešće pale kao sledeći duplikat.
Preciznije: 
nisu dokaz da će stvarno pasti, ali jesu rangirana preporuka modela/simulacije.


Po modelu (mehanizam koji je proizveo dosadašnji duplikat) 
predviđa sledeću next kombinaciju i daje rangiranu preporuku

Stopa za sledeći hit u istorijski skup je po 4625 jedinstvenih, 
ne po 4626 redova, jer duplikat ne širi skup kandidata.

Provera postojećeg duplikata 2262/4047, pa tek onda simulacija.
Provera je prošla: fajl vidi 4626 izvlačenja, 
4625 jedinstvenih i postojeći duplikat na 2262/4047 sa lex_1 12632941. 
Stopa u simulatoru je namerno po jedinstvenom istorijskom skupu: 4625 / 15380937.
stopa za sledeći hit u istorijski skup je po 4625 jedinstvenih, ne po 4626 redova, jer duplikat ne širi skup kandidata.

učita 4626 izvlačenja
potvrdi 4625 jedinstvenih
potvrdi duplikat [2262, 4047] za (8,16,19,23,29,31,37)
potvrdi lex_1 = 12632941
pokreće „vremeplov“ simulaciju za sledeći duplikat u istorijskom skupu


Za pun test:
RUNS=10000 python3 /Users/4c/Desktop/GHQ/data/vremeplov_duplikat_v2.py


v2 je Monte Carlo vremeplov: 
simulira buduća izvlačenja, pa mora da generiše slučajne 7/39 kombinacije dok ne pogodi već viđenu.

random.Random(seed) daje ponovljiv generator
rng.sample(range(1, 40), 7) pravi jednu simuliranu kombinaciju
"""




"""
2262 ---> 12,632,941                     
4047 ---> 12,632,941


račun za očekivane duplikate:

1. Duplikat je očekivana slučajnost, ne signal. 
4626 izvlačenja u prostoru od 15.380.937. 
Broj parova je: 
parovi: 4626·4625/2 = 10.697.625
10.697.625 / 15.380.937 ≈ 0.6955119184
Dakle teorija očekuje ~0.70 duplikata, a ima 1 — 
i dalje potpuno u skladu sa slučajnošću — nema „skrivene strukture“.


Iz 0.70 (očekivani broj duplikata kroz 4626 izvlačenja) može se izvući stopa.

Trenutna verovatnoća da baš sledeće izvlačenje napravi duplikat ≈ broj već izvučenih / ceo prostor:

4626 / 15.380.937 ≈ 0.0003 ≈ 1/3325

Znači očekivani sledeći duplikat je tek za ~3325 izvlačenja 
(i taj razmak se vremenom skraćuje kako lista raste, jer kumulativ ide kao t²/2N).

Drugim rečima: duplikati su retki, na razmaku od više hiljada izvlačenja. 
0.70 i kaže „za sad bi očekivao manje od jednog“, a desio se 1 — normalno.

To je odgovor na „kad sledeći“.



vremenska mašina: 
ne čekam 3300 stvarnih izvlačenja, 
nego pustim algoritam da „izvrti“ budućnost 
(Monte Carlo) i registruje prvi sledeći duplikat — 
koju kombinaciju ponovi i posle koliko simuliranih izvlačenja.

Učitam 4626 istorijskih u set (kao „viđene“).
Nastavim da izvlačim slučajne 7/39 kombinacije (nastavak istorije).
Čim padne kombinacija koja je već u setu → to je „sledeći duplikat“. 
Zabeležim: koja kombinacija, posle koliko koraka.
Ponovim run N puta → 
dobijem raspodelu: 
prosečno vreme do duplikata i koje se kombinacije ponavljaju.
Koja kombinacija će biti ponovljena ispada uniformno (svih 4625 podjednako verovatno), 
pa simulacija ne može da favorizuje jednu. 
Ono što realno dobijem je raspodela „posle koliko izvlačenja“ (waiting time) — 
i ona se lepo poklopi sa ~3300 proseka.


Precizno, na 10 decimala:
parovi: C(4626,2) = 10,697,625
prostor: C(39,7) = 15,380,937
očekivani broj duplikata = 0.6955119184
stopa po izvlačenju = 4626 / 15,380,937 = 0.0003007619
Dakle ne 0.70 zaokruženo, nego 0.6955119184.

Kod lex ranga je sve celobrojno i egzaktno, 
pa shift od 1 = susedna kombinacija, ne ista. 
Zato moram da zaključam konvenciju i držimo je svuda isto:
0-based rang {8,16,19,23,29,31,37} = 12,632,940
1-based = 12,632,941

rank/unrank, čistu celobrojna aritmetiku 
(bez float zaokruživanja) i jednu fiksnu konvenciju 
(1-based, pošto je moja numeracija u CSV-u sad 1-based) — 
pa da unrank(rank(komb)) == komb uvek vraća isto.



Cilj: 
predvideti sledeći duplikat preko simulacije (vremeplov), radeći u podskupu izvučenih, sa egzaktnim lex rank/unrank (1-based).

4626 izvlačenja, prostor C(39,7) = 15.380.937
očekivani duplikati do sad: 0.6955119184; stopa po izvlačenju 0.0003007619
sledeći duplikat = ponavljanje jedne od 4625 jedinstvenih izvučenih; 
prosek ~3300 izvlačenja unapred
brisanje duplikata = df.duplicated() (k−1 po grupi)

Koraci:
Učitam 4626 → set jedinstvenih (proverim da ih je 4625).
Lex rank/unrank (egzaktno, 1-based) — validacija unrank(rank(x))==x.
Simulator „vremeplov“: nastavak izvlačenja dok ne padne već viđena → beleži korak i kombinaciju; N runova → raspodela waiting-time.

rank(prva kombinacija) = 1, rank(poslednja) = 15,380,937
unrank(1) = {1,2,3,4,5,6,7}, unrank(15,380,937) = {33,34,35,36,37,38,39}
garancija: unrank(rank(x)) == x
"""
