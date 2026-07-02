import pygame
import sys
import serial
import time
import caculation
import costmap

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


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 5  

# color
COLOR_BG = (240, 240, 240)       # 背景淺灰
COLOR_GRID = (210, 210, 210)     # 網格線淡灰
COLOR_AXIS = (50, 50, 50)        # 主座標軸深灰
COLOR_TEXT = (100, 100, 100)     # 標籤文字灰色
COLOR_ORIGIN = (255, 57, 57)     # 原點紅色
COLOR_CROSSHAIR = (0, 150, 255, 100) # 準星藍色 (帶有一點透明度)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pygame 4-Quadrant Gridmap (Float Coordinates)")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 12)
font_bold = pygame.font.SysFont("arial", 14, bold=True)

CENTER_X = WINDOW_WIDTH // 2
CENTER_Y = WINDOW_HEIGHT // 2

inflation_radius = 6  
obstacle_map = {}  
inflation_map = {}
counter = 0
obstacle_map_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
inflated_map_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)

def draw_gridmap():
    x_pixel = CENTER_X
    grid_count = 0
    while x_pixel < WINDOW_WIDTH:
        if grid_count != 0:
            pygame.draw.line(screen, COLOR_GRID, (x_pixel, 0), (x_pixel, WINDOW_HEIGHT), 1)
            text = font.render(str(grid_count), True, COLOR_TEXT)
            screen.blit(text, (x_pixel - text.get_width()//2, CENTER_Y + 5))
        x_pixel += GRID_SIZE
        grid_count += 1

    x_pixel = CENTER_X
    grid_count = 0
    while x_pixel > 0:
        if grid_count != 0:
            pygame.draw.line(screen, COLOR_GRID, (x_pixel, 0), (x_pixel, WINDOW_HEIGHT), 1)
            text = font.render(str(grid_count), True, COLOR_TEXT)
            screen.blit(text, (x_pixel - text.get_width()//2, CENTER_Y + 5))
        x_pixel -= GRID_SIZE
        grid_count -= 1

    y_pixel = CENTER_Y
    grid_count = 0
    while y_pixel < WINDOW_HEIGHT:
        if grid_count != 0:
            pygame.draw.line(screen, COLOR_GRID, (0, y_pixel), (WINDOW_WIDTH, y_pixel), 1)
            text = font.render(str(grid_count), True, COLOR_TEXT)
            screen.blit(text, (CENTER_X + 8, y_pixel - text.get_height()//2))
        y_pixel += GRID_SIZE
        grid_count -= 1

    y_pixel = CENTER_Y
    grid_count = 0
    while y_pixel > 0:
        if grid_count != 0:
            pygame.draw.line(screen, COLOR_GRID, (0, y_pixel), (WINDOW_WIDTH, y_pixel), 1)
            text = font.render(str(grid_count), True, COLOR_TEXT)
            screen.blit(text, (CENTER_X + 8, y_pixel - text.get_height()//2))
        y_pixel -= GRID_SIZE
        grid_count += 1

    pygame.draw.line(screen, COLOR_AXIS, (0, CENTER_Y), (WINDOW_WIDTH, CENTER_Y), 3) # X 軸
    pygame.draw.line(screen, COLOR_AXIS, (CENTER_X, 0), (CENTER_X, WINDOW_HEIGHT), 3) # Y 軸

    pygame.draw.circle(screen, COLOR_ORIGIN, (CENTER_X, CENTER_Y), 6)
    origin_text = font_bold.render("(0,0)", True, COLOR_ORIGIN)
    screen.blit(origin_text, (CENTER_X - 35, CENTER_Y - 20))

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"成功連結 {COM_PORT}")
    running = True
    time.sleep(2) 

    while running:
        while ser.in_waiting > 0:
            raw_data = ser.readline()
            try:
                data_string = raw_data.decode('utf-8', errors='ignore').strip()
                
                if data_string: 
                    
                    input_array = data_string.split(",")

                    if len(input_array) >= 3:
                        val_str1 = input_array[0].strip()
                        val_str2 = input_array[1].strip()
                        val_str3 = input_array[-1].strip()
                        
                        print(val_str2,val_str3)
                        # if val_str1 and val_str2 are not empty, convert to float
                        if val_str1 and val_str2 and val_str3:
                            obstacle_distance = float(val_str1)
                            deltaSL = float(val_str2)
                            deltaSR = float(val_str3)
                            
                            car_x, car_y, car_theta = caculation.car_position(car_x, car_y, car_theta, deltaSL, deltaSR)
                            rel_obs_x, rel_obs_y = caculation.obs_pos(obstacle_distance, car_theta)
                            
                            obs_x = car_x + rel_obs_x
                            obs_y = car_y + rel_obs_y

                            # realtime obstacle
                            px = int(CENTER_X + obs_x * GRID_SIZE)
                            py = int(CENTER_Y - obs_y * GRID_SIZE)
                            obstacle_history.append((px, py))
                            
                            # obstacle layer visualization
                            change_points, new_obs_point, removed_obs = costmap.obs_layer(car_x, car_y, obs_x, obs_y, obstacle_map)

                            if removed_obs is not None: 
                                tt_obs_points = []       
                                for (ox,oy),state in change_points:
                                    if state == 1:  
                                        pygame.draw.circle(obstacle_map_surface, (0, 0, 255), (CENTER_X+ox*GRID_SIZE, CENTER_Y-oy*GRID_SIZE), 4)
                                    elif state == 0:  
                                        pygame.draw.circle(obstacle_map_surface, (0, 255, 0), (CENTER_X+ox*GRID_SIZE, CENTER_Y-oy*GRID_SIZE), 4)
                                    else:
                                        continue
                                
                                if removed_obs:
                                    for rx, ry in removed_obs:
                                        
                                        # rmove cost
                                        for dx in range(-inflation_radius, inflation_radius + 1):
                                            for dy in range(-inflation_radius, inflation_radius + 1):
                                                target_key = (rx + dx, ry + dy)
                                                if target_key in inflation_map:
                                                    del inflation_map[target_key]

                                        rect_x = CENTER_X + (rx - inflation_radius) * GRID_SIZE
                                        rect_y = CENTER_Y - (ry + inflation_radius + 1) * GRID_SIZE
                                        rect_size = (2 * inflation_radius + 1) * GRID_SIZE
                                        inflated_map_surface.fill((0, 0, 0, 0), (rect_x, rect_y, rect_size, rect_size))

                                        #rebiuld exist obs inflation layer
                                        search_r = 2 * inflation_radius
                                        
                                        for nx in range(-search_r, search_r + 1):
                                            for ny in range(-search_r, search_r + 1):
                                                neighbor_pt = (rx + nx, ry + ny)
                                                if obstacle_map.get(neighbor_pt) == 1:
                                                    tt_obs_points.append(neighbor_pt)
                            
                        # inflation layer visualization
                        for (fx, fy), cost in costmap.inflation_layer(tt_obs_points, inflation_radius, inflation_map):
                            rect_x = CENTER_X + fx * GRID_SIZE
                            rect_y = CENTER_Y - (fy + 1) * GRID_SIZE 
                            
                            pygame.draw.rect(inflated_map_surface, (255, 0, 0, cost), (rect_x, rect_y, GRID_SIZE, GRID_SIZE))

                            if len(obstacle_history) > 500:
                                obstacle_history.pop(0)
            except UnicodeDecodeError:
                pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #pygame display
        screen.fill(COLOR_BG)
        draw_gridmap()

        screen.blit(obstacle_map_surface, (0, 0))
        screen.blit(inflated_map_surface, (0, 0))

        for px, py in obstacle_history:
            pygame.draw.circle(screen, (255, 0, 0), (px, py), 5)

        car_pixel_x = int(CENTER_X + car_x * GRID_SIZE)
        car_pixel_y = int(CENTER_Y - car_y * GRID_SIZE)
        pygame.draw.circle(screen, (0, 10, 200), (car_pixel_x, car_pixel_y), 6) # 藍色小車

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