import pygame
import sys
import serial
import time
import costmap, planner, caculation, draw

pygame.init()

# Arduino Serial Port 
COM_PORT = 'COM5'  
input_array = []
input_trigger = False
BAUD_RATE = 115200
obstacle_history = []
car_theta = 0
car_x = 0
car_y = 0


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
GRID_SIZE = 4
SENSOR_OFFSET = 11.5 #cm
inflation_radius = 6  

# color
COLOR_CROSSHAIR = (0, 150, 255, 100) # 準星藍色 (帶有一點透明度)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pygame 4-Quadrant Gridmap (Float Coordinates)")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 12)
font_bold = pygame.font.SysFont("arial", 14, bold=True)

CENTER_X = WINDOW_WIDTH // 2
CENTER_Y = WINDOW_HEIGHT // 2

base_map = draw.grid_map(screen, GRID_SIZE)

obstacle_map = {}  
inflation_map = {}
goal_grid = (15, 15) 
path_cells = []      
counter = 0
obstacle_map_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
inflated_map_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"成功連結 {COM_PORT}")
    running = True
    time.sleep(2) 

    while running:
        map_changed = False
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONUP:
                last_grid_pos = None
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2: 
                    mx, my = pygame.mouse.get_pos()
                    goal_grid = caculation.pixel_to_world(CENTER_X, CENTER_Y, mx, my, GRID_SIZE)
                    map_changed = True

        tt_obs_points = [] 
        while ser.in_waiting > 0:
            print("in")
            raw_data = ser.readline()
            try:
                data_string = raw_data.decode('utf-8', errors='ignore').strip()
                
                if data_string: 
                    
                    input_array = data_string.split(",")

                    if len(input_array) >= 3:
                        val_str1 = input_array[0].strip()
                        val_str2 = input_array[1].strip()
                        val_str3 = input_array[-1].strip()
                        
                        
                        # if val_str1 and val_str2 are not empty, convert to float
                        if val_str1 and val_str2 and val_str3:
                            try:
                                val_str1 = val_str1.replace('\r', '').strip()
                                obstacle_distance = float(val_str1)+SENSOR_OFFSET
                            except ValueError:
                                print(f"error obstacle_distance: {val_str1}")
                                obstacle_distance = 0.0
                                
                            try:
                                val_str2 = val_str2.replace('\r', '').strip()
                                deltaSL = float(val_str2)
                            except ValueError:
                                print(f"error deltaSL: {val_str2}")
                                deltaSL = 0.0

                            try:
                                val_str3 = val_str3.replace('\r', '').strip()
                                deltaSR = float(val_str3)
                            except ValueError:
                                print(f"error deltaSR: {val_str3}")
                                deltaSR = 0.0  

                            car_x, car_y, car_theta = caculation.car_position(car_x, car_y, car_theta, deltaSL, deltaSR)
                            rel_obs_x, rel_obs_y = caculation.obs_pos(obstacle_distance, car_theta)
                            
                            obs_x = int(car_x) + int(rel_obs_x)
                            obs_y = int(car_y) + int(rel_obs_y)

                            # realtime obstacle
                            px, py = caculation.world_to_pixel(CENTER_X, CENTER_Y, obs_x, obs_y, GRID_SIZE)
                            obstacle_history.append((px, py))
                            
                            # obstacle layer visualization
                            change_points, new_obs_point, removed_obs = costmap.obs_layer(car_x, car_y, obs_x, obs_y, obstacle_map)

                            if removed_obs is not None:     
                                for (ox,oy),state in change_points:
                                    if state == 1:  
                                        tt_obs_points.append((ox, oy))
                                        pygame.draw.circle(obstacle_map_surface, (0, 0, 255), (CENTER_X+ox*GRID_SIZE, CENTER_Y-oy*GRID_SIZE), 4)
                                    elif state == 0:  
                                        pygame.draw.circle(obstacle_map_surface, (0, 255, 0), (CENTER_X+ox*GRID_SIZE, CENTER_Y-oy*GRID_SIZE), 4)
                                    else:
                                        continue
                                
                                if removed_obs:
                                    inflation_map_needs_update = True 
                                    for rx, ry in removed_obs:
                                        
                                        # rmove cost
                                        for dx in range(-inflation_radius, inflation_radius + 1):
                                            for dy in range(-inflation_radius, inflation_radius + 1):
                                                target_key = (rx + dx, ry + dy)
                                                if target_key in inflation_map:
                                                    del inflation_map[target_key]

                                        rect_x, rect_y = caculation.world_to_pixel(CENTER_X, CENTER_Y, rx-inflation_radius, ry + inflation_radius + 1, GRID_SIZE)
                                        rect_size = (2 * inflation_radius + 1) * GRID_SIZE
                                        inflated_map_surface.fill((0, 0, 0, 0), (rect_x, rect_y, rect_size, rect_size))

                                        #rebiuld exist obs inflation layer
                                        search_r = 2 * inflation_radius
                                        
                                        for nx in range(-search_r, search_r + 1):
                                            for ny in range(-search_r, search_r + 1):
                                                neighbor_pt = (rx + nx, ry + ny)
                                                if obstacle_map.get(neighbor_pt) == 1:
                                                    tt_obs_points.append(neighbor_pt)

                                if tt_obs_points:
                                    unique_obs_points = list(set(tt_obs_points))
                                    # inflation layer visualization
                                    for (fx, fy), cost in costmap.inflation_layer(unique_obs_points, inflation_radius, inflation_map):
                                        rect_x, rect_y = caculation.world_to_pixel(CENTER_X, CENTER_Y, fx, fy + 1, GRID_SIZE)
                                        pygame.draw.rect(inflated_map_surface, (255, 0, 0, 100), (rect_x, rect_y, GRID_SIZE, GRID_SIZE))
                                

                            if len(obstacle_history) > 500:
                                obstacle_history.pop(0)
            except UnicodeDecodeError:
                pass
            print("out")

        if map_changed or 'prev_map_state' not in locals():
            print("in")
            start_tuple = (int(car_x), int(car_y))
            goal_tuple = (int(goal_grid[0]), int(goal_grid[1]))
            path_cells = planner.astar(start_tuple, goal_tuple, inflation_map)
            print("out")
            prev_map_state = True

        #base map

        screen.fill(base_map.COLOR[0])  # Fill the background with the base color
        base_map.draw_grid(screen)


        #screen.blit(obstacle_map_surface, (0, 0))
        screen.blit(inflated_map_surface, (0, 0))

        """
        for px, py in obstacle_history:
            pygame.draw.circle(screen, (255, 0, 0), (px, py), 5)
        """

        #car position
        car_pixel_x, car_pixel_y = caculation.world_to_pixel(CENTER_X, CENTER_Y, car_x, car_y, GRID_SIZE)
        pygame.draw.circle(screen, (0, 10, 200), (car_pixel_x, car_pixel_y), 6) 

        #A* path
        if path_cells:
            points = []
            for (gx, gy) in path_cells:
                px, py = caculation.world_to_pixel(CENTER_X, CENTER_Y, gx, gy, GRID_SIZE)
                points.append((px, py))

            if len(points) > 1:
                pygame.draw.lines(screen, (0, 180, 0), False, points, 3)

        #goal point
        g_px, g_py = caculation.world_to_pixel(CENTER_X, CENTER_Y, goal_grid[0], goal_grid[1], GRID_SIZE)
        pygame.draw.circle(screen, (0, 200, 0), (g_px, g_py), 5)

        pygame.display.flip()
        clock.tick(80)

    pygame.quit()
    sys.exit()

except serial.SerialException as e:
    print(f"無法開啟序列埠 {COM_PORT}，原因: {e}")
    print("提示：請確認 VS Code 的 Serial Monitor 已經關閉！")
except KeyboardInterrupt:
    print("\n程式被使用者中止。")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("序列埠已關閉。")