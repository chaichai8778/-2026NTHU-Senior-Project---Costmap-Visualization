import math

def obs_pos(distance, angle_degrees):
    angle_radians = math.radians(angle_degrees)

    x = distance * math.cos(angle_radians)
    y = distance * math.sin(angle_radians)

    return x, y

#output cm,degree
def car_position(car_x, car_y, car_theta, deltaSL, deltaSR):
    delta_s = (deltaSL + deltaSR) * 50
    delta_theta = (deltaSL - deltaSR) / 0.195
    
    car_x += delta_s * math.cos(math.radians(car_theta) + delta_theta / 2.0)
    car_y += delta_s * math.sin(math.radians(car_theta) + delta_theta / 2.0)

    car_theta += math.degrees(delta_theta)
    if car_theta > 180 :
       car_theta -=360
    if car_theta < -180:
       car_theta +=360

    return car_x, car_y, car_theta