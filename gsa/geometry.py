from dataclasses import dataclass
import math

@dataclass
class Point:
    x: int
    y: int

    def diff(self, p):
        return Vector(self.x - p.x, self.y - p.y)

@dataclass
class Vector:
    dx: int
    dy: int

    def sum(self, v):
        return Vector(self.dx + v.dx, self.dy + v.dy)

    def diff(self, v):
        return Vector(self.dx - v.dx, self.dy - v.dy)

    def norm(self):
        return self.scale(1/self.magnitude())

    # Whether v added self has a smaller magnitude than self, or roughly
    # whether v is pointing "against" (anywhere in the 180-degrees opposite)
    # the direction of self.
    def contraryTo(self, v):
        return self.sum(v).magnitude() < self.magnitude()

    def dot(self, v):
        return (self.dx * v.dx + self.dy * v.dy)

    def scale(self, s: float):
        return Vector(self.dx * s, self.dy * s)

    def magnitude(self):
        return math.sqrt(self.dx * self.dx + self.dy * self.dy)
    

# A line represented as a point + a unit vector
@dataclass
class Line:
    p: Point
    v: Vector

    def __init__(self, p: Point, v: Vector):
        self.p = p
        self.v = v.norm()

    def perpendicularVectorTo(self, p: Point) -> Vector:
        # https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Vector_formulation
        projection = p.diff(self.p)
        return projection.diff( self.v.scale(projection.dot(self.v))  )
        