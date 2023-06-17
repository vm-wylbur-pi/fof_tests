#! python3
#
# This tool reads the CSV-format flower inventory, then prints it out
# as lines that can be copied into multicore/src/flower_info.cpp in
# the definition of the FlowerInventory constant.
#
# Sample usage:
#   cd fof_tests
#   tools/convert_flower_inventory_to_cpp.py server/config/inventory.csv

import csv
import sys

if len(sys.argv) != 2:
    print("Requires one argument specifying the inventory CSV file.")
csv_file_path = sys.argv[1]

def validate_data(records):
    data = list(records)
    expected_fields = ("sequence", "mac", "type", "height")
    if not all(field in records.fieldnames for field in expected_fields):
        print("CSV file was missing an expected field.")
        sys.exit()
    # These strings are used in a C++ enum definition, so they must match exactly.
    expected_flower_types = ('geranium', 'aster', 'poppy')
    for rec in data:
        if rec['type'] not in expected_flower_types:
            print(f"unexpected flower type '{rec['type']}', must be one of {expected_flower_types}")
            sys.exit()
        # Some flowers in the inventory don't have a height value, but we need to
        # have something that is C++ - parseable as a float.  Use -1 as a sentinel
        # value meaning "unknown."
        if not rec['height']:
            rec['height'] = "-1"
        try:
            int(rec['sequence'])
            float(rec['height'])
        except ValueError:
            print(f"Unparseable number in record: {rec}")
            sys.exit()

    return data

with open(csv_file_path, 'r') as csv_file:
    data = csv.DictReader(csv_file)
    inventory = validate_data(data)

    print(f"// This definition was gerated by {sys.argv[0]}")
    print("std::map<String, flower_info::FlowerInfo> FlowerInventory = {")
    for rec in inventory:
        print('  { "%s",  {%s, "%s", %s, %s}  },' % 
                (rec['mac'], rec['sequence'], rec['mac'], rec['type'], rec['height']))
    print("};")
