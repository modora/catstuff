# Source: https://en.wikipedia.org/wiki/Tf%E2%80%93idf

import collections
import math


def binary(term, doc):
    if term in doc:
        return 1
    else:
        return 0


def raw_count(term, doc):
    words = collections.Counter()
    words.update(doc)
    return words[term]


def term_freq(term, doc):
    return raw_count(term, doc)/len(doc)


def log_norm(term, doc, base=10):
    return 1 + math.log(raw_count(term, doc), base=base)


def double_norm(term, doc, K=0.5):
    assert 0 < K < 1
    words = collections.Counter()
    words.update(doc)

    K + (1-K) * words[term] / words.most_common(1)
