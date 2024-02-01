import string

input_string = "sn lrss$oocilmpssseeo"
common_dictionary = "abcdefghijklmnopqrstuvwxyz $"


def mtf_transform(plain_text: str) -> list[int]:
    dictionary = common_dictionary
    compressed_text = []
    rank = 0

    for c in plain_text:
        rank = dictionary.find(c)
        compressed_text.append(rank)

        dictionary = dictionary.replace(c, '', 1)
        dictionary = c + dictionary

    return compressed_text


print(mtf_transform(input_string))
