#! python3
#
# Sample usage:
#   cd fof_tests
#   utils/test_flower_mac_hash_functions.py server/config/inventory.csv

from collections import Counter
import csv
import sys

if len(sys.argv) != 2:
    print("Requires one argument specifying the inventory CSV file.")
csv_file_path = sys.argv[1]

def readFlowerMacAddressIDs():
    with open(csv_file_path, 'r') as csv_file:
        macs = [rec['mac'] for rec in csv.DictReader(csv_file)]
        print(f"Read {len(macs)} from {csv_file_path} (example: {macs[0]})")
        return macs

# Includes the colon, e.g. 'F0:5F:EC'
macStrings = readFlowerMacAddressIDs()

def asBytes(macStr):
    # Turn it into a sequence of bytes. This should be easy on the flower.
    return bytes(macStr.encode("utf8"))

# Interpret each character as a byte, then add them up
def byteSum(macStr):
    return sum(asBytes(macStr))

def byteProduct(macStr):
    result = 23
    for b in asBytes(macStr):
        result *= b+1
    return result

# https://en.wikipedia.org/wiki/Hash_function#Mid-squares
def midSquares(macStr):
    byte_sum = byteSum(macStr)
    square = byte_sum * byte_sum
    square_str = str(byte_sum * byte_sum)
    index = len(square_str) // 3
    mid = square_str[index:index*2]
    return int(mid)

# https://en.wikipedia.org/wiki/Hash_function#Character_folding
def charFolding(macStr):
    somePrime = 59
    total = 0
    for b in asBytes(macStr):
        total = total * somePrime + b
    return total

# All hash function should take a mac address string and return an integer.
hashFunctions = [
    byteSum,
    byteProduct,
    midSquares,
    charFolding,
]


for hashFunction in hashFunctions:
    print("Testing", hashFunction.__name__)
    hashes = list([hashFunction(macString) for macString in macStrings])
    for divisor in (2,3,4):
        mods = [hash % divisor for hash in hashes]
        mod_distribution = Counter(mods)
        print(f'  %{divisor}: {mod_distribution.values()}')
        
