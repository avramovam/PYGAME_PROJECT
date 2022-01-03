import pygame
import engine

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
    Andrey Avramov                                                                                        #3
    Daria Stolyarova                                                                              03.01.2022
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
#region [BG]
def BG_create(target):
    target.image = None
    target.angle = 0
    target.offset = 8
    target.gotofield = 0
    target.gotofield_step = 0

def BG_step(target):
    target.angle = (target.angle+UPF(30)) % 360
    if target.gotofield:
        target.gotofield_step += UPF(1/2) # полный переход за 2 секунды
    if target.gotofield_step >= 1:
        engine.rooms.change_current_room(room_field)

def BG_draw_before(target, surface: pygame.Surface):
    #pygame.draw.circle(surface, 'yellow', (2, 2), 5.0)
    ox = engine.lengthdir_x(target.offset, target.angle)
    oy = engine.lengthdir_y(target.offset, target.angle)
    width = surface.get_width()
    height = surface.get_height()
    for x in ((-1, 0),(0, 1))[ox<0]:     # этот цикл отрисовывает картинку четырежды, чтобы в любом случае
        for y in ((-1, 0),(0, 1))[oy<0]: # замостить полностью холст. ((-1, 0),(0, 1))[ox<0] лишь оптимизирует это
            surface.blit(target.image, (ox + (x * width),  # - леша
                                        oy + (y * height)))

def BG_draw_after(target, surface: pygame.Surface):
    '''Здесь будет рисоваться типо круг перехода из уровня в уровень'''
    width = surface.get_width()
    height = surface.get_height()
    half_diagonal = (((width**2) + (height**2))**0.5) / 2
    circle_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    circle_surface2 = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    circle_surface.fill('black')
    pygame.draw.circle(circle_surface2, 'black', (width/2, height/2), half_diagonal * (1 - target.gotofield_step), 0)
    circle_surface.blit(circle_surface2, (0, 0), None, pygame.BLEND_RGBA_SUB)
    surface.blit(circle_surface, (0, 0), None)

EntBG = engine.Entity(event_create=BG_create, event_step=BG_step, event_draw_before=BG_draw_before,
                      event_draw_after=BG_draw_after)
#endregion
#region [MAINMENU TEXT]
def mm_text_create(target):
    target.x, target.y = 0, 0
    target.font = font_default
    target.string = 'Neon Constellation'
    target.text_color = 'white'
    target.text_align = 1  # 0 - слева, 1 - в центре, 2 - справа
    instance_render_text(target)


def mm_text_draw(target, surface: pygame.Surface):
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

EntMainMenuText = engine.Entity(event_create=mm_text_create, event_draw=mm_text_draw)
#endregion
#region [MAINMENU BUTTON]
def mm_button_user0(): # Переход на поле
    bg1.gotofield = 1

def mm_button_create(target):
    target.x, target.y = 0, 0
    target.font = font_default
    target.string = 'Sample Text'
    target.text_color = 'black'
    instance_render_text(target)
    target.press_link = None

def mm_button_draw(target, surface: pygame.Surface):
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

def mm_button_mouse_pressed(target, mousepos, buttonid):
    tw = target.text[0].get_width()
    th = target.text[0].get_height()
    fs = 16  # размер поля между прямоугольником и текстом
    xrange = target.x - ((tw+fs)//2) <= mousepos[0] <= target.x + ((tw+fs)//2)
    yrange = target.y - ((th+fs)//2) <= mousepos[1] <= target.y + ((th+fs)//2)
    if xrange and yrange:
        if target.press_link is not None:
            target.press_link()

# EntMainMenuButton копирует метод создания и рендера текста из EntGameTitle
EntMainMenuButton = engine.Entity(event_create=mm_button_create, event_draw=mm_button_draw,
                                  event_mouse_pressed=mm_button_mouse_pressed)
#endregion
#endregion

#region [ОБЪЯВЛЕНИЕ ROOM]
room_mainmenu = engine.Room([EntBG, EntMainMenuText, EntMainMenuButton])

room_field = engine.Room([])

engine.rooms.change_current_room(room_mainmenu)
#endregion

#region [СОЗДАНИЕ INSTANCE]
bg1 = EntBG.instance()
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
mmb1.press_link = mm_button_user0

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
#endregion

#region [КОНСТАНТЫ, ПЕРЕМЕННЫЕ И Т.Д.]

#endregion

#region [ГЛАВНЫЙ ЦИКЛ]
print('Запуск главного цикла...')
game_running = 1
a = 0
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


    screen.get_canvas().fill('black')
    engine.rooms.current_room.do_step(screen.get_canvas())
    screen.draw_screen()
    pygame.display.flip()
    clock.tick(FPS)
#endregion