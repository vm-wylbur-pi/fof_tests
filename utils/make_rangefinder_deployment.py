# Usage:
#   cd fof_tests
#   python3 utils/make_rangefinder_deployment.py server/config/inventory.csv > fake_field/playa_deployment.yaml

import csv
import sys
from dataclasses import dataclass

# Location of a flower in field coordinates, as measured by the range finder
# units is feet
@dataclass
class Point:
    quadrant: str #
    x: float
    y: float

@dataclass
class Offset:
    x: float
    y: float

# in feet.  Add before multiplying by 12
quadrant_offsets = {
    "A": Offset(0,0),
    "B": None,
    "C": None,
    "D": Offset(0,60.4),
}

flowers = {
    3:   Point("A", 9.1,  7.5),
    4:   Point("A", 20.4,  10.9),
    5:   Point("A", 30.0,  11.3),
    6:   Point("A", 37.1,  12.2),
    7:   Point("A", 46.15,  8.4),
    8:   Point("A", 42.6,  14.8),
    10:  Point("A", 33.7,  19.3),
    12:  Point("A", 25.9,  16.3),
    13:  Point("A", 18.2,  18.3),
    14:  Point("A", 9.2,  20.4),
    15:  Point("A", 22.2,  26.2),
    16:  Point("A", 28.0,  22.1),
    17:  Point("A", 36.7,  28.2),
    18:  Point("A", 38.5,  22.9),
    19:  Point("A", 44.2,  24.6),
    20:  Point("A", 43.8,  30.1),
    21:  Point("A", 47.9,  33.5),
    22:  Point("A", 44.2,  36.6),
    23:  Point("A", 32.8,  36.5),
    24:  Point("A", 27.0,  29.1),
    25:  Point("A", 22.2,  29.1),
    26:  Point("A", 13.8,  28.7),
    27:  Point("A", 21.5,  33.9),
    28:  Point("A", 12.35,  40.6),
    29:  Point("A", 15.2,  35.3),
    30:  Point("A", 20.2,  46.5),
    31:  Point("A", 29.2,  43.8),
    32:  Point("A", 37.7,  46.6),
    33:  Point("A", 42.5,  42.0),
    34:  Point("A", 44.7,  55.0),
    35:  Point("A", 47.5,  49.0),
    36:  Point("A", 35.5,  54.0),
    37:  Point("A", 23.8,  51.2),
    38:  Point("A", 31.3,  51.9),
    39:  Point("A", 30.6,  56.2),
    40:  Point("A", 11.8,  47.6),
    41:  Point("A", 15.8,  52.6),
    42:  Point("A", 8.9,  57.4),

    85: Point("D", 10.3, 2.7),
    86: Point("D", 17, 1.1),
    87: Point("D", 22.3, 0.6),
    88: Point("D", 28, 2.8),
    90: Point("D", 34.4, 1.8),
    91: Point("D", 40, 2.12),
    92: Point("D", 46.7, 0.8),
    93: Point("D", 9.7, 9.2),
    94: Point("D", 13.3, 7.4),
    95: Point("D", 20.8, 8.5),
    96: Point("D", 26.1, 6.2),
    97: Point("D", 32.3, 8.2),
    98: Point("D", 37.7, 7.6),
    99: Point("D", 44.2, 7.9),
    100: Point("D", 11.3, 15),
    101: Point("D", 23.7, 13.9),
    102: Point("D", 18.4, 13.6),
    103: Point("D", 30.6, 14.4),
    104: Point("D", 37.3, 13),
    105: Point("D", 46.7, 13.1),
    106: Point("D", 40.6, 12.5),
    107: Point("D", 9.6, 20.2),
    108: Point("D", 16.1, 18),
    109: Point("D", 22.8, 18.6),
    110: Point("D", 28.7, 17.8),
    111: Point("D", 35.4, 19.6),
    112: Point("D", 38.2, 19.2),
    113: Point("D", 42.0, 18.6),
    114: Point("D", 12.9, 25.1),
    115: Point("D", 19.3, 23.9),
    116: Point("D", 25.3, 23.7),
    117: Point("D", 28.2, 23.8),
    118: Point("D", 32.9, 24.0),
    119: Point("D", 37.6, 24.6),
    120: Point("D", 42.2, 25.6),
    121: Point("D", 14.5, 29.6),
    122: Point("D", 22.5, 30.8),
    123: Point("D", 25.3, 25.9),
    124: Point("D", 32.8, 30.5),
    125: Point("D", 37.3, 28.9),
    126: Point("D", 43.6, 31.3),

    133: Point("A", 62.2, 84.8),
    132: Point("A", 61, 79.1),
    131: Point("A", 65.4, 73),
    130: Point("A", 62.8, 70.4),
    129: Point("A", 60.5, 63.8),
    128: Point("A", 66.7, 56.1),
    127: Point("A", 65.5, 60.9),
    134: Point("A", 69.1, 83.5),
    135: Point("A", 71.4, 79.8),
    136: Point("A", 58.7, 46.8),
    137: Point("A", 71.8, 74.2),
    138: Point("A", 73.6, 69.9),
    139: Point("A", 70.3, 63.7),
    140: Point("A", 74.1, 57.3),
    141: Point("A", 76.7, 52.2),
    142: Point("A", 79, 59.2),
    143: Point("A", 80.7, 65.4),
    144: Point("A", 82.8, 73.1),
    145: Point("A", 82.6, 77.6),
    146: Point("A", 81.6, 82.1),
    147: Point("A", 84.6, 80.9),
    148: Point("A", 85.4, 75.2),
    149: Point("A", 85.7, 70),
    150: Point("A", 85.8, 63.6),
    151: Point("A", 83.7, 49.2),
    152: Point("A", 87.8, 58.9),
    153: Point("A", 88.9, 66.1),
    154: Point("A", 91, 70.2),
    155: Point("A", 89.6, 79),
    156: Point("A", 91.4, 82.6),
    157: Point("A", 91.6, 57.2),
    158: Point("A", 93.2, 60.9),
    159: Point("A", 78.3, 72.5),
    160: Point("A", 76.3, 79.1),
    161: Point("A", 88, 84.4),
    162: Point("A", 88.6, 56.2),
    43: Point("A", 51.6, 13.4),
    44: Point("A", 55, 12.8),
    45: Point("A", 63.2, 16.4),
    46: Point("A", 66.8, 12.2),
    47: Point("A", 72, 15.5),
    48: Point("A", 78.5, 12.5),
    49: Point("A", 83.8, 18.4),
    50: Point("A", 78.9, 22.4),
    51: Point("A", 73.4, 21.8),
    52: Point("A", 68.2, 24.7),
    53: Point("A", 62.7, 21.9),
    54: Point("A", 60.4, 23.8),
    55: Point("A", 51.4, 23.5),
    56: Point("A", 49.6, 28.2),
    57: Point("A", 54.2, 29.2),
    58: Point("A", 61.9, 30.2),
    59: Point("A", 66.4, 31.8),
    60: Point("A", 69.8, 31.8),
    61: Point("A", 73.3, 30.1),
    62: Point("A", 78.5, 34),
    63: Point("A", 80.7, 33.4),
    64: Point("A", 80.2, 35.8),
    65: Point("A", 72.4, 40.8),
    67: Point("A", 66.7, 39),
    68: Point("A", 61.2, 40.1),
    69: Point("A", 55.5, 37.8),
    70: Point("A", 52.8, 40.6),
    71: Point("A", 53.2, 48),
    72: Point("A", 60.6, 46.8),
    73: Point("A", 65.1, 45.6),
    74: Point("A", 71.8, 46.5),
    75: Point("A", 77.3, 43.7),
    77: Point("A", 83.3, 46.3),
    78: Point("A", 80.9, 53),
    80: Point("A", 74.9, 56.8),
    81: Point("A", 68.9, 52.5),
    82: Point("A", 61.4, 55.4),
    83: Point("A", 57.7, 57.9),
    84: Point("A", 48.7, 59.7),
}

if len(sys.argv) != 2:
    print("Requires one argument specifying the inventory CSV file.")
csv_file_path = sys.argv[1]

with open(csv_file_path, 'r') as csv_file:
    data = csv.DictReader(csv_file)
    # Key the inventory by sequence number, since that's how the grid is defined above.
    # The keys and all fields in each record are string-typed.
    inventory = {rec['sequence']: rec for rec in list(data)}

print('name: "Burning Man Deployment"')
print('description: "The real thing, made 2023-08-25"')
print('field:')
print('  x: 1150')
print('  y: 1000')
print('  corners:')
print('    - [284, 568]')
print('    - [326, 109]')
print('    - [891, 98]')
print('    - [1121, 550]')
print('flowers:')

for flower_num, point in flowers.items():
    info = inventory.get(str(flower_num), None)
    if info:
        offset = quadrant_offsets[point.quadrant]
        x_inches = int(round(12 * (point.x + offset.x)))
        y_inches = int(round(12 * (point.y + offset.y)))
        print('  "%s": { id:  %3s,   x: %3s,   y: %3s }' %
                (info['mac'], info['sequence'], x_inches, y_inches)
             )
    else:
        print(f"No inventory entry for flower {flower_num}")




# We decided not to measure distances to the corners, for simplicity.

# Measurements from each of the corners to a flower. None means unknown
# @dataclass
# class Measurements:
#     dA: float = None  # Distance to corner A (0,0), far left seen from solar panels
#     dB: float = None  # Distance to corner B (w,0), far right seen from solar panels
#     dC: float = None  # Distance to corner C (w,h), near left seen from solar panels
#     dD: float = None  # Distance to corner D (0,h), near right seen from solar panels


# def calculateFlowerPosition(m: Measurements):
#     pass

# # Known by walking around the grid and writing down the number of each flower.
# flowers = {
#     1: Measurements(dA=500, dB=600, dC=800, dD=100),
#     2: Measurements(dA=400, dB=500, dC=700, dD=200),
#     3: Measurements(dA=300, dB=400, dC=900, dD=800),
# }
