import pygame
import caculation
import math

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 10  

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

class Gridmap:
    def __init__(self, screen_size, grid_size):
        pygame.init()
        self.WINDOW_WIDTH = screen_size[0]
        self.WINDOW_HEIGHT = screen_size[1]
        self.CENTER_X = screen_size[2]
        self.CENTER_Y = screen_size[3]
        self.GRID_SIZE = grid_size
        self.screen = screen

        self.COLOR = [(240, 240, 240),     # 背景淺灰, COLOR_BG
                      (210, 210, 210),     # 網格線淡灰, COLOR_GRID
                      (50, 50, 50),        # 主座標軸深灰, COLOR_AXIS
                      (100, 100, 100),     # 標籤文字灰色, COLOR_TEXT
                      (255, 57, 57)       # 原點紅色, COLOR_ORIGIN
                      ] 
        
        self.font = pygame.font.SysFont("arial", 12)
        self.font_bold = pygame.font.SysFont("arial", 14, bold=True)
        self.draw_grid(self.screen)

    def draw_grid(self, screen):
        x_pixel = self.CENTER_X
        grid_count = 0
        while x_pixel < self.WINDOW_WIDTH:
            if grid_count != 0:
                pygame.draw.line(screen, self.COLOR[1], (x_pixel, 0), (x_pixel, self.WINDOW_HEIGHT), 1)
                text = self.font.render(str(grid_count), True, self.COLOR[3])
                screen.blit(text, (x_pixel - text.get_width()//2, self.CENTER_Y + 5))
            x_pixel += self.GRID_SIZE
            grid_count += 1

        x_pixel = self.CENTER_X
        grid_count = 0
        while x_pixel > 0:
            if grid_count != 0:
                pygame.draw.line(screen, self.COLOR[1], (x_pixel, 0), (x_pixel, self.WINDOW_HEIGHT), 1)
                text = self.font.render(str(grid_count), True, self.COLOR[3])
                screen.blit(text, (x_pixel - text.get_width()//2, self.CENTER_Y + 5))
            x_pixel -= self.GRID_SIZE
            grid_count -= 1

        y_pixel = self.CENTER_Y
        grid_count = 0
        while y_pixel < self.WINDOW_HEIGHT:
            if grid_count != 0:
                pygame.draw.line(screen, self.COLOR[1], (0, y_pixel), (self.WINDOW_WIDTH, y_pixel), 1)
                text = self.font.render(str(grid_count), True, self.COLOR[3])
                screen.blit(text, (self.CENTER_X + 8, y_pixel - text.get_height()//2))
            y_pixel += self.GRID_SIZE
            grid_count -= 1

        y_pixel = self.CENTER_Y
        grid_count = 0
        while y_pixel > 0:
            if grid_count != 0:
                pygame.draw.line(screen, self.COLOR[1], (0, y_pixel), (self.WINDOW_WIDTH, y_pixel), 1)
                text = self.font.render(str(grid_count), True, self.COLOR[3])
                screen.blit(text, (self.CENTER_X + 8, y_pixel - text.get_height()//2))
            y_pixel -= self.GRID_SIZE
            grid_count += 1

        pygame.draw.line(screen, self.COLOR[2], (0, self.CENTER_Y), (self.WINDOW_WIDTH, self.CENTER_Y), 3) # X 軸
        pygame.draw.line(screen, self.COLOR[2], (self.CENTER_X, 0), (self.CENTER_X, self.WINDOW_HEIGHT), 3) # Y 軸

        pygame.draw.circle(screen, self.COLOR[4], (self.CENTER_X, self.CENTER_Y), 6)
        origin_text = self.font_bold.render("(0,0)", True, self.COLOR[4])
        screen.blit(origin_text, (self.CENTER_X - 35, self.CENTER_Y - 20))

    def draw_Unstd_obs_point(self, Unstd_obs_points):
        for px, py in Unstd_obs_points:
            pygame.draw.circle(screen, (255, 0, 0), (px, py), 5)
    
    def draw_Astar_path(self, path_cells):
         if path_cells:
            points = []
            for (gx, gy) in path_cells:
                px, py = caculation.world_to_pixel(self.CENTER_X, self.CENTER_Y, gx, gy, self.GRID_SIZE)
                points.append((px, py))

            if len(points) > 1:
                pygame.draw.lines(screen, (0, 180, 0), False, points, 3)

    def draw_goal_point(self, g_x, g_y):
        g_px, g_py = caculation.world_to_pixel(self.CENTER_X, self.CENTER_Y, g_x, g_y, self.GRID_SIZE)
        pygame.draw.circle(self.screen, (0, 200, 0), (g_px, g_py), 5)

    def draw_car_position(self, car_x, car_y, car_angle_deg):
        car_pixel_x, car_pixel_y = caculation.world_to_pixel(self.CENTER_X, self.CENTER_Y, car_x, car_y, self.GRID_SIZE)
        rect_length = 25  
        rect_width = 4
        angle_rad = math.radians(car_angle_deg)
        end_x = car_pixel_x + rect_length * math.cos(angle_rad)
        end_y = car_pixel_y - rect_length * math.sin(angle_rad)

        pygame.draw.line(self.screen, (0, 50, 150), (car_pixel_x, car_pixel_y), (end_x, end_y), rect_width)
        pygame.draw.circle(self.screen, (0, 10, 200), (car_pixel_x, car_pixel_y), 6) 
class Obsmap:
    def __init__(self, screen_size, grid_size):
        self.obs_map_surface = pygame.Surface((screen_size[0], screen_size[1]), pygame.SRCALPHA)
        self.GRID_SIZE = grid_size
        self.CENTER_X = screen_size[2]
        self.CENTER_Y = screen_size[3]

    def draw_space_obstacle(self, space_obs_points):
        for (ox,oy),state in space_obs_points:
            if state == 1:  
                pygame.draw.circle(self.obs_map_surface, (0, 0, 255), (self.CENTER_X+ox*self.GRID_SIZE, self.CENTER_Y-oy*self.GRID_SIZE), 4)
            elif state == 0:  
                pygame.draw.circle(self.obs_map_surface, (0, 255, 0), (self.CENTER_X+ox*self.GRID_SIZE, self.CENTER_Y-oy*self.GRID_SIZE), 4)
            else:
                continue

class Inflamap:
    def __init__(self, screen_size, grid_size):
        self.infla_map_surface = pygame.Surface((screen_size[0], screen_size[1]), pygame.SRCALPHA)
        self.GRID_SIZE = grid_size
        self.CENTER_X = screen_size[2]
        self.CENTER_Y = screen_size[3]

    def draw_infla_points(self, infla_layer):
        for (fx, fy), cost in infla_layer:
            if cost:
                rect_x, rect_y = caculation.world_to_pixel(self.CENTER_X, self.CENTER_Y, fx, fy + 1, self.GRID_SIZE)
                pygame.draw.rect(self.infla_map_surface, (255, 0, 0, 100), (rect_x, rect_y, self.GRID_SIZE, self.GRID_SIZE))
            else:
                pass

    def redraw_del_infla_points(self, infla_radius, removed_obs):
        for rx, ry in removed_obs:
            rect_x, rect_y = caculation.world_to_pixel(self.CENTER_X, self.CENTER_Y, rx-infla_radius, ry + infla_radius + 1, self.GRID_SIZE)
            rect_size = (2 * infla_radius + 1) * self.GRID_SIZE
            self.infla_map_surface.fill((0, 0, 0, 0), (rect_x, rect_y, rect_size, rect_size))

"""
base_map = grid_map(screen, GRID_SIZE)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    screen.fill((240, 240, 240))
    base_map.draw_grid(screen)

    pygame.display.flip()
"""
