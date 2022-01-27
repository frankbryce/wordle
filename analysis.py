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


def getResp(guess, master):
    # 0 is miss, 1 is wrong spot, 2 is right spot
    resp = [0,0,0,0,0]
    mastercpy = list(master)
    for i in range(5):
        if guess[i] == master[i]:
            resp[i] = 2
            mastercpy.pop(i-(5-len(mastercpy)))
    for c in mastercpy:
        c_in_guess = -1
        for i in range(5):
            if resp[i] != 0:
                continue
            if guess[i] == c:
                c_in_guess = i
                break
        if c_in_guess >= 0:
            resp[c_in_guess] = 1
    return tuple(resp)

def main2():
    words = []
    with open("dict.txt", "r") as f:
        for w in f.readlines():
            w = w.strip()  # trailing \n for some reason
            words.append(w)

    rdict = dict()
    for w1 in tqdm(words):
        for w2 in words:
            r = getResp(w1, w2)
            if r not in rdict:
                rdict[r] = set()
            rdict[r].add((w1,w2))

    for r, t in sorted(rdict.items(), key=lambda item: len(item[1])):
        print(r, len(t), sep=':')
    print(len(rdict))

if __name__ == "__main__":
    main()
    main2()
