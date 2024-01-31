input_string = "lossless compression"
delimiter = '$'


def rotate(data, n):
    return data[n:] + data[:n]


"""
TRANSFORM
"""


def get_rotations(data):
    """ Generates a list of all possible rotations of a string
    :param data: Input string
    :return: List of string
    """
    output = []
    for i in range(len(data)):
        output.append(rotate(data, i))
    return output


def get_code(rotations):
    """ Returns the BWT code of a given list of rotations
    :param rotations:
    :return:
    """
    result = ""
    for s in rotations:
        if len(s) > 0:
            result += s[-1]
    return result


def bwt_transform(data):
    data = data + delimiter
    rotations = get_rotations(data)
    rotations.sort()
    return get_code(rotations)


"""
INVERSE
"""


def generate_first_column(data):
    """
    Generate the first column based on the last column.
    """
    return ''.join(sorted(data))


def get_occurrences(data):
    """ Gives the occurrence count of each char in a string.

    :param data:
    :return: Array with corresponding occurrence
    """
    count_dict = {}
    result_array = []

    for item in data:
        if item in count_dict:
            count_dict[item] += 1
        else:
            count_dict[item] = 0
        result_array.append(count_dict[item])

    return result_array


def follow_mapping(first_column, last_column):
    """

    :param first_column: Sorted first column
    :param last_column:
    :return:
    """
    c = get_occurrences(last_column)

    output = ''
    index = 0
    for i in range(len(first_column)):
        char_last = last_column[index]
        output = char_last + output
        index = first_column.find(char_last) + c[index]
    return output


def fix_rotations(data):
    dollar_index = data.find(delimiter)
    if dollar_index != -1:
        return data[dollar_index + 1:] + data[:dollar_index + 1]
    else:
        return data


def bwt_inverse(data):
    first_column = generate_first_column(data)
    rotated_result = follow_mapping(first_column, data)
    return fix_rotations(rotated_result).replace(delimiter, "")


bwt_transformed = bwt_transform(input_string)

print(bwt_transformed)

print(bwt_inverse(bwt_transformed))
