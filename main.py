import pygame
import sys
import serial
import time
import costmap, planner, caculation, draw, read_arduino

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
CENTER_X = WINDOW_WIDTH // 2
CENTER_Y = WINDOW_HEIGHT // 2
GRID_SIZE = 4

screen_size = (WINDOW_WIDTH, WINDOW_HEIGHT, CENTER_X, CENTER_Y, GRID_SIZE)

SENSOR_OFFSET = 11.5 #cm
infla_radius = 6  

# color
COLOR_CROSSHAIR = (0, 150, 255, 100) # 準星藍色 (帶有一點透明度)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pygame 4-Quadrant Gridmap (Float Coordinates)")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 12)
font_bold = pygame.font.SysFont("arial", 14, bold=True)

base_map = draw.Gridmap(screen_size, GRID_SIZE)
pg_obs_map = draw.Obsmap(screen_size, GRID_SIZE)
pg_infla_map = draw.Inflamap(screen_size, GRID_SIZE)

COSTMAP = costmap.Costmap()

goal_x, goal_y = 15, 15
path_cells = []      

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
                    goal_x, goal_y = caculation.pixel_to_world(CENTER_X, CENTER_Y, mx, my, GRID_SIZE)
                    map_changed = True

        tt_obs_points = [] 
        while ser.in_waiting > 0:
            raw_data = ser.readline()
            try:
                data_string = raw_data.decode('utf-8', errors='ignore').strip()
                
                if data_string: 
                    
                    obstacle_distance, deltaSL, deltaSR = read_arduino.decode(data_string)
                    if obstacle_distance is None :
                        continue
                    
                    car_x, car_y, car_theta = caculation.car_position(car_x, car_y, car_theta, deltaSL, deltaSR)
                    rel_obs_x, rel_obs_y = caculation.obs_pos(obstacle_distance, car_theta)
                    
                    obs_x = int(car_x) + int(rel_obs_x)
                    obs_y = int(car_y) + int(rel_obs_y)

                    # realtime obstacle
                    px, py = caculation.world_to_pixel(CENTER_X, CENTER_Y, obs_x, obs_y, GRID_SIZE)
                    obstacle_history.append((px, py))
                    
                    change_points, removed_obs = COSTMAP.obs_layer.do_obs_layer(car_x, car_y, obs_x, obs_y)

                    COSTMAP.total_obs_points(infla_radius, change_points, removed_obs, tt_obs_points)

                    pg_infla_map.redraw_del_infla_points(infla_radius, removed_obs)
                    pg_obs_map.draw_space_obstacle(change_points)
                    if tt_obs_points:
                        unique_obs_points = list(set(tt_obs_points))
                        infla_layer = COSTMAP.infla_layer.do_infla_layer(unique_obs_points, infla_radius)
                        pg_infla_map.draw_infla_points(infla_layer)

                    if len(obstacle_history) > 500:
                        obstacle_history.pop(0)
            except UnicodeDecodeError:
                pass

        if map_changed or 'prev_map_state' not in locals():
            start_tuple = (int(car_x), int(car_y))
            goal_tuple = (int(goal_x), int(goal_y))
            path_cells = planner.astar(start_tuple, goal_tuple, COSTMAP.infla_layer.infla_map)
            print(path_cells)
            prev_map_state = True

        #base map

        screen.fill(base_map.COLOR[0])  # Fill the background with the base color
        base_map.draw_grid(screen)
        base_map.draw_Unstd_obs_point(obstacle_history)
        base_map.draw_car_position(car_x, car_y)
        base_map.draw_Astar_path(path_cells)
        base_map.draw_goal_point(goal_x, goal_y)

        #screen.blit(pg_obs_map.obs_map_surface, (0, 0))
        screen.blit(pg_infla_map.infla_map_surface, (0, 0))

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