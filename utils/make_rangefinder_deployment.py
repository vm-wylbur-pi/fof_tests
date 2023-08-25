# Usage:
#   cd fof_tests
#   python3 utils/make_rangefinder_deployment.py server/config/inventory.csv > fake_field/playa_deployment.yaml

import csv
import sys
from dataclasses import dataclass

# Location of a flower in field coordinates, as measured by the range finder
@dataclass
class Point:
    x: float
    y: float

flowers = {
    1: Point(x=300, y=500),
    2: Point(x=100, y=1100),
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
        print('  "%s": { id:  %3s,   x: %3s,   y: %3s }' %
                (info['mac'], info['sequence'], 
                 int(round(point.x)), int(round(point.y))
                 )
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
