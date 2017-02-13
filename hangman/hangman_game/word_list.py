"""
Methods for building a word table, includes alternative options.

build_word_table is preferred.
It will populate the Word table in the database
with words from a file. This allows for
WordManager's random() method, which takes ~15ms.

generate_json_word_list was the original solution.
It took up to 200ms to get a random word.
Could see using this approach for a local app without a database.
"""
import random
import json
from .models import Word


def build_word_table(filename):
    """
    Build the Word table from a file.

    The file passed to build_word_table
    should contain one word and a newline character
    on each line.
    """
    with open(filename, 'r') as f:
        for line in f:
            word = line.strip('\n')
            Word.objects.create(word_text=word)

def get_random_json_word(filename):
    """
    Get a random word from a json-serialized python dictionary,
    as created by generate_word_list().
    """
    with open(filename, 'r') as f:
        word_list = json.load(f)
        random_int = random.randint(0, (len(word_list) - 1))
        return word_list[str(random_int)]

def generate_json_word_list(filename):
    """
    Create a new json file containing a dictionary representation
    of the word list.

    The file passed to generate_word_list
    should contain one word and a newline character
    on each line.

    A dictionary is used for 0(1) lookup.
    """
    word_list = dict()
    with open(filename, 'r') as f:
        for index, word in enumerate(f):
            word_list[index] = word.strip('\n')

    new_filename = filename.split('.')[0] + ".json"

    with open(new_filename, 'w') as f:
        json.dump(word_list, f)
