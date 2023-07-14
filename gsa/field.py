import os.path
import random
import yaml

import geometry

# Representation of the rectangular field in which all the flowers are located.
# Used for deriving points like "center of the field", "edge of the field", etc.
class Field:
    def __init__(self, yaml_filename):
        yaml_file_path = os.path.join(os.path.dirname(__file__), yaml_filename)
        with open(yaml_file_path, 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)
            self.width = config['field']['x']
            self.height = config['field']['y']
        print(f"Read {self.width}x{self.height} field dimensions from {yaml_filename}")

    def center(self):
        return geometry.Point(self.width/2, self.height/2)
    
    def randomPoint(self):
        return geometry.Point(random.randint(0,self.width),
                              random.randint(0,self.height))
    
    def randomPointNearEdge(self):
        edge_width = 100
        candidate_xs = list(range(0, edge_width)) + list(range(self.width - edge_width, self.width))
        candidate_ys = list(range(0, edge_width)) + list(range(self.height - edge_width, self.height))
        return geometry.Point(random.choice(candidate_xs), random.choice(candidate_ys))