from functools import lru_cache
import math
import numpy as np
import random
from termcolor import cprint
from tqdm import tqdm

STRATEGY = 'COMMON_CHAR'
FIRST_WORD = 'arose'  # hack to speed up search
# STRATEGY = 'COMMON_CHAR_W_EXACT'
# FIRST_WORD = 'rates'  # hack to speed up search
# STRATEGY = 'HIGHEST_MATCH'
# FIRST_WORD = 'eases'  # hack to speed up search

# COMMON_CHAR_W_EXACT params
IN_WORD_SCORE = 1
EXACT_MATCH_SCORE = 1.45

# MONTE_CARLO params
MONTE_CARLO_SIM_COUNT = 10_000

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

def bestWord(wordsLeft, all_words, strategy):
    if len(wordsLeft) == len(all_words) and FIRST_WORD:
        return FIRST_WORD
    if strategy == 'COMMON_CHAR':
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
    elif strategy == 'COMMON_CHAR_W_EXACT':
        max_score = 0
        max_guess = None
        for guess in wordsLeft:
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
    elif strategy == 'HIGHEST_MATCH':
        cscore = dict()
        for c in ALPHABET:
            cscore[c] = [0,0,0,0,0]
        for master in wordsLeft:
            for i in range(5):
                for j in range(5):
                    add = 1
                    if i == j:
                        add = EXACT_MATCH_SCORE
                    cscore[master[i]][j] += add
        max_score = 0
        max_guess = None
        for guess in wordsLeft:
            score = 0
            for i in range(5):
                score += cscore[guess[i]][i]
            if score > max_score:
                max_score = score
                max_guess = guess
        if not max_guess:
            raise('BUG')
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


def playGame(words, strategy, master=None, all_words=None):
    if not master:
        master = random.choice(words)
    if not all_words:
        all_words=frozenset(words)
    wordsLeft = set(words)

    guess = ''
    nguesses = 0

    while guess != master:
        guess = bestWord(wordsLeft, all_words, strategy)
        nguesses += 1
        resp = getResp(guess, master)
        for word in list(wordsLeft):
            if getResp(guess, word) != resp:
                wordsLeft.remove(word)
        if VERBOSE:
            print(master, len(wordsLeft), sep=', ', end=', guess=')
            printGuess(guess, resp)

    if VERBOSE:
        input()
    return nguesses


def main():
    words = []
    with open("dict.txt", "r") as f:
        for w in f.readlines():
            words.append(w.strip())

    masters = words
    if NUM_MASTERS:
        masters = random.sample(words, NUM_MASTERS)
    cnt = 0
    for master in tqdm(masters):
        cnt += playGame(words, STRATEGY, master=master, all_words=frozenset(words))
    print(f"Average score over {len(masters)} runs: {cnt/len(masters):0.2f}")

if __name__ == "__main__":
    main()
