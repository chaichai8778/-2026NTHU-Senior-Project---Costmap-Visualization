import math

def obs_layer(car_x, car_y, obs_x, obs_y, obs_map):
    dx = obs_x - car_x
    dy = obs_y - car_y
    distance = math.sqrt(dx**2 + dy**2)

    if distance == 0:
        return [], None, []
    
    modified_points = []
    removed_obs = []

    ux = dx / distance
    uy = dy / distance
    
    step = 0.5
    current_dist = 0.0

    # Space point
    while current_dist < distance - 0.2: 
        curr_x = math.floor(car_x + ux * current_dist)
        curr_y = math.floor(car_y + uy * current_dist)

        if obs_map.get((curr_x, curr_y)) == 1:
            removed_obs.append((curr_x,curr_y))
        
        obs_map[(curr_x, curr_y)] = 0
        modified_points.append(((curr_x, curr_y), 0))
        current_dist += step

    # Obstacle point
    obs_floor_x = math.floor(obs_x)
    obs_floor_y = math.floor(obs_y)
    obs_map[(obs_floor_x, obs_floor_y)] = 1
    modified_points.append(((obs_floor_x, obs_floor_y), 1))
    
    return modified_points, (obs_floor_x, obs_floor_y), removed_obs

def inflation_layer(obs_points, inflation_radius, inflation_map):

    inflation_area = []

    for pt in obs_points:
        if pt is None or not isinstance(pt, (tuple, list)) or len(pt) < 2:
            continue
        
        x, y = pt

        for dx in range(-inflation_radius, inflation_radius + 1):
            for dy in range(-inflation_radius, inflation_radius + 1):
                fx = x + dx
                fy = y + dy
                distance = math.sqrt(dx**2 + dy**2)
            
                if distance > inflation_radius:
                    continue
                cost = int(255 * (1.0 - (distance / inflation_radius)))

                current_cost = inflation_map.get((fx, fy), 0)
                if cost > current_cost:
                    inflation_map[(fx, fy)] = cost
                    inflation_area.append(((fx, fy), cost))

    return inflation_area

def remove_infation(removed_obs, inflation_radius, inflation_map):
    if removed_obs:
        for rx, ry in removed_obs:
            for dx in range(-inflation_radius, inflation_radius + 1):
                for dy in range(-inflation_radius, inflation_radius + 1):
                    target_key = (rx + dx, ry + dy)
                    if target_key in inflation_map:
                        del inflation_map[target_key]

