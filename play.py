import random
from termcolor import cprint

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
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)[0][0]

def r2color(r):
    if r is None:
        return 'on_grey'
    if r is False:
        return 'on_yellow'
    if r is True:
        return 'on_green'
    raise("you got a bug in your code, dufus")

def printGuess(guess, resp):
    for i, c in enumerate(guess):
        cprint(c, 'white', r2color(resp[i]), end='')
    print()

def getResp(guess, master):
    # None is miss, False is wrong spot, True is right spot
    resp = [None,None,None,None,None]
    mastercpy = list(master)
    for i in range(5):
        if guess[i] == master[i]:
            resp[i] = True
            mastercpy.pop(i-(5-len(mastercpy)))
    for c in mastercpy:
        c_in_guess = -1
        for i in range(5):
            if resp[i] is not None:
                continue
            if guess[i] == c:
                c_in_guess = i
                break
        if c_in_guess >= 0:
            resp[c_in_guess] = False
    return resp


def playGame(words):
    master = random.choice(words)
    wordsLeft = set(words)

    guess = ''
    nguesses = 0
    resps = dict()

    while guess != master:
        guess = bestWord(wordsLeft)
        nguesses += 1
        resps[guess] = getResp(guess, master)
        printGuess(guess, resps[guess])
        words2rem = set()
        for word in wordsLeft:
            for guess, resp in resps.items():
                if getResp(guess, word) != resps[guess]:
                    words2rem.add(word)
        wordsLeft = wordsLeft - words2rem

    print(f"you got it! The word was {master}.")


def main():
    words = []
    with open("dict.txt", "r") as f:
        for w in f.readlines():
            words.append(w.strip())
    playGame(words)

if __name__ == "__main__":
    main()
