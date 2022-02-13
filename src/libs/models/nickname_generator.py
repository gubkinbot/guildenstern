from random import choice
from os import path


def generate_nickname():
    res_dir = path.abspath(path.join(path.dirname(__file__), '..', '..', '..', '.resource'))
    with open(path.join(res_dir, 'adjectives.txt'), encoding='utf-8') as f:
        adjectives = f.readlines()
    with open(path.join(res_dir, 'nouns.txt'), encoding='utf-8') as f:
        nouns = f.readlines()

    return choice(adjectives).strip().capitalize() + ' ' + choice(nouns).strip().capitalize()
