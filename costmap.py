import math

def obstacle_layer(car_x, car_y, obs_x, obs_y, obstacle_map):
    dx = obs_x - car_x
    dy = obs_y - car_y
    distance = math.sqrt(dx**2 + dy**2)
    
    if distance == 0:
        return
        
    ux = dx / distance
    uy = dy / distance
    
    step = 0.5
    current_dist = 0.0
    while current_dist < distance - 0.2: 
        curr_x = car_x + ux * current_dist
        curr_y = car_y + uy * current_dist
        
        obstacle_map[(math.floor(curr_x), math.floor(curr_y))] = 0
        current_dist += step

    obstacle_map[(math.floor(obs_x), math.floor(obs_y))] = 1

def inflation_layer(obstacle_map, inflation_radius):
    inflated_map = {}
    for (x, y), value in obstacle_map.items():
        if value != 1:
            continue

        for dx in range(-inflation_radius, inflation_radius + 1):
            for dy in range(-inflation_radius, inflation_radius + 1):
                fx = x + dx
                fy = y + dy
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > inflation_radius:
                    continue

                cost = int(255 * (1.0 - (distance / inflation_radius)))

                if (fx, fy) in inflated_map:
                    inflated_map[(fx, fy)] = max(inflated_map[(fx, fy)], cost)
                else:
                    inflated_map[(fx, fy)] = cost

    return inflated_map