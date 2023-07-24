import os
import csv
import sys
from PIL import Image

STARTDIR = '/Users/george/Downloads/FOF-Test.v1-initial-test-wtf-am-i-doing.tensorflow'  # Replace with the actual path to the STARTDIR directory

def process_annotations(directory, writer):
    input_file = os.path.join(directory, '_annotations.csv')
    dir_name = os.path.basename(os.path.normpath(directory))

    if dir_name == 'valid':
        upper_dir_name = 'VALIDATION'
    else:
        upper_dir_name = dir_name.upper()

    known_dims = False
    width = -1
    height = -1

    with open(input_file, 'r') as csv_in:
        reader = csv.reader(csv_in)
        next(reader)

        for row in reader:
            if len(row) == 0:
                break

            if not known_dims:
                fname = row[0]
                fpath = os.path.join(STARTDIR,dir_name,fname)
                with Image.open(fpath) as img:
                    width = img.width
                    height = img.height
            image_name = row[0]
            xmin = str(int(row[4]) / width)
            ymin = str(int(row[5]) / height)
            xmax = str(int(row[6]) / width)
            ymax = str(int(row[7]) / height)
            row = [upper_dir_name, os.path.join(dir_name, image_name)] + [row[3],xmin,xmax] + ['',''] + [ymin,ymax] + ['', '']
            writer.writerow(row)

def main():
    output_file = os.path.join(STARTDIR,'tf-convert.csv')
    csv_out = open(output_file, 'w', newline='')
    writer = csv.writer(csv_out)

    for subdir in ['train', 'valid', 'test']:
        subdirectory = os.path.join(STARTDIR, subdir)
        if os.path.isdir(subdirectory):
            process_annotations(subdirectory, writer)

if __name__ == "__main__":
    main()
