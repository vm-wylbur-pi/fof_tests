from dataclasses import dataclass
import math

@dataclass
class HSVAColor:
    hue: int
    sat: int = 0
    val: int = 100
    alpha: int = 255

# Utility functions for transforming and mixing colors.

# Halfway around the color wheel
def oppositeHue(hue: int) -> int:
    return (hue + 128) % 255

def averageHue(hues: 'list[int]') -> int:
    # Treat each hue as a point on the hue circle, where 
    # theta=0 is hue=0 and theta=2pi is hue=255.  Find the
    # 2D average of these points on the plane, then project
    # that average back to the hue circle.
    if not hues:
        return None
    total_x, total_y = 0, 0
    for hue in hues:
        assert 0 <= hue <= 255
        theta = math.tau * hue/255
        x, y = math.cos(theta), math.sin(theta)
        total_x += x
        total_y += y
    avg_x = total_x / len(hues)
    avg_y = total_y / len(hues)
    avg_theta = math.atan2(avg_y, avg_x)
    # atan2 returns a value between -pi and pi.
    # To map back to [0-255] I want one in the range 0-2pi
    if avg_theta < 0:
        avg_theta += math.tau
    avg_hue = 255 * avg_theta / math.tau
    assert 0 <= avg_hue <= 255
    return int(round(avg_hue))


def distantFromSetofHues(hues: 'list[int]') -> int:
	# We want an output hue that looks as *different* as possible from all
    # the inputs. The common case is two inputs (two waves or two blobs
    # intersecting). in that case, we find the average of the input hues 
    # (clamped to [0-255]), then get the hue opposite it on the hue wheel
    # (clamped to [0-255])
    return oppositeHue(averageHue(hues))


# Unit tests
assert oppositeHue(0) == 128
assert oppositeHue(240) == 113
assert averageHue([]) is None
assert averageHue([30, 40]) == 35
assert averageHue([250, 15]) == 5  # Average around the zero-point correctly
assert averageHue([10, 20, 30]) == 20  # Average of >2 colors
assert averageHue([245, 250, 15, 20]) == 5  # Average around the zero point with > 2 colors
