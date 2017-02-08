"""
Original, rejected solution.
This takes up to two tenths of a second to get a random word.
Could see using this approach for a local app without a database.
"""
import random
import json

def get_random_word(filename):
    """
    Get a random word from a json-serialized python dictionary,
    as created by generate_word_list().
    """
    with open(filename, 'r') as f:
        word_list = json.load(f)
        random_int = random.randint(0, (len(word_list) - 1))
        return word_list[str(random_int)]

def generate_word_list(filename):
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
