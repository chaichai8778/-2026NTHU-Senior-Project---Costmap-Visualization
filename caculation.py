import math

def obstacle_position(distance, angle_degrees):
    angle_radians = math.radians(angle_degrees)

    x = distance * math.cos(angle_radians)
    y = distance * math.sin(angle_radians)

    return x, y