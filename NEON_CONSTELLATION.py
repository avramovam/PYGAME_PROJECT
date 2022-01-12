import pygame
import engine
from math import floor, ceil
import random

#region [ИНИЦИАЛИЗАЦИЯ ПРОГРАММЫ]
print(''':P
 _   _  _____ _____ _   _   _____ _____ _   _  _____ _____ _____ _      _       ___ _____ _____ _____ _   _ 
| \\ | ||  ___|  _  | \\ | | /  __ \\  _  | \\ | |/  ___|_   _|  ___| |    | |     / _ \\_   _|_   _|  _  | \\ | |
|  \\| || |__ | | | |  \\| | | /  \\/ | | |  \\| |\\ `--.  | | | |__ | |    | |    / /_\\ \\| |   | | | | | |  \\| |
| . ` ||  __|| | | | . ` | | |   | | | | . ` | `--. \\ | | |  __|| |    | |    |  _  || |   | | | | | | . ` |
| |\\  || |___\\ \\_/ / |\\  | | \\__/\\ \\_/ / |\\  |/\\__/ / | | | |___| |____| |____| | | || |  _| |_\\ \\_/ / |\\  |
\\_| \\_/\\____/ \\___/\\_| \\_/  \\____/\\___/\\_| \\_/\\____/  \\_/ \\____/\\_____/\\_____/\\_| |_/\\_/  \\___/ \\___/\\_| \\_/
                                            (Neon Constellation)
by:                                                                                      version:
    Alexey Kozhanov                                                                               DVLP BUILD
    Andrey Avramov                                                                                        #5
    Daria Stolyarova                                                                              08.01.2022
''')

pygame.init()
USER_SCREENSIZE = engine.get_screensize(engine.pygame_videoinfo()) # размер монитора пользователя
scale = 40
pixelscale = 2
screen = engine.Screen((16*scale, 9*scale), (16*scale*pixelscale, 9*scale*pixelscale), 0, 1)
clock = pygame.time.Clock()
FPS = 60

del scale, pixelscale

img_bg = pygame.transform.scale(engine.load_image('bg.png'), (screen.get_canvas_width()*1, screen.get_canvas_height()*1))
img_player_battle = engine.load_image('player_battle.png')

def UPF(units_per_second):
    '''Сокращение функции engine.speed_upf, которая возвращает скорость "еденицы в кадр",
       имея скорость "еденицы в секунду" и количество кадров в секунду.
       Использовать в ежекадровых функциях где считается время или двигаются объекты.'''
    return engine.speed_upf(units_per_second, FPS)

font_default = pygame.font.Font(None, 24)
font_small =   pygame.font.Font(None, 18)
font_heading = pygame.font.Font(None, 48)

def instance_render_text(target):
    '''Рендерит текст для target если есть target.string и target.font.
       target.text содержит отрендеренные строчки текста.'''
    target.text = []
    for line in target.string.split('\n'):
        target.text.append(target.font.render(line, True, target.text_color))
#endregion

#region [ОБЪЯВЛЕНИЕ ENTITY]
#region [MAINMENU BG]
def MainMenuBG_create(target):
    target.image = None
    target.angle = 0
    target.offset = 8
    target.gotofield = 0
    target.gotofield_step = 0

def MainMenuBG_step(target):
    target.angle = (target.angle+UPF(30)) % 360
    if target.gotofield:
        target.gotofield_step += UPF(1/2) # полный переход за 2 секунды
    if target.gotofield_step >= 1:
        engine.rooms.change_current_room(room_field)

def MainMenuBG_draw_before(target, surface: pygame.Surface):
    #pygame.draw.circle(surface, 'yellow', (2, 2), 5.0)
    ox = engine.lengthdir_x(target.offset, target.angle)
    oy = engine.lengthdir_y(target.offset, target.angle)
    width = surface.get_width()
    height = surface.get_height()
    for x in ((-1, 0),(0, 1))[ox<0]:     # этот цикл отрисовывает картинку четырежды, чтобы в любом случае
        for y in ((-1, 0),(0, 1))[oy<0]: # замостить полностью холст. ((-1, 0),(0, 1))[ox<0] лишь оптимизирует это
            surface.blit(target.image, (ox + (x * width),  # - леша
                                        oy + (y * height)))

def MainMenuBG_draw_after(target, surface: pygame.Surface):
    '''Здесь будет рисоваться типо круг перехода из уровня в уровень'''
    width = surface.get_width()
    height = surface.get_height()
    half_diagonal = (((width**2) + (height**2))**0.5) / 2
    circle_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    circle_surface2 = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    circle_surface.fill('black')
    pygame.draw.circle(circle_surface2, 'black', (width/2, height/2), half_diagonal * (max(0, 1.4*(1 - target.gotofield_step) - 0.4)), 0)
    circle_surface.blit(circle_surface2, (0, 0), None, pygame.BLEND_RGBA_SUB)
    surface.blit(circle_surface, (0, 0), None)

EntMainMenuBG = engine.Entity(event_create=MainMenuBG_create, event_step=MainMenuBG_step,
                              event_draw_before=MainMenuBG_draw_before, event_draw_after=MainMenuBG_draw_after)
#endregion
#region [MAINMENU TEXT]
def MainMenuText_create(target):
    target.x, target.y = 0, 0
    target.font = font_default
    target.string = 'Neon Constellation'
    target.text_color = 'white'
    target.text_align = 1  # 0 - слева, 1 - в центре, 2 - справа
    instance_render_text(target)


def MainMenuText_draw(target, surface: pygame.Surface):
    lineoffset = 0
    maxtw = max([x.get_width() for x in target.text])
    for lineindex in range(len(target.text)):
        tw = target.text[lineindex].get_width()
        th = target.text[lineindex].get_height()
        lineoffset += th+4
        if target.text_align == 0:
            surface.blit(target.text[lineindex], (target.x, target.y - (th//2) + lineoffset))
        elif target.text_align == 2:
            surface.blit(target.text[lineindex], (target.x + (maxtw - tw), target.y - (th//2) + lineoffset))
        else:  # if target.text_align == 1:
            surface.blit(target.text[lineindex], (target.x - (tw//2), target.y - (th//2) + lineoffset))

EntMainMenuText = engine.Entity(event_create=MainMenuText_create, event_draw=MainMenuText_draw)
#endregion
#region [MAINMENU BUTTON]
def MainMenuButton_user0(): # Переход на поле
    bg1.gotofield = 1

def MainMenuButton_user2(): # Выход
    global game_running
    game_running = 0

def MainMenuButton_create(target):
    target.x, target.y = 0, 0
    target.font = font_default
    target.string = 'Sample Text'
    target.text_color = 'black'
    instance_render_text(target)
    target.press_link = None

def MainMenuButton_draw(target, surface: pygame.Surface):
    tw = target.text[0].get_width()
    th = target.text[0].get_height()
    fs = 16 # размер поля между прямоугольником и текстом
    rect_coords = (target.x - ((tw+fs)//2), target.y - ((th+fs)//2), tw+fs, th+fs)
    text_coords = (target.x - (tw//2),      target.y - (th//2))
    rounding = 4 # величина скругления задника
    full_rounding = (rounding, rounding, rounding, rounding) # для всех углов
    pygame.draw.rect(surface, 'white', rect_coords, 0, *full_rounding) # задник
    pygame.draw.rect(surface, 'gray',  rect_coords, 3, *full_rounding) # обводка задника
    surface.blit(target.text[0], text_coords)

def MainMenuButton_mouse_pressed(target, mousepos, buttonid):
    tw = target.text[0].get_width()
    th = target.text[0].get_height()
    fs = 16  # размер поля между прямоугольником и текстом
    xrange = target.x - ((tw+fs)//2) <= mousepos[0] <= target.x + ((tw+fs)//2)
    yrange = target.y - ((th+fs)//2) <= mousepos[1] <= target.y + ((th+fs)//2)
    if xrange and yrange:
        if target.press_link is not None:
            target.press_link()

# EntMainMenuButton копирует метод создания и рендера текста из EntGameTitle
EntMainMenuButton = engine.Entity(event_create=MainMenuButton_create, event_draw=MainMenuButton_draw,
                                  event_mouse_pressed=MainMenuButton_mouse_pressed)
#endregion
#region [FIELD BG]
def FieldBG_create(target):
    target.image = None
    target.angle = 0
    target.offset = 8
    target.fadeout = 1
    #target.x = 0
    #target.y = 0

def FieldBG_draw_before(target, surface):
    ox = 0
    oy = 0
    #width = surface.get_width()
    #height = surface.get_height()
    surface.blit(target.image, (ox, oy))

EntFieldBG = engine.Entity(event_create=FieldBG_create, event_draw_before=FieldBG_draw_before)
#endregion
#region [FIELD BOARD]
def FieldBoard_get_cell_coords(target, cellx, celly):
    retx = target.start_x + (cellx*(target.cellsize+1))
    rety = target.start_y + (celly*(target.cellsize+1))
    return retx, rety

def FieldBoard_user0(target, surface: pygame.Surface):
    '''Расчет start_x и start_y согласно центрированию на surface'''
    surface_center_x = surface.get_width()//2
    surface_center_y = surface.get_height()//2
    target.start_x = surface_center_x - (target.width//2)
    target.start_y = surface_center_y - (target.height//2)

def FieldBoard_create(target):
    target.cellsize = 20
    target.cellcount_x = 15
    target.cellcount_y = 15
    # target.start_x = 0
    # target.start_y = 0
    target.width = ((target.cellsize+1) * target.cellcount_x) + 1
    target.height = ((target.cellsize+1) * target.cellcount_y) + 1
    FieldBoard_user0(target, screen.get_canvas())
    target.boardalpha = 1 # уровень прозрачности от 0 (полностью прозрачный) до 1 (полностью видимый)


def FieldBoard_draw_before(target, surface: pygame.Surface):
    board_surface = pygame.Surface((target.width, target.height), pygame.SRCALPHA)
    board_surface.fill((0,0,0,0))
    # попиксельное отрисовывание сетки хехехехехехехехехе ужас
    cellsize_with_border = target.cellsize + 1
    for px in range(target.width):
        for py in range(target.height):
            if py % cellsize_with_border == 0: # линия по горизонтали
                minimal = floor(px / cellsize_with_border) * cellsize_with_border # близжайшее левое пересечение линий
                maximal = ceil(px / cellsize_with_border) * cellsize_with_border # близжайшее правое пересечение линий

                if minimal == maximal: # мы находимся на пересечении
                    alpha = 1
                else:
                    alpha = max(abs(minimal-px), abs(maximal-px)) / cellsize_with_border
                    alpha = 2 * (alpha - 0.5)
                board_surface.set_at((px, py), (255, 255, 255, 255 * alpha * target.boardalpha))
            elif px % cellsize_with_border == 0:  # линия по горизонтали
                minimal = floor(py / cellsize_with_border) * cellsize_with_border  # близжайшее верхнее пересечение линий
                maximal = ceil(py / cellsize_with_border) * cellsize_with_border  # близжайшее нижнее пересечение линий

                if minimal == maximal:  # мы находимся на пересечении
                    alpha = 1
                else:
                    alpha = max(abs(minimal - py), abs(maximal - py)) / cellsize_with_border
                    alpha = 2 * (alpha - 0.5)
                board_surface.set_at((px, py), (255, 255, 255, 255 * alpha * target.boardalpha))
    surface.blit(board_surface, (target.start_x, target.start_y))


EntFieldBoard = engine.Entity(event_create=FieldBoard_create, event_draw_before=FieldBoard_draw_before)
#endregion
#region [FIELD PLAYER]
def FieldPlayer_create(target):
    target.x = 0 # где он щас
    target.y = 0 # где он щас
    target.xto = 0 # куда двигаться
    target.yto = 0 # куда двигаться
    target.cellx = 0 # в какой клетке
    target.celly = 0 # в какой клетке
    target.nextcellx = 0
    target.nextcelly = 0
    target.image = img_player_battle
    target.image_angle = 0
    target.myboard = None

def FieldPlayer_step(target):
    if target.myboard is not None:
        target.xto, target.yto = FieldBoard_get_cell_coords(target.myboard, target.cellx, target.celly) # получение left-top-края
        # target.xto += target.myboard.cellsize//2 # xto = середина клетки
        # target.yto += target.myboard.cellsize//2 # yto = середина клетки
    ix = engine.interpolate(target.x, target.xto, 2, 0)
    iy = engine.interpolate(target.y, target.yto, 2, 0)

    if round(target.x, 2) == round(ix, 2): target.x = target.xto
    else: target.x = ix

    if round(target.y, 2) == round(iy, 2): target.y = target.yto
    else: target.y = iy
    #target.x = target.xto
    #target.y = target.yto

    dx = target.xto - target.x
    dy = target.yto - target.y
    if not (dx == dy == 0):
        originangle = target.image_angle - 90
        angleto = engine.point_direction(0, 0, dx, dy)
        target.image_angle = (originangle + angleto)/2
    else:
        target.image_angle = engine.point_direction(target.cellx, target.celly,
                                                    target.nextcellx, target.nextcelly) - 90

def FieldPlayer_draw(target, surface: pygame.Surface):
    myimage = pygame.transform.rotate(target.image, target.image_angle)
    myimage_width = myimage.get_width()
    myimage_height = myimage.get_height()
    deltawidth = myimage_width - target.myboard.cellsize
    deltaheight = myimage_height - target.myboard.cellsize
    surface.blit(myimage,
                 (target.x - deltawidth//2 + 1,
                  target.y - deltaheight//2 + 1))
    #surface.blit(myimage, (target.x - (myimage_width//2) + 1, target.y - (myimage_height//2) + 1))
    #surface.blit(myimage, (target.x, target.y))

def FieldPlayer_kb_pressed(target, buttonid):
    if buttonid == pygame.K_LEFT:
        target.cellx = engine.clamp(target.cellx - 1, 0, target.myboard.cellcount_x-1)
        target.nextcellx = target.cellx - 1
        target.nextcelly = target.celly
    elif buttonid == pygame.K_RIGHT:
        target.cellx = engine.clamp(target.cellx + 1, 0, target.myboard.cellcount_x-1)
        target.nextcellx = target.cellx + 1
        target.nextcelly = target.celly
    elif buttonid == pygame.K_UP:
        target.celly = engine.clamp(target.celly - 1, 0, target.myboard.cellcount_y-1)
        target.nextcellx = target.cellx
        target.nextcelly = target.celly - 1
    elif buttonid == pygame.K_DOWN:
        target.celly = engine.clamp(target.celly + 1, 0, target.myboard.cellcount_y-1)
        target.nextcellx = target.cellx
        target.nextcelly = target.celly + 1

EntFieldPlayer = engine.Entity(event_create=FieldPlayer_create, event_step=FieldPlayer_step, event_draw=FieldPlayer_draw,
                               event_kb_pressed=FieldPlayer_kb_pressed)
#endregion
#endregion

#region [ОБЪЯВЛЕНИЕ ROOM]
room_mainmenu = engine.Room([EntMainMenuBG, EntMainMenuText, EntMainMenuButton])

room_field = engine.Room([EntFieldBG, EntFieldBoard, EntFieldPlayer])

engine.rooms.change_current_room(room_mainmenu)
#endregion

#region [СОЗДАНИЕ INSTANCE]
bg1 = EntMainMenuBG.instance()
bg1.image = img_bg

gametitle = EntMainMenuText.instance()
gametitle.x = screen.get_canvas_halfwidth()
gametitle.y = 0
gametitle.font = font_heading
gametitle.string = 'Neon Constellation'
instance_render_text(gametitle)

creators = EntMainMenuText.instance()
creators.x = 8
creators.y = screen.get_canvas_height() - 80
creators.font = font_small
creators.text_align = 0
creators.string = 'Создатели:\nАлексей Кожанов\nАндрей Аврамов\nДарья Столярова'
instance_render_text(creators)

mmb1 = EntMainMenuButton.instance()
mmb1.x = screen.get_canvas_halfwidth()
mmb1.y = screen.get_canvas_halfheight() - 48
mmb1.string = 'Начать игру'
instance_render_text(mmb1)
mmb1.press_link = MainMenuButton_user0

mmb2 = EntMainMenuButton.instance()
mmb2.x = screen.get_canvas_halfwidth()
mmb2.y = screen.get_canvas_halfheight()
mmb2.string = 'Настройки'
instance_render_text(mmb2)

mmb3 = EntMainMenuButton.instance()
mmb3.x = screen.get_canvas_halfwidth()
mmb3.y = screen.get_canvas_halfheight() + 48
mmb3.string = 'Выйти'
instance_render_text(mmb3)
mmb3.press_link = MainMenuButton_user2


class Enemy:
    def __init__(self, app, pos, number):
        self.app = app
        self.grid_pos = pos
        self.starting_pos = [pos.x, pos.y]
        self.pix_pos = self.get_pix_pos()
        self.radius = int(self.app.cell_width//2.3)
        self.number = number
        self.colour = self.set_colour()
        self.direction = vec(0, 0)
        self.personality = self.set_personality()
        self.target = None
        self.speed = self.set_speed()


    def update(self):
        self.target = self.set_target()
        if self.target != self.grid_pos:
            self.pix_pos += self.direction * self.speed
            if self.time_to_move():
                self.move()

        # Setting grid position in reference to pix position
        self.grid_pos[0] = (self.pix_pos[0]- 50 +
                            self.app.cell_width//2)//self.app.cell_width+1
        self.grid_pos[1] = (self.pix_pos[1]- 50 +
                            self.app.cell_height//2)//self.app.cell_height+1

    def draw(self):
        pygame.draw.circle(self.app.screen, self.colour,
                           (int(self.pix_pos.x), int(self.pix_pos.y)), self.radius)

    def set_speed(self):
        # Скорость врага на поле
        speed = 1
        return speed

    def set_target(self):
        # Нужно изменить систему поиска игрока
        # if self.personality == "speedy" or self.personality == "slow":
        #     return self.app.player.grid_pos
        # else:
        #     if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
        #         return vec(1, 1)
        #     if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] < ROWS//2:
        #         return vec(1, ROWS-2)
        #     if self.app.player.grid_pos[0] < COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
        #         return vec(COLS-2, 1)
        #     else:
        #         return vec(COLS-2, ROWS-2)
        pass
#
    def time_to_move(self):
        # Нужно изменить и эту функцию тоже
        # if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
        #     if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
        #         return True
        # if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
        #     if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
        #         return True
        # return False
        pass

    def move(self):
        # Нужно добавить пару функций для работы этого класса
        if self.personality == "random":
            self.direction = self.get_random_direction()
        if self.personality == "slow":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "speedy":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "scared":
            self.direction = self.get_path_direction(self.target)

    def get_path_direction(self, target):
        next_cell = self.find_next_cell_in_path(target)
        xdir = next_cell[0] - self.grid_pos[0]
        ydir = next_cell[1] - self.grid_pos[1]
        return vec(xdir, ydir)

    def find_next_cell_in_path(self, target):
        path = self.BFS([int(self.grid_pos.x), int(self.grid_pos.y)], [
                        int(target[0]), int(target[1])])
        return path[1]

    def BFS(self, start, target):
        grid = [[0 for x in range(28)] for x in range(30)]
        for cell in self.app.walls:
            if cell.x < 28 and cell.y < 30:
                grid[int(cell.y)][int(cell.x)] = 1
        queue = [start]
        path = []
        visited = []
        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    if neighbour[0]+current[0] >= 0 and neighbour[0] + current[0] < len(grid[0]):
                        if neighbour[1]+current[1] >= 0 and neighbour[1] + current[1] < len(grid):
                            next_cell = [neighbour[0] + current[0], neighbour[1] + current[1]]
                            if next_cell not in visited:
                                if grid[next_cell[1]][next_cell[0]] != 1:
                                    queue.append(next_cell)
                                    path.append({"Current": current, "Next": next_cell})
        shortest = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest

    def get_random_direction(self):
        while True:
            number = random.randint(-2, 1)
            if number == -2:
                x_dir, y_dir = 1, 0
            elif number == -1:
                x_dir, y_dir = 0, 1
            elif number == 0:
                x_dir, y_dir = -1, 0
            else:
                x_dir, y_dir = 0, -1
            next_pos = vec(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
            if next_pos not in self.app.walls:
                break
        return vec(x_dir, y_dir)

    def get_pix_pos(self):
        return vec((self.grid_pos.x*self.app.cell_width)+ 50 //2+self.app.cell_width//2,
                   (self.grid_pos.y*self.app.cell_height)+ 50 //2 +
                   self.app.cell_height//2)

    def set_colour(self):
        # Для теста на случай отсутствия картинки

        return (215, 159, 33)

    def set_personality(self):
        # Тут тоже нужны функции с других классов, в течении пару дней сделаю
        # if self.number == 0:
        #     return "speedy"
        # elif self.number == 1:
        #     return "slow"
        # elif self.number == 2:
        #     return "random"
        # else:
        #     return "scared"
        pass


vec = pygame.math.Vector2

fboard = EntFieldBoard.instance()

bg2 = EntFieldBG.instance()
bg2.image = img_bg

fplayer = EntFieldPlayer.instance()
fplayer.myboard = fboard
#endregion

#region [КОНСТАНТЫ, ПЕРЕМЕННЫЕ И Т.Д.]

#endregion

#region [ГЛАВНЫЙ ЦИКЛ]
print('Запуск главного цикла...')
pygame.mixer.music.load('music.mp3')
pygame.mixer.music.play()
game_running = 1
event_fight = 0 # событие начала боя. Меняет музыку, добавлявет текст "Бой" и др.
music_turned_on = 1 # Переменная, обозначающая включена ли музыка для более удобной работы с кодом
# Добавление события начала боя

# Событие меняет фон если установлено значение 1
# Функция отображения текста
def draw_text(self, words, screen, pos, size, colour, font_name='arial', centered=False):
    font = pygame.font.SysFont(font_name, size)
    text = font.render(words, False, colour)
    text_size = text.get_size()
    if centered:
        pos[0] = pos[0] - text_size[0] // 2
        pos[1] = pos[1] - text_size[1] // 2
    screen.blit(text, pos)


a = 0
screen_to_draw = pygame.display.set_mode((screen.get_canvas_width() * 2, screen.get_canvas_height() * 2))
while game_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # выход
            game_running = 0
        elif event.type == pygame.VIDEORESIZE: # изменение размера экрана
            screen.update_screen((event.w, event.h))
        elif event.type == pygame.MOUSEMOTION:
            engine.rooms.current_room.do_mouse_moved(screen.get_mousepos_on_canvas(event.pos))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            engine.rooms.current_room.do_mouse_pressed(screen.get_mousepos_on_canvas(event.pos), event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            engine.rooms.current_room.do_mouse_released(screen.get_mousepos_on_canvas(event.pos), event.button)
        elif event.type == pygame.KEYDOWN:
            engine.rooms.current_room.do_kb_pressed(event.key)
        elif event.type == pygame.KEYUP:
            engine.rooms.current_room.do_kb_released(event.key)

    if event_fight == 1:
        print('fight')
        draw_text(screen, "БОЙ", screen_to_draw, [screen.get_canvas_width(), screen.get_canvas_height() * 2 - 25], 36, (255, 0, 0), "arial", centered=True)
        pygame.display.flip()
        if not music_turned_on:
            pygame.mixer.music.load('fight.mp3')
            pygame.mixer.music.play()
            music_turned_on = 1

    screen.get_canvas().fill('black')
    engine.rooms.current_room.do_step(screen.get_canvas())
    screen.draw_screen()
    pygame.display.flip()
    clock.tick(FPS)
#endregion