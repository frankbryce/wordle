from functools import lru_cache
import heapq
import math
import numpy as np
import random
from termcolor import cprint
from tqdm import tqdm

# STRATEGY = 'COMMON_CHAR'
# STRATEGY = 'COMMON_CHAR_W_EXACT'
# STRATEGY = 'RANDOM'
# STRATEGY = 'MONTE_CARLO'
STRATEGY = 'MIN_LEFT'
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
NUM_MASTERS = 5
VERBOSE = True


class WordBag:
    def __init__(self, words=[]):
        self.bag = set(words)
        self.charCount = dict()
        for c in ALPHABET:
            self.charCount[c] = 0
        for w in self.bag:
            for c in w:
                self.charCount[c] += 1

    def add(self, word):
        if word not in self.bag:
            self.bag.add(word)
            for c in word:
                self.charCount[c] += 1
        return self.bag

    def rem(self, word):
        if word in self.bag:
            self.bag.remove(word)
            for c in word:
                self.charCount[c] -= 1
        return self.bag

    def get(self):
        return self.bag

    def minus(self, other):
        ret = WordBag(self.bag)
        for o in other.bag:
            ret.rem(o)
        return ret

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
    if len(wordsLeft.bag) == 0:
        raise("bug in your code")
    if len(wordsLeft.bag) <= 2:
        return list(wordsLeft.bag)[:n]
    if len(wordsLeft.bag) == NUM_WORDS and FIRST_WORD:
        return [FIRST_WORD]
    if strategy == 'RANDOM':
        return random.choices(list(wordsLeft.bag), k=n)
    if strategy == 'COMMON_CHAR':
        chartot = dict()
        for c in ALPHABET:
            chartot[c] = 0
        for w in wordsLeft.bag:
            for c,_ in charcount(w).items():
                chartot[c] += 1
        scores = []
        for i,w in enumerate(guessWords.bag):
            scores[i] = 0
            for c,_ in charcount(w).items():
                scores[i] += chartot[c]
        best = heapq.nlargest(n, enumerate(wordsLeft.bag), key=lambda i: scores[i[0]])
        return [x[1] for x in best]
    elif strategy == 'COMMON_CHAR_W_EXACT':
        scores = []
        for guess in guessWords.bag:
            score = 0
            for master in wordsLeft.bag:
                for r in getResp(guess, master):
                    if r is 1:
                        score += IN_WORD_SCORE
                    if r is 2:
                        score += EXACT_MATCH_SCORE
            scores.append((score, master))
        best = heapq.nlargest(n, enumerate(wordsLeft.bag), key=lambda i: scores[i[0]])
        return [x[1] for x in best]
    elif STRATEGY == 'MIN_LEFT':
        rm = []
        for guess in tqdm(guessWords.bag):
            rm.append(0)
            for master in wordsLeft.bag:
                resp = getResp(guess, master)
                for word in wordsLeft.bag:
                    if getResp(guess, word) != resp:
                        rm[-1] += 1
        best = heapq.nlargest(n, enumerate(wordsLeft.bag), key=lambda i: rm[i[0]])
        return [x[1] for x in best]
    elif STRATEGY == 'MONTE_CARLO':
        if n > 1:
            raise('MONTE_CARLO does not support n > 1')
        if len(wordsLeft.bag) > MONTE_CARLO_LT:
            return bestWords(wordsLeft, MONTE_CARLO_STRATEGY, guessWords)

        bestSoFar = 1_000_000_000 # way too big
        bestGuess = None
        for guess in bestWords(wordsLeft, MONTE_CARLO_STRATEGY, guessWords, n=MONTE_CARLO_TOP_N):
            nGuesses = 0
            for master in random.sample(list(wordsLeft.bag), min(len(wordsLeft.bag), MONTE_CARLO_SIM_COUNT)):
                resp = getResp(guess, master)
                words2rem = WordBag()
                for word in wordsLeft.bag:
                    if getResp(guess, word) != resp:
                        words2rem.add(word)
                left = wordsLeft.minus(words2rem)
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
        guessWords.rem(guess)
        return
    if GUESS_REMOVE_STRATEGY == 'WORDS_LEFT':
        for w in list(guessWords.bag):
            if w not in wordsLeft.bag:
                guessWords.rem(w)
        return
    if GUESS_REMOVE_STRATEGY == 'NO_MATCH':
        for w in list(guessWords.bag):
            matches = False
            for c in w:
                if guessWords.charCount[c] > 0:
                    matches = True
                    break
            if not matches:
                guessWords.rem(w)
        return
    raise("invalid GUESS_REMOVE_STRATEGY")

def r2color(r):
    if r is 0:
        return 'on_grey'
    if r is 1:
        return 'on_yellow'
    if r is 2:
        return 'on_green'
    raise("you got a bug in your code, dufus")

def printGuess(guess, resp):
    for i, c in enumerate(guess):
        cprint(c, 'white', r2color(resp[i]), end='')
    print()

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


def playGame(wordsLeft, strategy, master, allWords, verbose=VERBOSE):
    guessWords = allWords
    guess = ''
    nguesses = 0

    while guess != master:
        guess = bestWord(wordsLeft, strategy, guessWords)
        nguesses += 1
        resp = getResp(guess, master)
        for word in list(wordsLeft.bag):
            if getResp(guess, word) != resp:
                wordsLeft.rem(word)
        refineGuessWords(guess, wordsLeft, guessWords)
        if verbose:
            print(master, len(wordsLeft.bag), 'guess=', sep=', ')
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
        cnt += playGame(WordBag(words), STRATEGY, master, allWords=WordBag(words))
    print(f"Average score over {len(masters)} runs: {cnt/len(masters):0.2f}")

if __name__ == "__main__":
    main()
