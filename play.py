from functools import lru_cache
import math
import numpy as np
import random
from termcolor import cprint
from tqdm import tqdm

# STRATEGY = 'COMMON_CHAR'
# FIRST_WORD = 'arose'  # hack to speed up search
STRATEGY = 'COMMON_CHAR_W_EXACT'
FIRST_WORD = 'rates'  # hack to speed up search

# COMMON_CHAR_W_EXACT params
IN_WORD_SCORE = 1
EXACT_MATCH_SCORE = 1.45

WORD_LIST = None  # to be set in main()
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
NUM_MASTERS = None
VERBOSE = False


@lru_cache(maxsize=3088)
def charcount(w):
    d = dict()
    for c in w:
        if c not in d:
            d[c] = 0
        d[c] += 1
    return d

def bestWord(wordsLeft):
    if len(wordsLeft) == len(WORD_LIST) and FIRST_WORD:
        return FIRST_WORD
    if STRATEGY == 'COMMON_CHAR':
        chartot = dict()
        for c in ALPHABET:
            chartot[c] = 0
        for w in wordsLeft:
            for c,_ in charcount(w).items():
                chartot[c] += 1
        scores = dict()
        for w in wordsLeft:
            scores[w] = 0
            for c,_ in charcount(w).items():
                scores[w] += chartot[c]
        return sorted(scores.items(), key=lambda item: item[1], reverse=True)[0][0]
    elif STRATEGY == 'COMMON_CHAR_W_EXACT':
        max_score = 0
        max_guess = None
        for guess in WORD_LIST:
            score = 0
            for master in wordsLeft:
                for r in getResp(guess, master):
                    if r is False:
                        score += IN_WORD_SCORE
                    if r is True:
                        score += EXACT_MATCH_SCORE
            if score > max_score:
                max_score = score
                max_guess = guess
        if not max_guess:
            raise("bug in your code, yyyyep")
        return max_guess
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

    global WORD_LIST
    WORD_LIST = words

    masters = words
    if NUM_MASTERS:
        masters = random.sample(words, NUM_MASTERS)
    cnt = 0
    for master in tqdm(masters):
        cnt += playGame(words, master)
    print(f"Average score over {len(masters)} runs: {cnt/len(masters):0.2f}")

if __name__ == "__main__":
    main()
