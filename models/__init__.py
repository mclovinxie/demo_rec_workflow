#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
@File       __init_.py.py
@Author     McLovin Xie
@Date       3/10/2022 11:38 AM
@Contact    mclovin.xxh@gmail.com
"""

import collections

from gensim.models import Word2Vec

from const import MODELS, WINDOW_SIZES

model_keys = [f'{m.lower()}_{w}' for m in MODELS for w in WINDOW_SIZES]

models = {k: Word2Vec.load(f'models/{k}') for k in model_keys}


precursor, successor = collections.defaultdict(lambda: collections.defaultdict(int)), collections.defaultdict(lambda: collections.defaultdict(int))
with open(f'data/dfs.txt', 'r', encoding='utf-8') as f:
    for line in f:
        content = line.replace('\n', '').split()
        for i, word_a in enumerate(content):
            for j, word_b in enumerate(content):
                if i == j:
                    continue
                if i < j:
                    precursor[word_b][word_a] += 1
                    successor[word_a][word_b] += 1
