import pygame

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 10  

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

class grid_map:
    def __init__(self, screen, cell_size):
        pygame.init()
        self.WINDOW_WIDTH = screen.get_width()
        self.WINDOW_HEIGHT = screen.get_height()
        self.CENTER_X = self.WINDOW_WIDTH // 2
        self.CENTER_Y = self.WINDOW_HEIGHT // 2
        self.cell_size = cell_size
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
            x_pixel += self.cell_size
            grid_count += 1

        x_pixel = self.CENTER_X
        grid_count = 0
        while x_pixel > 0:
            if grid_count != 0:
                pygame.draw.line(screen, self.COLOR[1], (x_pixel, 0), (x_pixel, self.WINDOW_HEIGHT), 1)
                text = self.font.render(str(grid_count), True, self.COLOR[3])
                screen.blit(text, (x_pixel - text.get_width()//2, self.CENTER_Y + 5))
            x_pixel -= self.cell_size
            grid_count -= 1

        y_pixel = self.CENTER_Y
        grid_count = 0
        while y_pixel < self.WINDOW_HEIGHT:
            if grid_count != 0:
                pygame.draw.line(screen, self.COLOR[1], (0, y_pixel), (self.WINDOW_WIDTH, y_pixel), 1)
                text = self.font.render(str(grid_count), True, self.COLOR[3])
                screen.blit(text, (self.CENTER_X + 8, y_pixel - text.get_height()//2))
            y_pixel += self.cell_size
            grid_count -= 1

        y_pixel = self.CENTER_Y
        grid_count = 0
        while y_pixel > 0:
            if grid_count != 0:
                pygame.draw.line(screen, self.COLOR[1], (0, y_pixel), (self.WINDOW_WIDTH, y_pixel), 1)
                text = self.font.render(str(grid_count), True, self.COLOR[3])
                screen.blit(text, (self.CENTER_X + 8, y_pixel - text.get_height()//2))
            y_pixel -= self.cell_size
            grid_count += 1

        pygame.draw.line(screen, self.COLOR[2], (0, self.CENTER_Y), (self.WINDOW_WIDTH, self.CENTER_Y), 3) # X 軸
        pygame.draw.line(screen, self.COLOR[2], (self.CENTER_X, 0), (self.CENTER_X, self.WINDOW_HEIGHT), 3) # Y 軸

        pygame.draw.circle(screen, self.COLOR[4], (self.CENTER_X, self.CENTER_Y), 6)
        origin_text = self.font_bold.render("(0,0)", True, self.COLOR[4])
        screen.blit(origin_text, (self.CENTER_X - 35, self.CENTER_Y - 20))

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
