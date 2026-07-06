import math

class Costmap():
    def __init__(self):
        self.obs_layer = self.Obslayer()
        self.infla_layer = self.Inflalayer()

    class Obslayer():
        def __init__(self):
            self.obs_map = {}

        def do_obs_layer(self, car_x, car_y, obs_x, obs_y):
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

                if self.obs_map.get((curr_x, curr_y)) == 1:
                    removed_obs.append((curr_x,curr_y))
                
                self.obs_map[(curr_x, curr_y)] = 0
                modified_points.append(((curr_x, curr_y), 0))
                current_dist += step

            # Obstacle point
            obs_floor_x = math.floor(obs_x)
            obs_floor_y = math.floor(obs_y)
            self.obs_map[(obs_floor_x, obs_floor_y)] = 1
            modified_points.append(((obs_floor_x, obs_floor_y), 1))
            
            return modified_points, removed_obs

    class Inflalayer():
        def __init__(self):
            self.infla_map = {}

        def do_infla_layer(self, obs_points, infla_radius):

            infla_area = []

            for pt in obs_points:
                if pt is None or not isinstance(pt, (tuple, list)) or len(pt) < 2:
                    continue
                
                x, y = pt

                for dx in range(-infla_radius, infla_radius + 1):
                    for dy in range(-infla_radius, infla_radius + 1):
                        fx = x + dx
                        fy = y + dy
                        distance = math.sqrt(dx**2 + dy**2)
                    
                        if distance > infla_radius:
                            continue
                        cost = 1

                        self.infla_map[(fx, fy)] = cost
                        infla_area.append(((fx, fy), cost))

            return infla_area

    def total_obs_points(self, infla_radius, change_points, removed_obs, total_obs_points):
        if change_points:     
            for (ox,oy),state in change_points:
                if state == 1:  
                    total_obs_points.append((ox, oy))
            
        if removed_obs:
            for rx, ry in removed_obs:
                
                # rmove cost
                for dx in range(-infla_radius, infla_radius + 1):
                    for dy in range(-infla_radius, infla_radius + 1):
                        target_key = (rx + dx, ry + dy)
                        if target_key in self.infla_layer.infla_map:
                            del self.infla_layer.infla_map[target_key]

                #rebiuld exist obs infla layer
                search_r = 2 * infla_radius
                
                for nx in range(-search_r, search_r + 1):
                    for ny in range(-search_r, search_r + 1):
                        neighbor_pt = (rx + nx, ry + ny)
                        if self.obs_layer.obs_map.get(neighbor_pt) == 1:
                            total_obs_points.append(neighbor_pt)
