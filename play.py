from functools import lru_cache
import math
import numpy as np
import random
from termcolor import cprint
from tqdm import tqdm

# STRATEGY = 'COMMON_CHAR'
# STRATEGY = 'COMMON_CHAR_W_EXACT'
# STRATEGY = 'RANDOM'
# FIRST_WORD = 'rates'  # hack to speed up search
STRATEGY = 'MONTE_CARLO'
FIRST_WORD = 'stead'  # hack to speed up search

# COMMON_CHAR_W_EXACT params
IN_WORD_SCORE = 1
EXACT_MATCH_SCORE = 1.45

# MONTE_CARLO params
MONTE_CARLO_SIM_COUNT = 10
MONTE_CARLO_STRATEGY = 'COMMON_CHAR'

NUM_WORDS = None  # to be set by main()
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
NUM_MASTERS = 500
VERBOSE = False


@lru_cache(maxsize=4096)
def charcount(w):
    d = dict()
    for c in w:
        if c not in d:
            d[c] = 0
        d[c] += 1
    return d

def bestWord(wordsLeft, strategy, guessWords):
    if len(wordsLeft) == 0:
        raise("bug in your code")
    if len(wordsLeft) <= 2:
        return next(iter(wordsLeft))
    if len(wordsLeft) == NUM_WORDS and FIRST_WORD:
        return FIRST_WORD
    if strategy == 'RANDOM':
        return random.choice(list(wordsLeft))
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
    elif STRATEGY == 'MONTE_CARLO':
        bestSoFar = 1_000_000_000 # way too big
        bestGuess = None
        for guess in guessWords:
            nGuesses = 0
            for master in random.sample(list(wordsLeft), min(len(wordsLeft), MONTE_CARLO_SIM_COUNT)):
                resp = getResp(guess, master)
                words2rem = set()
                for word in wordsLeft:
                    if getResp(guess, word) != resp:
                        words2rem.add(word)
                left = wordsLeft - words2rem
                nGuesses += playGame(left, MONTE_CARLO_STRATEGY, master, left, verbose=False)
                if nGuesses > bestSoFar * MONTE_CARLO_SIM_COUNT:
                    break
            if nGuesses < bestSoFar:
                bestSoFar = nGuesses
                bestGuess = guess
        if not bestGuess:
            raise(f"bug {bestGuess}")
        return bestGuess
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

@lru_cache(maxsize=65536)
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


def playGame(wordsLeft, strategy, master, allWords=None, verbose=VERBOSE):
    guessWords = set(allWords)

    guess = ''
    nguesses = 0

    while guess != master:
        guess = bestWord(wordsLeft, strategy, guessWords)
        nguesses += 1
        resp = getResp(guess, master)
        for word in list(wordsLeft):
            if getResp(guess, word) != resp:
                wordsLeft.remove(word)
        missingChars = set(guess[i] for i in range(5) if resp[i] is None)
        for word in list(guessWords):
            for c in missingChars:
                if c in word:
                    guessWords.remove(word)
                    break
        if verbose:
            print(master, len(wordsLeft), 'guess=', sep=', ')
            printGuess(guess, resp)

    if verbose:
        input()
    return nguesses


def main():
    words = []
    with open("dict.txt", "r") as f:
        for w in f.readlines():
            words.append(w.strip())

    global NUM_WORDS
    NUM_WORDS = len(words)

    masters = words
    if NUM_MASTERS:
        masters = random.sample(words, NUM_MASTERS)
    cnt = 0
    for master in tqdm(masters):
        cnt += playGame(set(words), STRATEGY, master, allWords=frozenset(words))
    print(f"Average score over {len(masters)} runs: {cnt/len(masters):0.2f}")

if __name__ == "__main__":
    main()
