#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_file> <output_size_in_bytes> <output_file>"
    exit 1
fi

input_file="$1"
output_size="$2"
output_file="$3"

if [ ! -f "$input_file" ]; then
    echo "Error: Input file '$input_file' not found."
    exit 1
fi

if ! [[ "$output_size" =~ ^[0-9]+$ ]]; then
    echo "Error: Output size must be a positive integer."
    exit 1
fi

input_size=$(wc -c < "$input_file")

repetitions=$((output_size / input_size))
remainder=$((output_size % input_size))

# Create the output file
rm -f "$output_file"
touch "$output_file"

# Repeat the input file content
for ((i = 0; i < repetitions; i++)); do
    cat "$input_file" >> "$output_file"
done

# Append remaining bytes if needed
if [ "$remainder" -gt 0 ]; then
    head -c "$remainder" "$input_file" >> "$output_file"
fi

# Resize the output file to the exact input size
truncate -s "$output_size" "$output_file"

echo "Output file '$output_file' created with size $(wc -c < "$output_file") bytes."