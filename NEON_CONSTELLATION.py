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
    Andrey Avramov                                                                                        #1
    Daria Stolyarova                                                                              30.12.2021
''')

pygame.init()
USER_SCREENSIZE = engine.get_screensize(engine.pygame_videoinfo()) # размер монитора пользователя
scale = 20
pixelscale = 3
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
#endregion

#region [ОБЪЯВЛЕНИЕ ENTITY]
#region [BG]
def BG_create(target):
    target.image = None
    target.angle = 0
    target.offset = 8

def BG_step(target):
    target.angle = (target.angle+UPF(30)) % 360

def BG_draw_before(target, surface: pygame.Surface):
    #pygame.draw.circle(surface, 'yellow', (2, 2), 5.0)
    ox = engine.lengthdir_x(target.offset, target.angle)
    oy = engine.lengthdir_y(target.offset, target.angle)
    width = surface.get_width()
    height = surface.get_height()
    for x in ((-1, 0),(0, 1))[ox<0]:     # этот цикл отрисовывает картинку четырежды, чтобы в любом случае
        for y in ((-1, 0),(0, 1))[oy<0]: # замостить полностью холст. ((-1, 0),(0, 1))[ox<0] лишь оптимизирует это
            surface.blit(target.image, (ox + (x*width),                                                  # - леша
                                        oy + (y*height)))

BG = engine.Entity(event_create=BG_create, event_step=BG_step, event_draw_before=BG_draw_before)
#endregion
#endregion

#region [ОБЪЯВЛЕНИЕ ENTITYGROUP]
eg_mainmenu = engine.EntityGroup([BG])
#endregion

#region [СОЗДАНИЕ INSTANCE]
bg1 = BG.instance()
bg1.image = img_bg
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


    screen.get_canvas().fill('black')
    eg_mainmenu.do_step(screen.get_canvas())
    screen.draw_screen()
    pygame.display.flip()
    clock.tick(FPS)
#endregion