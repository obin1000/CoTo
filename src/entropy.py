import math
from collections import Counter

input_string = "lossless compression"

base = 2


def entropy(data):
    """ The Shannon entropy of a string
    """
    counter = Counter(data)
    entropy = 0
    for char in counter:
        p = float(counter[char]) / len(data)
        logp = math.log(p, base)
        entropy += p*logp
    return -entropy


def entropy_ideal(length):
    "Calculates the ideal Shannon entropy of a string with given length"

    prob = 1.0 / length

    return -1.0 * length * prob * math.log(prob) / math.log(2.0)

print(entropy(input_string))