"""
Store data as (offset, length) tuples
"""
input_string = "testtesttestestesttest"

window_size = 5

"""
COMPRESS
"""


def find_longest_match(history, forward):
    """ Finds the longest match of forward in history
    """
    longest_match = 0
    longest_offset = 0

    for progress_iterator in range(len(history)):
        current_match = 0
        for match_iterator in range(len(forward)):
            search_index = progress_iterator + match_iterator
            if search_index < len(history):
                if forward[match_iterator] == history[search_index]:
                    current_match += 1
                else:
                    break
        if current_match > longest_match:
            longest_match = current_match
            longest_offset = progress_iterator

    return longest_match, longest_offset


def compress(data):
    compressed_data = []
    history = ""

    i = 0
    while i < len(data):
        lookahead = data[i:i + window_size]

        match_length, offset = find_longest_match(history, lookahead)
        if match_length > 0:
            offset = len(history) - offset

        if match_length < len(lookahead):
            compressed_data.append((offset, match_length, lookahead[match_length]))
        else:
            compressed_data.append((offset, match_length-1, lookahead[match_length-1]))
        history += lookahead[:match_length+1]
        history = history[-window_size:]
        i += match_length + 1

    return compressed_data


"""
DECOMPRESS
"""

# TODO

print(compress(input_string))
