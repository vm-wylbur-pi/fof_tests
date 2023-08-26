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
    x: float
    y: float

flowers = {
    3:  Point(x=9.1, y=7.5),
    4:  Point(x=20.4, y=10.9),
    5:  Point(x=30.0, y=11.3),
    6:  Point(x=37.1, y=12.2),
    7:  Point(x=46.15, y=8.4),
    8:  Point(x=42.6, y=14.8),
    10:  Point(x=33.7, y=19.3),
    12:  Point(x=25.9, y=16.3),
    13:  Point(x=18.2, y=18.3),
    14:  Point(x=9.2, y=20.4),
    15:  Point(x=22.2, y=26.2),
    16:  Point(x=28.0, y=22.1),
    17:  Point(x=36.7, y=28.2),
    18:  Point(x=38.5, y=22.9),
    19:  Point(x=44.2, y=24.6),
    20:  Point(x=43.8, y=30.1),
    21:  Point(x=47.9, y=33.5),
    22:  Point(x=44.2, y=36.6),
    23:  Point(x=32.8, y=36.5),
    24:  Point(x=27.0, y=29.1),
    25:  Point(x=23.8, y=28.8),
    26:  Point(x=13.8, y=28.7),
    27:  Point(x=21.5, y=33.9),
    28:  Point(x=12.35, y=40.6),
    29:  Point(x=15.2, y=35.3),
    30:  Point(x=20.2, y=46.5),
    31:  Point(x=29.2, y=43.8),
    32:  Point(x=37.7, y=46.6),
    33:  Point(x=42.5, y=42.0),
    34:  Point(x=44.7, y=55.0),
    35:  Point(x=47.5, y=49.0),
    36:  Point(x=35.5, y=54.0),
    37:  Point(x=23.8, y=51.2),
    38:  Point(x=31.3, y=51.9),
    39:  Point(x=30.6, y=56.2),
    40:  Point(x=11.8, y=47.6),
    41:  Point(x=15.8, y=52.6),
    42:  Point(x=8.9, y=57.4),
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
print('  y: 1250')
print('flowers:')

for flower_num, point in flowers.items():
    info = inventory.get(str(flower_num), None)
    if info:
        x_inches = int(round(12 * point.x))
        y_inches = int(round(12 * point.y))
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
