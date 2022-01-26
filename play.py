from functools import lru_cache
import heapq
import math
import numpy as np
import random
from termcolor import cprint
from tqdm import tqdm

# STRATEGY = 'COMMON_CHAR'
STRATEGY = 'COMMON_CHAR_W_EXACT'
# STRATEGY = 'RANDOM'
# STRATEGY = 'MONTE_CARLO'
FIRST_WORD = 'rates'  # hack to speed up search

# GUESS_REMOVE_STRATEGY = 'REMOVE_GUESS'  # only remove the last guess
# GUESS_REMOVE_STRATEGY = 'WORDS_LEFT'  # only keep possible words left
GUESS_REMOVE_STRATEGY = 'NO_MATCH'  # remove words with no characters in words left

# COMMON_CHAR_W_EXACT params
IN_WORD_SCORE = 1
EXACT_MATCH_SCORE = 1.45

# MONTE_CARLO params
MONTE_CARLO_LT = 20        # do monte carlo when there's <= 20 words.
MONTE_CARLO_TOP_N = 20     # only simulate the top N guesses from guessList
MONTE_CARLO_SIM_COUNT = 5  # do simulations on up to this many master words
MONTE_CARLO_STRATEGY = 'COMMON_CHAR_W_EXACT' # heuristic for simulations

NUM_WORDS = None  # to be set by main()
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
NUM_MASTERS = None
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
    return bestWords(wordsLeft, strategy, guessWords)[0]

def bestWords(wordsLeft, strategy, guessWords, n=1):
    if len(wordsLeft) == 0:
        raise("bug in your code")
    if len(wordsLeft) <= 2:
        return list(wordsLeft)[:n]
    if len(wordsLeft) == NUM_WORDS and FIRST_WORD:
        return [FIRST_WORD]
    if strategy == 'RANDOM':
        return random.choices(list(wordsLeft), k=n)
    if strategy == 'COMMON_CHAR':
        chartot = dict()
        for c in ALPHABET:
            chartot[c] = 0
        for w in wordsLeft:
            for c,_ in charcount(w).items():
                chartot[c] += 1
        scores = []
        for i,w in enumerate(guessWords):
            scores[i] = 0
            for c,_ in charcount(w).items():
                scores[i] += chartot[c]
        best = heapq.nlargest(n, enumerate(wordsLeft), key=lambda i: scores[i[0]])
        return [x[1] for x in best]
    elif strategy == 'COMMON_CHAR_W_EXACT':
        scores = []
        for guess in guessWords:
            score = 0
            for master in wordsLeft:
                for r in getResp(guess, master):
                    if r is False:
                        score += IN_WORD_SCORE
                    if r is True:
                        score += EXACT_MATCH_SCORE
            scores.append((score, master))
        best = heapq.nlargest(n, enumerate(wordsLeft), key=lambda i: scores[i[0]])
        return [x[1] for x in best]
    elif STRATEGY == 'MONTE_CARLO':
        if n > 1:
            raise('MONTE_CARLO does not support n > 1')
        if len(wordsLeft) > MONTE_CARLO_LT:
            return bestWords(wordsLeft, MONTE_CARLO_STRATEGY, guessWords)

        bestSoFar = 1_000_000_000 # way too big
        bestGuess = None
        for guess in bestWords(wordsLeft, MONTE_CARLO_STRATEGY, guessWords, n=MONTE_CARLO_TOP_N):
            nGuesses = 0
            for master in random.sample(list(wordsLeft), min(len(wordsLeft), MONTE_CARLO_SIM_COUNT)):
                resp = getResp(guess, master)
                words2rem = set()
                for word in wordsLeft:
                    if getResp(guess, word) != resp:
                        words2rem.add(word)
                left = wordsLeft - words2rem
                nGuesses += playGame(left, MONTE_CARLO_STRATEGY, master, left, verbose=False)
                if nGuesses > bestSoFar:
                    break
            if nGuesses < bestSoFar:
                bestSoFar = nGuesses
                bestGuess = guess
        if not bestGuess:
            raise(f"bug {bestGuess}")
        return [bestGuess]
    else:
        raise(f"bad strategy {STRATEGY}")

def refineGuessWords(guess, wordsLeft, guessWords):
    if GUESS_REMOVE_STRATEGY == 'REMOVE_GUESS':
        guessWords.remove(guess)
        return
    if GUESS_REMOVE_STRATEGY == 'WORDS_LEFT':
        for w in list(guessWords):
            if w not in wordsLeft:
                guessWords.remove(w)
        return
    if GUESS_REMOVE_STRATEGY == 'NO_MATCH':
        charsLeft = set()
        for w in wordsLeft:
            for c in w:
                charsLeft.add(c)
        for w in list(guessWords):
            matches = False
            for c in charsLeft:
                matches = True
                break
            if not matches:
                guessWords.remove(w)
        return
    raise("invalid GUESS_REMOVE_STRATEGY")

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
        refineGuessWords(guess, wordsLeft, guessWords)
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
        random.seed(42)  # make hermetic
        masters = random.sample(words, NUM_MASTERS)
    cnt = 0
    for master in tqdm(masters):
        cnt += playGame(set(words), STRATEGY, master, allWords=frozenset(words))
    print(f"Average score over {len(masters)} runs: {cnt/len(masters):0.2f}")

if __name__ == "__main__":
    main()
