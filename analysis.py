import numpy as np
from tqdm import tqdm

def charcount(w):
    d = dict()
    for c in w:
        if c not in d:
            d[c] = 0
        d[c] += 1
    return d

def onehot(n):
    ret = np.array([0,0,0,0,0])
    ret[n-1] = 1
    return ret

def main():
    # dictionary will be
    # {char: [#words with 1 char, # words with 2 of this char, # of words with 3 of this char...]}
    chardict = dict()
    chartot = dict()
    totwords = 0
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for c in alphabet:
        chardict[c] = np.array([0,0,0,0,0])
        chartot[c] = 0
    words = []
    with open("dict.txt", "r") as f:
        for w in tqdm(f.readlines()):
            totwords += 1
            w = w.strip()  # trailing \n for some reason
            words.append(w)
            d = charcount(w)
            for c in d:
                chardict[c] += onehot(d[c])
                chartot[c] += 1

    scores = dict()
    for w in words:
        scores[w] = 0
        for c,cnt in charcount(w).items():
            scores[w] += chartot[c]

    for c in alphabet:
        printstr = f'# {c} words: {chartot[c]:04}: '
        for n in range(4):
            printstr += f'{n+1} {c} words: {chardict[c][n]:04} | '
        print(printstr)

    print([(w, score) for w, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)][:10])



if __name__ == "__main__":
    main()
