#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
@File       cmd.py
@Author     McLovin Xie
@Date       3/10/2022 11:47 AM
@Contact    mclovin.xxh@gmail.com
"""

import click

from const import MODELS, WINDOW_SIZES


@click.command()
@click.option('-m', '--model', type=click.Choice(MODELS, case_sensitive=False), required=True)
@click.option('-w', '--window', type=click.Choice([str(w) for w in WINDOW_SIZES]), required=True)
def train(model, window):
    model, window = model.lower(), int(window)
    from gensim.models import Word2Vec
    sentences = []
    with open(f'data/{model}.txt', 'r') as f:
        for line in f:
            sentences.append(line.replace('\n', '').split())
    the_model = Word2Vec(sentences=sentences, window=window, vector_size=50, min_count=1, epochs=200, sg=1, workers=10)
    the_model.save(f'models/{model}_{window}')


if __name__ == '__main__':
    train()
