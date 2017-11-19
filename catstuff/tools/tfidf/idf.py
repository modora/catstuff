# SRC: https://en.wikipedia.org/wiki/Tf%E2%80%93idf

import collections
import math


def _doc_freq(term, docs):
    """ Calculates the number of documents a term appears in"""
    doc_freq = 0
    for doc in docs:
        if term in doc:
            doc_freq += 1
    return doc_freq

def _full_doc_freq(docs):
    """ Calculates the number of documents all terms appear in"""
    doc_terms = collections.Counter()  # number of documents in which a term occurs in
    for doc in docs:
        doc_terms.update(set(doc))
    return doc_terms


def unary(term, docs):
    return 1


def idf(term, docs, base=10, K=1):
    # K is a divide-by-zero adjustment term
    doc_freq = _doc_freq(term, docs)
    return math.log(len(docs) / (doc_freq + K), base=base)


def idf_smooth(term, docs, base=10, K=1):
    doc_freq = _doc_freq(term, docs)
    return math.log(1 + len(docs) / (doc_freq + K), base=base)


def idf_max(term, docs, base=10):
    doc_terms = _full_doc_freq(docs)
    return math.log(doc_terms.most_common(1) / (1 + doc_terms[term]), base=base)


def idf_prob(term, docs, base=10, K=1):
    doc_freq = _doc_freq(term, docs)
    return math.log((len(docs) - doc_freq) / (doc_freq + K), base=base)
