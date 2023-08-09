# Usage:
#   cd fof_tests
#   python3 utils/make_regular_grid_deployment_file.py server/config/inventory.csv > fake_field/dress_rehearsal_deployment.yaml

EDGE_PADDING = 50
ROW_INTERVAL = 6 * 12   # inches
COL_INTERVAL = 6 * 12   # inches

import csv
import sys

# Known by walking around the grid and writing down the number of each flower.
flowers = [
  [ 135,   0,   0,   0,   0, 158, 152,   0,   0,   0,   0,   0,   0,   0 ],
  [ 160, 162, 153, 155, 159, 156, 141, 116, 104,  90, 111,  95, 103, 123 ],
  [ 146, 139, 134, 154, 122, 142, 143,  85,  70,  98,  92,  87,  82,  94 ],
  [ 147, 138, 140, 144, 137, 128, 132, 109, 105, 112, 115, 118,  86,  91 ],
  [ 149, 136, 145, 129, 131, 121, 161, 110,  96, 106, 102,  97, 127, 117 ],
  [ 126, 133, 151, 130, 150, 148, 157, 114,  93,  83,  84,  88,  89, 119 ],
  [   0,   0,   0,   0,   0,   0,  17,   0,   0,   0,   0,   0,   0,   0 ],
  [   0,  27,  24,  20,   5,  37,  19,  50,  68,  62,  75,  59,  80,  41 ],
  [  14,  26,  28,  31,   6,  34,  32,  65,  73,  56,  63,  61,  58,  49 ],
  [  15,  40,  16,  13,   3,  29,  38,  78,  46,  48,  66,  74,  64,  55 ],
  [  12,   8,  10,  18,   4,  36,  22,  57,  44,  43,  47,  54,  67,  72 ],
  [  25,   7,  21,  33,  23,  35,  30,  77,  52,  60,  42,  51,  45,  53 ],
]

if len(sys.argv) != 2:
    print("Requires one argument specifying the inventory CSV file.")
csv_file_path = sys.argv[1]

with open(csv_file_path, 'r') as csv_file:
    data = csv.DictReader(csv_file)
    # Key the inventory by sequence number, since that's how the grid is defined above.
    # The keys and all fields in each record are string-typed.
    inventory = {rec['sequence']: rec for rec in list(data)}

print('name: "Dress Rehearsal at Treasure Island"')
print('description: "Grid with 6-foot spacing"')
print('field:')
print('  x: 1000')
print('  y: 1000')
print('flowers:')

seen_flowers = set()

for row_num, row in enumerate(flowers):
    for col_num, flower_seq_num in enumerate(row):
        if not flower_seq_num:
            # Skip gaps in the grid, marked as zeros.
            continue
        if flower_seq_num in seen_flowers:
            print(f"WARNING: Saw flower {flower_seq_num} again")
        seen_flowers.add(flower_seq_num)
        y_coord = EDGE_PADDING + row_num * ROW_INTERVAL
        x_coord = EDGE_PADDING + col_num * COL_INTERVAL
        info = inventory.get(str(flower_seq_num), None)
        if info:
            print('  "%s": { id:  %3s,   x: %3s,   y: %3s }' %
                  (info['mac'], info['sequence'], x_coord, y_coord))
        else:
            print(f"No inventory entry for flower {flower_seq_num}")
