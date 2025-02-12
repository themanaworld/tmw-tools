#!/usr/bin/env python3
import sys
import zlib

def adler32(file):
    with open(file, 'rb') as f:
        checksum = zlib.adler32(f.read())
    return f'{checksum:08x}'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file1> [file2] [file3] ...")
        sys.exit(1)

    for filename in sys.argv[1:]:
        try:
            print(adler32(filename))
        except IOError as e:
            print(f"Error: Could not read file '{filename}' - {e}")
            sys.exit(1)
