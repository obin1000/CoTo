
input_string = "lossless compression"

in_file = "../data/silesia.tar.lz4"


def decompress(data):
    with open(in_file, "rb") as file:
        print(file.read(5).hex())




print(decompress(input_string))

