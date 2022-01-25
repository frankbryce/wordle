import math
import numpy as np
import random
from termcolor import cprint
from tqdm import tqdm

# STRATEGY = 'COMMON_CHAR'

STRATEGY = 'MIN_MASTER_LEFT'
MASTER_CNT_LOG_BASE = 24  # master count left -> expected turns

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
NUM_MASTERS = None
VERBOSE = False

def charcount(w):
    d = dict()
    for c in w:
        if c not in d:
            d[c] = 0
        d[c] += 1
    return d

def bestWord(words):
    if STRATEGY == 'COMMON_CHAR':
        chartot = dict()
        for c in ALPHABET:
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
    elif STRATEGY == 'MIN_MASTER_LEFT':
        min_rem = -1
        min_guess = None
        masters = words
        guesses = words
        for guess in guesses:
            expRem = 0
            resps = dict()
            for master in masters:
                resp = getResp(guess,master)
                if resp not in resps:
                    resps[resp] = set()
                resps[resp].add(master)
            for resp, masters in resps.items():
                expRem += len(masters) * math.log(len(masters), MASTER_CNT_LOG_BASE)
            if expRem < min_rem or min_rem == -1:
                max_rem = expRem
                min_guess = guess
        if not min_guess:
            raise("bug in your code, dummy")
        return min_guess
    else:
        raise(f"bad strategy {STRATEGY}")

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
    return tuple(resp)


def playGame(words, master=None):
    if not master:
        master = random.choice(words)
    wordsLeft = set(words)

    guess = ''
    nguesses = 0
    resps = dict()

    while guess != master:
        guess = bestWord(wordsLeft)
        nguesses += 1
        resp = getResp(guess, master)
        if VERBOSE:
            printGuess(guess, resp)
        words2rem = set()
        for word in wordsLeft:
            if getResp(guess, word) != resp:
                words2rem.add(word)
        wordsLeft = wordsLeft - words2rem

    if VERBOSE:
        print(f"you got it! The word was {master}.")
        input()
    return nguesses


def main():
    words = []
    with open("dict.txt", "r") as f:
        for w in f.readlines():
            words.append(w.strip())

    cnt = 0
    masters = words
    if NUM_MASTERS:
        masters = random.sample(words, NUM_MASTERS)
    for master in tqdm(masters):
        cnt += playGame(words, master)
    print(f"Average score over {len(masters)} runs: {cnt/len(masters):0.2f}")

if __name__ == "__main__":
    main()
