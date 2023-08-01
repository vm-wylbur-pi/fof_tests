from dataclasses import dataclass
import math

@dataclass
class Point:
    x: int
    y: int

    def diff(self, p):
        return Vector(self.x - p.x, self.y - p.y)
    
    def distanceTo(self, p):
        return self.diff(p).magnitude()

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


# Run unit testes:
#  python3 geometry.py

import unittest

class TestPeripendicularVectorTo(unittest.TestCase):

    def test_horizontal_line(self):
        # The perpendicular vector from a horizontal line must be vertical, i.e. x compenent of 0
        horizontal_line = Line(Point(0,0), Vector(1, 0))
        self.assertEqual(horizontal_line.perpendicularVectorTo(Point(3,3)), Vector(0, 3) )
        self.assertEqual(horizontal_line.perpendicularVectorTo(Point(-5,-7)), Vector(0, -7) )
        self.assertEqual(horizontal_line.perpendicularVectorTo(Point(200,6)), Vector(0, 6) )

    def test_horizontal_line(self):
        # The perpendicular vector from a vertical line must be horizontal, i.e. y compenent of 0
        vertical_line = Line(Point(0, 0), Vector(0, 1))
        self.assertEqual(vertical_line.perpendicularVectorTo(Point(3,3)), Vector(3, 0) )
        self.assertEqual(vertical_line.perpendicularVectorTo(Point(-5,-7)), Vector(-5, 0) )
        self.assertEqual(vertical_line.perpendicularVectorTo(Point(200,6)), Vector(200, 0) )

    def test_diagonal_line(self):
        # Line x=y (sope 1)
        diagonal_slope_one = Line(Point(0,0), Vector(1, 1))
        vec_to_x_axis = diagonal_slope_one.perpendicularVectorTo(Point(6, 0))
        self.assertAlmostEqual(vec_to_x_axis.dx, 3)
        self.assertAlmostEqual(vec_to_x_axis.dy, -3)
        vec_to_y_axis = diagonal_slope_one.perpendicularVectorTo(Point(0, -2))
        self.assertAlmostEqual(vec_to_y_axis.dx, 1)
        self.assertAlmostEqual(vec_to_y_axis.dy, -1)


if __name__ == '__main__':
    unittest.main()
