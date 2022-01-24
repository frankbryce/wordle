alphabet = 'abcdefghijklmnopqrstuvwxyz'

def charcount(w):
    d = dict()
    for c in w:
        if c not in d:
            d[c] = 0
        d[c] += 1
    return d

def bestWord(words):
    chartot = dict()
    for c in alphabet:
        chartot[c] = 0
    for w in words:
        for c,_ in charcount(w).items():
            chartot[c] += 1
    scores = dict()
    for w in words:
        scores[w] = 0
        for c,_ in charcount(w).items():
            scores[w] += chartot[c]
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)[0]

def main():
    words = []
    with open("dict.txt", "r") as f:
        for w in f.readlines():
            words.append(w.strip())
    print(bestWord(words))

if __name__ == "__main__":
    main()
