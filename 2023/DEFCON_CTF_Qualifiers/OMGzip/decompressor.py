#!/usr/bin/env python3

import sys
from dataclasses import dataclass

# Binary Tree Class
@dataclass
class BinaryTree:
    data: int
    right: "BinaryTree" = None
    left: "BinaryTree" = None
    parent: "BinaryTree" = None

class Omgzip:
    def __init__(self):
        self.dictionary = {}
        self.index = 0
        self.tree = self._setup_tree()

    def _setup_tree(self):
        tree = self._create_tree(0, None)

        block1 = self.dictionary[0]

        block2 = BinaryTree(block1.data)
        block2.parent = block1
        block2.right = None
        block2.left = None

        block4 = BinaryTree(None)
        block4.parent = block1
        block4.right = None
        block4.left = None

        block1.right = block2
        block1.left = block4

        self.dictionary[0] = block2
        self.dictionary[None] = block4

        return tree

    # create a binary tree of depth 8, then populate the dictionary with all 256 child nodes at depth 8
    def _create_tree(self, depth, parent_block):
        if depth > 8:
            # It's over 8
            return None

        tree = BinaryTree(None)
        tree.parent = parent_block
        tree.right = self._create_tree(depth + 1, tree)
        tree.left = self._create_tree(depth + 1, tree)

        if depth == 8:
            tree.data = self.index
            self.dictionary[self.index] = tree
            self.index += 1

        return tree

    # Scrambles the tree
    def _scrambler(self, x):
        while True:
            y = x.parent

            if x.parent is None or y.parent is None:
                break

            z = y.parent
            w = z.right

            if w == y:
                w = z.left
                z.left = x
            else:
                z.right = x

            if x == y.right:
                y.right = w
            else:
                y.left = w

            x.parent = z
            w.parent = y
            x = z

    # Encodes bytes by traversing the tree from the bottom up
    def _travesty(self, data, output: list):
        stack = []

        if data not in self.dictionary:
            raise ValueError("Lost data:" + str(data))

        block = self.dictionary[data]
        current = block.parent
        prev = block

        while current is not None:
            if current.left == prev:
                stack.append(1)
            else:
                stack.append(0)
            prev = current
            current = current.parent

        while stack:
            output.append(stack.pop())

        self._scrambler(block)

    # Decodes bytes by traversing the tree from the top down
    def _tribute(self, data: list, index):
        current = self.tree
        output = b""

        while index < len(data):
            prev = current
            if data[index] == 1:
                current = current.left
            else:
                current = current.right
            if current == None:
                break
            index += 1
        if index < len(data) and prev.data is not None:
            output = prev.data.to_bytes(1, 'big')

        self._scrambler(prev)
        return output, index

    # Encode a bitstream
    def encode(self, stream: bytes):
        output = []

        # Encodes one byte at a time, output is a bitstream
        for item in stream:
            self._travesty(item, output)
        self._travesty(None, output)

        # Converts the bits of output into bytes
        return bytes(int(''.join(map(str, output[i:i+8])), 2) for i in range(0, len(output), 8))
    
    # Decode a bitstream
    def decode(self, stream: bytes):
        bitstream = []
        for byte in stream:
            bitstream.extend([int(bit) for bit in f"{byte:08b}"])
        
        output = b""
        index = 0
        while index < len(bitstream):
            newbyte, index = self._tribute(bitstream, index)
            output += newbyte
            if len(output) % 80000 == 0:
                print(f"Serving bit {index} out of {len(bitstream)}")

        return output

def uncompress_part1(input_data: bytes) -> bytes:

    decoded = bytearray()

    i = 0
    while i < len(input_data):
        c = input_data[i]
        i += 1
        if c == 0xff:
            count = input_data[i]
            i += 1
            if count == 0xff:
                decoded.extend([c])                                         # single 0xff byte
            else:
                c = input_data[i]
                i += 1
                if c == 0xff:
                    decoded.extend([c for num in range(int(count) + 2)])    # 2+ 0xff bytes
                else:
                    decoded.extend([c for num in range(int(count) + 3)])    # 3+ bytes
        else:
            decoded.append(c)                                               # single byte

    return decoded


def main():
    """
    Main function when being run as a script.
    """
    # Ensure correct usage
    if len(sys.argv) <= 1:
        print(f"Usage: {sys.argv[0]} <filename>")
        sys.exit(1)

    # Parse command-line argument
    input_name = sys.argv[1]

    # Open and read input file
    try:
        with open(input_name, "rb") as input_file:
            input_data = input_file.read()
    except IOError:
        print(f"Could not open input file {input_name} for reading")
        sys.exit(1)

    # Decompress input data
    assert(input_data[:6] == b"OMGZIP")
    stripped_data = input_data[6:]
    dcode = Omgzip()
    decoded_data = dcode.decode(stripped_data)
    output_data = uncompress_part1(decoded_data)
    output_name = input_name.replace(".omgzip", "")
    if output_data is None:
        print("An unknown error occurred")
        sys.exit(1)

    # Write compressed data to output file
    try:
        with open(output_name, "wb") as output_file:
            output_file.write(output_data)
    except IOError:
        print(f"Could not open output file {output_name} for writing")
        sys.exit(1)


if __name__ == "__main__":
    main()
