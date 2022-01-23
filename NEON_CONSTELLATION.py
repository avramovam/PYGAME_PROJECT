import pygame
import engine
from math import floor, ceil, sin, radians
from typing import Union, Tuple
from random import randint

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
    Andrey Avramov                                                                                       #16
    Daria Stolyarova                                                                              23.01.2022
''')

pygame.init()
engine.SCREENSIZE = engine.get_screensize(engine.pygame_videoinfo()) # размер монитора пользователя
scale = 40
pixelscale = 2
screen = engine.Screen((16*scale, 9*scale), (16*scale*pixelscale, 9*scale*pixelscale), 0, 1)
clock = pygame.time.Clock()
FPS = 60

img_bg = pygame.transform.scale(engine.load_image('bg.png'), (screen.get_canvas_width()*1, screen.get_canvas_height()*1))
img_player_battle = engine.load_image('player_battle.png')
mask_player_battle = pygame.mask.from_surface(img_player_battle)
img_board_enemy0 = engine.load_image('board_enemy0.png')
img_board_enemy1 = engine.load_image('board_enemy1.png')
img_bullet_test = engine.load_image('bullet_test.png')
mask_bullet = pygame.mask.from_surface(img_bullet_test)

img_boss = engine.load_image('boss.png')
mask_boss = pygame.mask.from_surface(img_boss)
img_enemy0 = engine.load_image('enemy0_idle.png')
mask_enemy0 = pygame.mask.from_surface(img_enemy0)
img_enemy1 = engine.load_image('enemy1_idle.png')
mask_enemy1 = pygame.mask.from_surface(img_enemy1)

img_instructions = engine.load_image('instructions.png')
img_objective = engine.load_image('objective.png')
img_portal = engine.load_image('portal.png')
img_credit = engine.load_image('credit.png')

sfx_detected = pygame.mixer.Sound('data/sfx_detected.wav')
sfx_detected.set_volume(0.5)
sfx_buy = pygame.mixer.Sound('data/sfx_purchase.wav')
sfx_buy.set_volume(0.5)
sfx_nobuy = pygame.mixer.Sound('data/sfx_failed_purchase.wav')
sfx_nobuy.set_volume(0.5)
sfx_hurt = pygame.mixer.Sound('data/sfx_hurt.wav')
sfx_hurt.set_volume(0.25)
sfx_death = pygame.mixer.Sound('data/sfx_death.wav')
sfx_death.set_volume(0.5)

def UPF(units_per_second):
    '''Сокращение функции engine.speed_upf, которая возвращает скорость "еденицы в кадр",
       имея скорость "еденицы в секунду" и количество кадров в секунду.
       Использовать в ежекадровых функциях где считается время или двигаются объекты.'''
    return engine.speed_upf(units_per_second, FPS)

def sign(x):
    'Возвращает 1 со знаком числа x. Если x = 0, то возвращает 0.'
    return (0 if x == 0 else (2*(x > 0))-1)

font_default = pygame.font.Font(None, 24)
font_small =   pygame.font.Font(None, 18)
font_heading = pygame.font.SysFont('yugothic', 48, False, False)

def instance_render_text(target):
    '''Рендерит текст для target если есть target.string и target.font.
       target.text содержит отрендеренные строчки текста.'''
    target.text = []
    for line in target.string.split('\n'):
        target.text.append(target.font.render(line, True, target.text_color))
#endregion

#region [ОБЪЯВЛЕНИЕ ENTITY]
#region [GLOBAL CHEATS]
def GlobalCheats_create(target):
    target.keys = {pygame.K_LALT: False,
                   pygame.K_RALT: False}

def GlobalCheats_draw_after(target, surface: pygame.Surface):
    if cheats_enabled:
        draw_text('ЧИТЫ ВКЛЮЧЕНЫ', surface,
                  (4, 4),
                  8, 'white',
                  centered=False)
    if cheats_nodetect:
        draw_text('NODETECT', surface,
                  (4, 4+10),
                  8, 'white',
                  centered=False)

def GlobalCheats_kb_pressed(target, buttonid):
    global cheats_nodetect, cheats_enabled, money
    target.keys[buttonid] = True
    if target.keys[pygame.K_LALT] or target.keys[pygame.K_RALT]:
        if buttonid == pygame.K_RETURN: # вкл/выкл читы
            cheats_enabled = not cheats_enabled
        if cheats_enabled: # остальное пока читы включены
            if buttonid == pygame.K_n: # незаметность
                cheats_nodetect = not cheats_nodetect
            if buttonid == pygame.K_m: # деньгииииии
                money += 100
                sfx_buy.play()
            if buttonid == pygame.K_d: # урон
                BattlePlayer_got_hurt(bplayer)

def GlobalCheats_kb_released(target, buttonid):
    target.keys[buttonid] = False

EntGlobalCheats = engine.Entity(event_create=GlobalCheats_create,
                                event_draw_after=GlobalCheats_draw_after,
                                event_kb_pressed=GlobalCheats_kb_pressed,
                                event_kb_released=GlobalCheats_kb_released)
#endregion
#region [GLOBAL CREDITS]
def GlobalCredits_create(target):
    target.font = font_default

def GlobalCredits_draw_after(target, surface: pygame.Surface):
    text = target.font.render(str(money), False, 'white')
    ox1 = surface.get_width() - text.get_width() - 16
    oy1 = surface.get_height() - text.get_height() - 4
    ox2 = surface.get_width() - 12
    oy2 = surface.get_height() - 18
    surface.blit(text, (ox1, oy1))
    surface.blit(img_credit, (ox2, oy2))

EntGlobalCredits = engine.Entity(event_create=GlobalCredits_create,
                                 event_draw_after=GlobalCredits_draw_after)
#endregion
#region [MAINMENU BG]
def MainMenuBG_create(target):
    target.image = None
    target.angle = 0
    target.offset = 8

def MainMenuBG_step(target):
    target.angle = (target.angle+UPF(30)) % 360

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

EntMainMenuBG = engine.Entity(event_create=MainMenuBG_create, event_step=MainMenuBG_step,
                              event_draw_before=MainMenuBG_draw_before)
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
    if not settings.show and not instr.show:
        instr.show = 1

def MainMenuButton_user1(): # Настройки
    if not settings.show and not instr.show:
        settings.show = 1

def MainMenuButton_user2(): # Выход
    if not settings.show and not instr.show:
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
    pygame.draw.rect(surface, 'white', rect_coords, 0, rounding) # задник
    pygame.draw.rect(surface, 'gray',  rect_coords, 3, rounding) # обводка задника
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
#region [MAINMENU INSTRUCTIONS]
def MainMenuInstr_create(target):
    target.show = 0
    target.show_step = 0
    target.gotofield = 0
    target.gotofield_step = 0
    target.image = img_instructions
    # target.image = pygame.Surface((600, 150), pygame.SRCALPHA)
    # target.image.fill('purple')

    target.mybutton_x1, target.mybutton_y = 0, 0
    target.font = font_default
    target.string1 = 'Поехали!'
    target.text_color = 'black'

    target.mybutton_x2, target.mybutton_y = 0, 0
    target.font = font_default
    target.string2 = 'Я не готов'
    target.text_color = 'black'

    target.text1 = target.font.render(target.string1, True, target.text_color)
    target.text2 = target.font.render(target.string2, True, target.text_color)

    target.font = font_small
    target.text_color = 'white'
    target.i_strings = ['Инструкция',
                                  ['Вы - космический пират,',
                                   'и ваш путь идет через',
                                   'космическое поле.',
                                   'Избегайте военные',
                                   'корабли, иначе вы',
                                   'вступите с ними в бой.'],
                                  ['Ваша задача - достичь',
                                   'торговый корабль',
                                   '"Небесный" чтобы',
                                   'ограбить его! После',
                                   'ограбления, следуйте',
                                   'в пункт сверхзвуковой',
                                   'переброски, чтобы',
                                   'продвинуться на',
                                   'следующий уровень.'],
                                  ['В бою вам необходимо',
                                   'избегать вражеские',
                                   'пули и самому',
                                   'атаковать врага.',
                                   'Ваш корабль стреляет',
                                   'по вражескому',
                                   'автоматически, пока он',
                                   'напротив него.'],
                                  ['Во время сверхзвуковой',
                                   'переброски у вас есть',
                                   'время чтобы купить',
                                   'улучшения для вашего',
                                   'корабля.']]

    target.instructions = [font_default.render(target.i_strings[0], True, target.text_color), [], [], [], []]
    for i in range(1, len(target.i_strings)):
        for j in range(len(target.i_strings[i])):
            target.instructions[i].append(target.font.render(target.i_strings[i][j], True, target.text_color))

def MainMenuInstr_step(target):
    if target.show:
        target.show_step = engine.clamp(target.show_step+UPF(1), 0, 1)
    else:
        target.show_step = engine.clamp(target.show_step-UPF(1), 0, 1)

    if target.gotofield:
        target.gotofield_step += UPF(1/2) # полный переход за 2 секунды
    if target.gotofield_step >= 1:
        engine.rooms.change_current_room(room_field)
        FieldBoard_init_level(fboard)

def MainMenuInstr_draw_after(target, surface: pygame.Surface):
    width = surface.get_width()
    height = surface.get_height()

    showphase = sin(radians(target.show_step * 90))

    # ЗАТЕНЕНИЕ
    faded = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    faded.fill((0,0,0,255 * showphase * 0.65))
    surface.blit(faded, (0,0))

    # ИНСТРУКЦИЯ
    if target.image is not None:
        image_width = target.image.get_width()
        image_height = target.image.get_height()
        surface.blit(target.image, (width//2 - image_width//2, height//2 - image_height//2 + 512 - 576*showphase))
        #pygame.draw.rect(surface, 'purple', (surface.get_width()//2 - 200))

        # ТЕКСТ
        tw = target.instructions[0].get_width()
        th = target.instructions[0].get_height()
        surface.blit(target.instructions[0], (width//2 - tw//2, 16 + 512 - 512*showphase))
        for x in range(1, len(target.instructions)):
            xoffset = width//2 + (x-2.5)*160
            for y in range(len(target.instructions[x])):
                yoffset = height//2 + image_height//2 - 48 + (y*14) + 512 - 512*showphase
                tw = target.instructions[x][y].get_width()
                th = target.instructions[x][y].get_height()
                surface.blit(target.instructions[x][y], (xoffset - tw//2, yoffset - th//2))

    # КНОПКИ
    target.mybutton_x1 = width//2 - 256
    target.mybutton_x2 = width//2 + 256
    target.mybutton_y = height - 32 + 160 - 160*showphase

    tw = target.text1.get_width()
    th = target.text1.get_height()
    fs = 16  # размер поля между прямоугольником и текстом
    rect_coords = (target.mybutton_x1 - ((tw + fs) // 2), target.mybutton_y - ((th + fs) // 2), tw + fs, th + fs)
    text_coords = (target.mybutton_x1 - (tw // 2), target.mybutton_y - (th // 2))
    rounding = 4  # величина скругления задника
    pygame.draw.rect(surface, 'white', rect_coords, 0, rounding)  # задник
    pygame.draw.rect(surface, 'gray', rect_coords, 3, rounding)  # обводка задника
    surface.blit(target.text1, text_coords)

    tw = target.text2.get_width()
    th = target.text2.get_height()
    rect_coords = (target.mybutton_x2 - ((tw + fs) // 2), target.mybutton_y - ((th + fs) // 2), tw + fs, th + fs)
    text_coords = (target.mybutton_x2 - (tw // 2), target.mybutton_y - (th // 2))
    pygame.draw.rect(surface, 'white', rect_coords, 0, rounding)  # задник
    pygame.draw.rect(surface, 'gray', rect_coords, 3, rounding)  # обводка задника
    surface.blit(target.text2, text_coords)

    # КРУГ
    half_diagonal = (((width ** 2) + (height ** 2)) ** 0.5) / 2
    circle_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    circle_surface2 = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    circle_surface.fill('black')
    pygame.draw.circle(circle_surface2, 'black', (width / 2, height / 2),
                       half_diagonal * (max(0, 1.4 * (1 - target.gotofield_step) - 0.4)), 0)
    circle_surface.blit(circle_surface2, (0, 0), None, pygame.BLEND_RGBA_SUB)
    surface.blit(circle_surface, (0, 0), None)

def MainMenuInstr_mouse_pressed(target, mousepos, buttonid):
    tw1 = target.text1.get_width()
    th1 = target.text1.get_height()
    tw2 = target.text2.get_width()
    th2 = target.text2.get_height()
    fs = 16  # размер поля между прямоугольником и текстом
    xrange1 = target.mybutton_x1 - ((tw1 + fs) // 2) <= mousepos[0] <= target.mybutton_x1 + ((tw1 + fs) // 2)
    xrange2 = target.mybutton_x2 - ((tw2 + fs) // 2) <= mousepos[0] <= target.mybutton_x2 + ((tw2 + fs) // 2)
    yrange1 = target.mybutton_y - ((th1 + fs) // 2) <= mousepos[1] <= target.mybutton_y + ((th1 + fs) // 2)
    yrange2 = target.mybutton_y - ((th2 + fs) // 2) <= mousepos[1] <= target.mybutton_y + ((th2 + fs) // 2)
    if xrange1 and yrange1:
        target.gotofield = 1
    if xrange2 and yrange2:
        target.show = 0

def MainMenuInstr_room_start(target):
    pygame.mixer.music.load('data/mainmenu.mp3')
    pygame.mixer.music.play(-1)
    target.show = 0
    target.show_step = 0
    target.gotofield = 0
    target.gotofield_step = 0

EntMainMenuInstr = engine.Entity(event_create=MainMenuInstr_create, event_step=MainMenuInstr_step,
                                 event_draw_after=MainMenuInstr_draw_after,
                                 event_mouse_pressed=MainMenuInstr_mouse_pressed,
                                 event_room_start=MainMenuInstr_room_start)
#endregion
#region [MAINMENU SETTINGS]
def MainMenuSettings_create(target):
    target.show = 0
    target.show_step = 0

    target.text1 = font_default.render('Громкость', False, 'white')
    target.text2 = font_default.render('Режим отображения', False, 'white')
    target.text3 = font_default.render('Оконный режим', False, 'black')
    target.text4 = font_default.render('Назад', False, 'black')

def MainMenuSettings_step(target):
    if target.show:
        target.show_step = engine.clamp(target.show_step+UPF(1), 0, 1)
    else:
        target.show_step = engine.clamp(target.show_step-UPF(1), 0, 1)

def MainMenuSettings_draw_after(target, surface: pygame.Surface):
    width, height = surface.get_size()

    showphase = sin(radians(target.show_step * 90))

    # ЗАТЕНЕНИЕ
    faded = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    faded.fill((0, 0, 0, 255 * showphase * 0.65))
    surface.blit(faded, (0, 0))

    # ТЕКСТА
    tw1, th1 = target.text1.get_size()
    tw2, th2 = target.text2.get_size()
    surface.blit(target.text1, ((surface.get_width() - tw1)//2 - 512 + (512*showphase), surface.get_height()//2 - 96))
    surface.blit(target.text2, ((surface.get_width() - tw2)//2 + 512 - (512*showphase), surface.get_height()//2 + 48))

    # КНОПКА
    tw3, th3 = target.text3.get_size()
    fs = 16
    button1_x = screen.get_canvas_halfwidth() + 512 - (512 * showphase)
    button1_y = screen.get_canvas_halfheight() + 96
    rect_coords = (button1_x - ((tw3 + fs) // 2), button1_y - ((th3 + fs) // 2), tw3 + fs, th3 + fs)
    text_coords = (button1_x - (tw3 // 2), button1_y - (th3 // 2))
    rounding = 4  # величина скругления задника
    pygame.draw.rect(surface, 'white', rect_coords, 0, rounding)  # задник
    pygame.draw.rect(surface, 'gray', rect_coords, 3, rounding)  # обводка задника
    surface.blit(target.text3, text_coords)

    tw4, th4 = target.text4.get_size()
    button2_x = screen.get_canvas_halfwidth()
    button2_y = screen.get_canvas_height() - 32 + 128 - (128 * showphase)
    rect_coords = (button2_x - ((tw4 + fs) // 2), button2_y - ((th4 + fs) // 2), tw4 + fs, th4 + fs)
    text_coords = (button2_x - (tw4 // 2), button2_y - (th4 // 2))
    pygame.draw.rect(surface, 'white', rect_coords, 0, rounding)  # задник
    pygame.draw.rect(surface, 'gray', rect_coords, 3, rounding)  # обводка задника
    surface.blit(target.text4, text_coords)

def MainMenuSettings_mouse_pressed(target, mousepos, buttonid):
    global show_mode
    showphase = sin(radians(target.show_step * 90))

    fs = 16
    tw, th = target.text3.get_size()
    xd, yd = (tw+fs)//2, (th+fs)//2

    button1_x = screen.get_canvas_halfwidth() + 512 - (512*showphase)
    button1_y = screen.get_canvas_halfheight() + 96

    xrange1 = button1_x - xd <= mousepos[0] <= button1_x + xd
    yrange1 = button1_y - yd <= mousepos[1] <= button1_y + yd

    button2_x = screen.get_canvas_halfwidth()
    button2_y = screen.get_canvas_height() - 32 + 128 - (128*showphase)

    xrange2 = button2_x - xd <= mousepos[0] <= button2_x + xd
    yrange2 = button2_y - yd <= mousepos[1] <= button2_y + yd

    if (xrange1 and yrange1):
        if show_mode == 0: # оконный -> полный экран
            target.text3 = font_default.render('На весь экран', False, 'black')
            show_mode = 1
            screen.update_screen(engine.SCREENSIZE, fullscreen_mode=1, resizable_mode=False)

        elif show_mode == 1:  # полный экран -> оконный
            target.text3 = font_default.render('Оконный режим', False, 'black')
            show_mode = 0
            screen.update_screen((16 * scale * pixelscale, 9 * scale * pixelscale), fullscreen_mode=0,
                                 resizable_mode=True)

        # if show_mode == 0: # оконный -> оконный на весь экран
        #     target.text3 = font_default.render('Оконный на весь экран', False, 'black')
        #     show_mode = 1
        #     screen.update_screen(fullscreen_mode=2, resizable_mode=False)
        #
        # elif show_mode == 1: # оконный на весь экран -> полный экран
        #     target.text3 = font_default.render('На весь экран', False, 'black')
        #     show_mode = 2
        #     screen.update_screen(fullscreen_mode=1, resizable_mode=False)
        #
        # elif show_mode == 2: # полный экран -> оконный
        #     target.text3 = font_default.render('Оконный режим', False, 'black')
        #     show_mode = 0
        #     screen.update_screen((16*scale*pixelscale, 9*scale*pixelscale), fullscreen_mode=0, resizable_mode=True)

    if (xrange2 and yrange2):
        target.show = 0

EntMainMenuSettings = engine.Entity(event_create=MainMenuSettings_create,
                                    event_step=MainMenuSettings_step,
                                    event_draw_after=MainMenuSettings_draw_after,
                                    event_mouse_pressed=MainMenuSettings_mouse_pressed)
#endregion
#region [FIELD BG]
def FieldBG_create(target):
    target.image = None
    target.angle = 0
    target.offset = 128
    target.fadeout = 1
    #target.x = 0
    #target.y = 0

def FieldBG_draw_before(target, surface):
    if engine.rooms.current_room == room_field:
        ox = target.offset * (1 - (fplayer.x/screen.get_canvas_width()))
        oy = target.offset * (1 - (fplayer.y/screen.get_canvas_height()))
    elif engine.rooms.current_room == room_battle:
        ox = target.offset * (1 - (bplayer.x / screen.get_canvas_width()))
        oy = target.offset * (1 - (bplayer.y / screen.get_canvas_height()))
    else:
        ox = 0
        oy = 0
    width = surface.get_width()
    height = surface.get_height()
    for x in ((-1, 0), (0, 1))[ox < 0]:  # этот цикл отрисовывает картинку четырежды, чтобы в любом случае
        for y in ((-1, 0), (0, 1))[oy < 0]:  # замостить полностью холст. ((-1, 0),(0, 1))[ox<0] лишь оптимизирует это
            surface.blit(target.image, (ox + (x * width),  # - леша
                                        oy + (y * height)))

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

def FieldBoard_init_level(target): # расположение штук на поле
    global hp, maxhp
    ucfe = [] # unused_coords_for_enemies - координаты всем и всям уникальные
    for x in range(0, target.cellcount_x):
        for y in range(4, target.cellcount_y-3):
            ucfe.append((x, y))
    # создать 7 противников
    for j in range(7):
        i = EntFieldEnemy.instance()
        i.cellx, i.celly = ucfe.pop(randint(0, len(ucfe)-1))
        i.enemyid = randint(0, 4)
        i.pl_ins = fplayer
        i.detect_method = (FieldEnemy_detect0, FieldEnemy_detect1,
                           FieldEnemy_detect2, FieldEnemy_detect3, FieldEnemy_detect4)[i.enemyid]
        if i.detect_method == FieldEnemy_detect0:
            i.detect_phase = randint(0, 3)
        i.image = (img_board_enemy0, img_board_enemy1,
                   img_board_enemy0, img_board_enemy1, img_board_enemy0)[i.enemyid]
        i.myboard = target
    # создать босса
    i = EntFieldBoss.instance()
    i.cellx, i.celly = randint(0, target.cellcount_x-1), randint(0, 3)
    i.pl_ins = fplayer
    i.myboard = target
    # создать портал
    fportal.cellx, fportal.celly = randint(0, target.cellcount_x-1), randint(target.cellcount_y-1-2, target.cellcount_y-1)
    fportal.gotoshop_step = 0
    fportal.gotoshop = False
    # переместить игрока, исцелить
    fplayer.cellx = randint(0, target.cellcount_x-1)
    fplayer.celly = randint(target.cellcount_y-1-2, target.cellcount_y-1)
    hp = maxhp
    # надпись цикла
    target.cycle = font_default.render(f'Цикл {cycle}', False, 'white')

def FieldBoard_create(target):
    target.cellsize = 20
    target.cellcount_x = 15
    target.cellcount_y = 15
    # target.start_x = 0
    # target.start_y = 0
    target.width = ((target.cellsize+1) * target.cellcount_x) + 1
    target.height = ((target.cellsize+1) * target.cellcount_y) + 1
    FieldBoard_user0(target, screen.get_canvas())
    target.boardalpha = 0.6 # уровень прозрачности от 0 (полностью прозрачный) до 1 (полностью видимый)
    target.detected = False  # это на случай замечания
    target.moving_to_battle = 0  # переход - 0..1

    target.board_surface = pygame.Surface((target.width, target.height), pygame.SRCALPHA)
    target.board_surface.fill((0, 0, 0, 0))
    # попиксельное отрисовывание сетки хехехехехехехехехе ужас
    cellsize_with_border = target.cellsize + 1
    for px in range(target.width):
        for py in range(target.height):
            if py % cellsize_with_border == 0:  # линия по горизонтали
                minimal = floor(px / cellsize_with_border) * cellsize_with_border  # близжайшее левое пересечение линий
                maximal = ceil(px / cellsize_with_border) * cellsize_with_border  # близжайшее правое пересечение линий

                if minimal == maximal:  # мы находимся на пересечении
                    alpha = 1
                else:
                    alpha = max(abs(minimal - px), abs(maximal - px)) / cellsize_with_border
                    alpha = 2 * (alpha - 0.5)
                # alpha *= max(0, 1-target.moving_to_battle)
                target.board_surface.set_at((px, py), (255, 255, 255, 255 * alpha * target.boardalpha))
            elif px % cellsize_with_border == 0:  # линия по горизонтали
                minimal = floor(
                    py / cellsize_with_border) * cellsize_with_border  # близжайшее верхнее пересечение линий
                maximal = ceil(py / cellsize_with_border) * cellsize_with_border  # близжайшее нижнее пересечение линий

                if minimal == maximal:  # мы находимся на пересечении
                    alpha = 1
                else:
                    alpha = max(abs(minimal - py), abs(maximal - py)) / cellsize_with_border
                    alpha = 2 * (alpha - 0.5)
                # alpha *= max(0, 1-target.moving_to_battle)
                target.board_surface.set_at((px, py), (255, 255, 255, 255 * alpha * target.boardalpha))


def FieldBoard_step(target):
    if target.detected:
        if target.moving_to_battle >= 1:
            engine.rooms.change_current_room(room_battle)
        else:
            if target.moving_to_battle == 0: # только начал двигаться
                pygame.mixer.music.stop()
                sfx_detected.play()
            target.moving_to_battle += UPF(2) # продвинется за 0.5 секунды


def FieldBoard_draw_before(target, surface: pygame.Surface):
    surface.blit(target.board_surface, (target.start_x, target.start_y))

def FieldBoard_draw_after(target, surface: pygame.Surface):
    phase = sin(radians(min(90, 180 * target.moving_to_battle)))
    draw_text('!', surface, [surface.get_width() // 2, surface.get_height() // 2], round(128 * phase), 'red',
              'yugothic', True)
    surface.blit(target.cycle, (surface.get_width() - target.cycle.get_width() - 4, 4))

def FieldBoard_room_start(target):
    target.detected = False
    target.moving_to_battle = 0

EntFieldBoard = engine.Entity(event_create=FieldBoard_create, event_step=FieldBoard_step,
                              event_draw_before=FieldBoard_draw_before, event_draw_after=FieldBoard_draw_after,
                              event_room_start=FieldBoard_room_start)
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
    if not target.myboard.detected:
        if buttonid == pygame.K_LEFT:
            target.cellx = engine.clamp(target.cellx - 1, 0, target.myboard.cellcount_x-1)
            target.nextcellx = target.cellx - 1
            target.nextcelly = target.celly
            for ins in EntFieldEnemy.instances:
                ins.detect_phase = (ins.detect_phase + 1) % 4
                FieldEnemy_change_pos(ins)
        elif buttonid == pygame.K_RIGHT:
            target.cellx = engine.clamp(target.cellx + 1, 0, target.myboard.cellcount_x-1)
            target.nextcellx = target.cellx + 1
            target.nextcelly = target.celly
            for ins in EntFieldEnemy.instances:
                ins.detect_phase = (ins.detect_phase + 1) % 4
                FieldEnemy_change_pos(ins)
        elif buttonid == pygame.K_UP:
            target.celly = engine.clamp(target.celly - 1, 0, target.myboard.cellcount_y-1)
            target.nextcellx = target.cellx
            target.nextcelly = target.celly - 1
            for ins in EntFieldEnemy.instances:
                ins.detect_phase = (ins.detect_phase + 1) % 4
                FieldEnemy_change_pos(ins)
        elif buttonid == pygame.K_DOWN:
            target.celly = engine.clamp(target.celly + 1, 0, target.myboard.cellcount_y-1)
            target.nextcellx = target.cellx
            target.nextcelly = target.celly + 1
            for ins in EntFieldEnemy.instances:
                ins.detect_phase = (ins.detect_phase + 1) % 4
                FieldEnemy_change_pos(ins)

def FieldPlayer_room_start(target):
    pygame.mixer.music.load('data/onfield.mp3')
    pygame.mixer.music.play(-1)
    target.x, target.y = mylastpos_inbattle
    target.image_angle = mylastrot_inbattle

def FieldPlayer_room_end(target):
    global mylastpos_onfield, mylastrot_onfield
    mylastpos_onfield = target.x, target.y
    mylastrot_onfield = target.image_angle

EntFieldPlayer = engine.Entity(event_create=FieldPlayer_create, event_step=FieldPlayer_step,
                               event_draw=FieldPlayer_draw,
                               event_kb_pressed=FieldPlayer_kb_pressed,
                               event_room_start=FieldPlayer_room_start,
                               event_room_end=FieldPlayer_room_end)
#endregion
#region [FIELD ENEMY]
def FieldEnemy_detect_test(myx, myy, playerx, playery, phase): # тестовый вариант - крест
    return (myx == playerx) or (myy == playery)

def FieldEnemy_detect0(myx, myy, playerx, playery, phase): # луч
    if phase == 0:
        return (myx == playerx) and (myy <= playery)
    elif phase == 1:
        return (myx >= playerx) and (myy == playery)
    elif phase == 2:
        return (myx == playerx) and (myy >= playery)
    elif phase == 3:
        return (myx <= playerx) and (myy == playery)

def FieldEnemy_detect1(myx, myy, playerx, playery, phase): # радиус-3-крест
    return ((myx == playerx) or (myy == playery)) and ((abs(playerx-myx)+abs(playery-myy)) <= 3)

def FieldEnemy_detect2(myx, myy, playerx, playery, phase): # ежетрехфазовый ферзь
    if phase == 0:
        return False
    if phase == 1:
        return (abs(myx-playerx) == 0) and (abs(myy-playery) == 0)
    if phase == 2:
        return (abs(myx-playerx) <= 1) and (abs(myy-playery) <= 1)
    if phase == 3:
        return (myx == playerx) or (myy == playery) or (abs(playerx-myx) == abs(playery-myy))

def FieldEnemy_detect3(myx, myy, playerx, playery, phase): # круговая мина
    return (abs(myx-playerx) <= 1) and (abs(myy-playery) <= 1)

def FieldEnemy_detect4(myx, myy, playerx, playery, phase): # сфера
    dx = abs(myx-playerx)
    dy = abs(myy-playery)
    return (dx+dy <= 3) and not (dx >= 3 or dy >= 3)

def FieldEnemy_change_pos(target):
    if target.detect_method == FieldEnemy_detect0:
        target.image_angle = (-90*target.detect_phase) % 360
    if target.detect_method == FieldEnemy_detect3:
        if target.detect_phase == 0:
            target.celly += 1
            target.image_angle = 180
        elif target.detect_phase == 1:
            target.cellx -= 1
            target.image_angle = 90
        elif target.detect_phase == 2:
            target.celly -= 1
            target.image_angle = 0
        elif target.detect_phase == 3:
            target.cellx += 1
            target.image_angle = 270

def FieldEnemy_create(target):
    target.image = None
    target.image_angle = 0
    target.cellx = 0
    target.celly = 0
    target.x = 0
    target.y = 0
    target.xto = 0
    target.yto = 0
    target.angleto = 0 # к какому углу направляться
    target.myboard = None
    target.detect_method = None
    '''    ^^^^^^^^^^^^^   сие метод обнаружения игрока (присвоить функцию с аргументами myx, myy, playerx, playery
       которая возвращает bool - обнаруживает ли игрока когда игрок на координатах (playerx;playery) и
       когда fieldenemy на координатах (myx;myy))'''
    target.enemyid = 1
    '''    ^^^^^^^   сие ID вражеского корабля, с которым игрок вступает в бой при обнаружении игрока'''
    target.detect_phase = 0
    target.pl_ins = None # instance-экземпляр игрока
    target.detect_color = pygame.Color(255, 0, 0, 55)
    target.detect_color.hsva = (randint(-30, 30) % 360, 100, 50, 55)

def FieldEnemy_step(target):
    global whodetected, enemyid
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

    if (target.myboard is not None) and (target.myboard.detected != True) and \
       (target.detect_method is not None) and (target.pl_ins is not None) and (not cheats_nodetect):
        if target.detect_method(target.cellx, target.celly,
                                target.pl_ins.cellx, target.pl_ins.celly,
                                target.detect_phase):
            target.myboard.detected = True # НАС АБНАРУЖИЛИ!!!!!!1
            enemyid = target.enemyid # НАС ЩАС УБИВАТЬ БУДУТ!!!1
            whodetected = target

def FieldEnemy_draw(target, surface: pygame.Surface):
    mysurface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    # далее подсветка клеток, которые входят в поле обнаружения
    if (target.myboard is not None) and (target.detect_method is not None):
        cs = target.myboard.cellsize
        ox, oy = target.myboard.start_x + 1, target.myboard.start_y + 1
        for cx in range(target.myboard.cellcount_x):
            for cy in range(target.myboard.cellcount_y):
                if target.detect_method(target.cellx, target.celly, cx, cy, target.detect_phase):
                    pygame.draw.rect(mysurface, target.detect_color, (ox, oy, cs, cs))
                oy += cs + 1
            ox += cs + 1
            oy = target.myboard.start_y + 1
    surface.blit(mysurface, (0,0))
    FieldPlayer_draw(target, surface) # отрисовка идентична отрисовке игрока

def FieldEnemy_room_start(target):
    if whodetected == target:
        del EntFieldEnemy.instances[EntFieldEnemy.instances.index(target)]  # самоуничтожение

EntFieldEnemy = engine.Entity(event_create=FieldEnemy_create, event_step=FieldEnemy_step,
                              event_draw=FieldEnemy_draw, event_room_start=FieldEnemy_room_start)
#endregion
#region [FIELD BOSS]
def FieldBoss_create(target):
    target.image = img_objective
    target.image_angle = 0
    target.cellx = 0
    target.celly = 0
    target.x = 0
    target.y = 0
    target.angleto = 0 # к какому углу направляться
    target.myboard = None
    target.pl_ins = None # instance-экземпляр игрока

def FieldBoss_step(target):
    global whodetected, enemyid
    if target.myboard is not None:
        target.x, target.y = FieldBoard_get_cell_coords(target.myboard, target.cellx, target.celly) # получение left-top-края

    if (target.myboard is not None) and (target.myboard.detected != True) and (target.pl_ins is not None):
        if (target.cellx == target.pl_ins.cellx) and (target.celly == target.pl_ins.celly):
            target.myboard.detected = True # НАС АБНАРУЖИЛИ!!!!!!1
            enemyid = 5 # НАС ЩАС УБИВАТЬ БУДУТ!!!1
            whodetected = target

def FieldBoss_draw(target, surface: pygame.Surface):
    FieldPlayer_draw(target, surface) # отрисовка идентична отрисовке игрока
    mysurface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    # далее подсветка клеток, которые входят в поле обнаружения
    if (target.myboard is not None):
        cs = target.myboard.cellsize
        ox, oy = FieldBoard_get_cell_coords(target.myboard, target.cellx, target.celly)
        # ox = target.myboard.get_cell_coords(target.cellx, target.celly)
        pygame.draw.rect(mysurface, (255,155,0,55), (ox + 1, oy + 1, cs, cs))
    surface.blit(mysurface, (0,0))

def FieldBoss_room_start(target):
    if whodetected == target:
        del EntFieldBoss.instances[EntFieldBoss.instances.index(target)]  # самоуничтожение

EntFieldBoss = engine.Entity(event_create=FieldBoss_create, event_step=FieldBoss_step,
                              event_draw=FieldBoss_draw, event_room_start=FieldBoss_room_start)
#endregion
#region [FIELD PORTAL]
def FieldPortal_create(target):
    target.image = img_portal
    target.image_alpha = target.image.copy() # прозрачный вариант
    target.image_alpha.fill((255, 255, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
    target.image_angle = 0
    target.cellx = 0
    target.celly = 0
    target.myboard = None
    target.pl_ins = None # instance-экземпляр игрока
    target.gotoshop_step = 0
    target.gotoshop = False

def FieldPortal_step(target):
    if killedboss and (target.cellx == target.pl_ins.cellx and
                       target.celly == target.pl_ins.celly): # активизируется только в случае если босс убит
        target.gotoshop = True
    target.image_angle = (target.image_angle + UPF(45)) % 360 # крутится на 45 градусов каждую секунду
    if target.gotoshop:
        if target.gotoshop_step >= 1:
            engine.rooms.change_current_room(room_shop)
        else:
            target.gotoshop_step += UPF(1/2)

def FieldPortal_draw(target, surface: pygame.Surface):
    myimage = pygame.transform.rotate(target.image if killedboss else target.image_alpha, target.image_angle)
    myimage_width = myimage.get_width()
    myimage_height = myimage.get_height()
    deltawidth = myimage_width - target.myboard.cellsize
    deltaheight = myimage_height - target.myboard.cellsize
    ox, oy = FieldBoard_get_cell_coords(target.myboard, target.cellx, target.celly)
    surface.blit(myimage,
                 (ox - deltawidth // 2 + 1,
                  oy - deltaheight // 2 + 1))

def FieldPortal_draw_after(target, surface: pygame.Surface):
    width, height = surface.get_size()
    # Круг как в главном меню
    half_diagonal = (((width ** 2) + (height ** 2)) ** 0.5) / 2
    circle_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    circle_surface2 = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    circle_surface.fill('black')
    pygame.draw.circle(circle_surface2, 'black', (width / 2, height / 2),
                       half_diagonal * (max(0, 1.4 * (1 - target.gotoshop_step) - 0.4)), 0)
    circle_surface.blit(circle_surface2, (0, 0), None, pygame.BLEND_RGBA_SUB)
    surface.blit(circle_surface, (0, 0), None)

EntFieldPortal = engine.Entity(event_create=FieldPortal_create,
                               event_step=FieldPortal_step,
                               event_draw=FieldPortal_draw,
                               event_draw_after=FieldPortal_draw_after)
#endregion
#region [BATTLE PLAYER]
def BattlePlayer_got_hurt(target): # попала пуля(
    global hp
    if target.invulner_time <= 0:
        target.invulner_time = 1
        if target.armor > 0:
            target.armor -= 1
        else:
            hp -= 1
        if hp > 0: # осталось >0 хп
            sfx_hurt.play()
        else:
            sfx_death.play()
            engine.rooms.change_current_room(room_mainmenu)
    return target.invulner_time <= 0

def BattlePlayer_create(target):
    target.x = 0 # где он щас
    target.y = 0 # где он щас
    target.image = img_player_battle
    # target.image_angle = 0
    target.keys = {'up': False,
                   'down': False,
                   'right': False,
                   'left': False}
    target.maxspeed = UPF(128)
    target.friction = target.maxspeed*UPF(10) # разгоняется за десятую секунды (наверное)
    target.hsp = 0
    target.vsp = 0
    target.shooting_delay = 0
    target.invulner_time = 0
    target.mask = mask_player_battle

    target.font = font_small
    target.string = 'Ваш корабль, RNP6'
    target.text_color = 'white'
    instance_render_text(target)

def BattlePlayer_step(target):
    horizontal_moving = target.keys['right']-target.keys['left']
    vertical_moving = target.keys['down']-target.keys['up']

    if horizontal_moving == 0:
        if target.hsp > 0:
            target.hsp = max(0, target.hsp-target.friction)
        else:
            target.hsp = min(0, target.hsp+target.friction)
    else:
        target.hsp += horizontal_moving*target.friction

    if vertical_moving == 0:
        if target.vsp > 0:
            target.vsp = max(0, target.vsp-target.friction)
        else:
            target.vsp = min(0, target.vsp+target.friction)
    else:
        target.vsp += vertical_moving*target.friction

    target.hsp = engine.clamp(target.hsp, -target.maxspeed, target.maxspeed)
    target.vsp = engine.clamp(target.vsp, -target.maxspeed, target.maxspeed)

    target.x += target.hsp
    target.y += target.vsp

    target.x = engine.clamp(target.x, 16, screen.get_canvas_width() - 16)
    target.y = engine.clamp(target.y, 16, screen.get_canvas_height() - 16)

    target.image_angle //= 2

    if target.shooting_delay <= 0:
        # BattlePlayer_got_hurt(target) # тест
        bullet = EntBattlePlBullet.instance()
        bullet.x = target.x
        bullet.y = target.y - 10
        target.shooting_delay = 1
    else:
        target.shooting_delay -= UPF(shootspeed)

    if target.invulner_time > 0:
        target.invulner_time -= UPF(1)

def BattlePlayer_draw(target, surface: pygame.Surface):
    # print(target.x, target.y, target.x + target.image.get_width()//2, target.y + target.image.get_height()//2)
    myimage = pygame.transform.rotate(target.image, target.image_angle)
    transparency = pygame.Surface(myimage.get_size(), pygame.SRCALPHA)
    transparency.fill((255, 255, 255, 255 - 150*ceil(target.invulner_time)))
    myimage.blit(transparency, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    circle = pygame.Surface((myimage.get_width()*4, myimage.get_height()*4), pygame.SRCALPHA)
    pygame.draw.circle(circle, 'red', (circle.get_width()//2, circle.get_height()//2), 32*target.invulner_time)
    surface.blit(circle, (target.x - circle.get_width()//2, target.y - circle.get_height()//2))
    surface.blit(myimage, (target.x - target.image.get_width()//2, target.y - target.image.get_height()//2))

    mysurface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    rectw = 128
    recth = 12
    rectx = surface.get_width()//2 - rectw//2
    recty = surface.get_height() - recth - 8
    pygame.draw.rect(mysurface, (55, 155, 55), (rectx, recty, rectw, recth)) # макс хп
    pygame.draw.rect(mysurface, (55, 255, 55), (rectx, recty, rectw * (hp / maxhp), recth)) # сколько хп
    if target.armor > 0:
        pygame.draw.rect(mysurface, (55, 155, 255),
                         (rectx, recty, rectw * (target.armor / maxhp), recth)) # сколько брони
    if maxhp < 50:
        for i in range(1, maxhp):
            ox = rectw*i/maxhp
            pygame.draw.line(mysurface, (35, 55, 35), (rectx+ox, recty), (rectx+ox, recty+recth-1)) # делящие палочки
    pygame.draw.rect(mysurface, 'black', (rectx, recty, rectw, recth), 1) # обводка
    mysurface.blit(target.text[0], (surface.get_width() // 2 - target.text[0].get_width() // 2,
                                    recty - target.text[0].get_height() - 4))
    paint_surface(mysurface, (255, 255, 255, 125), pygame.BLEND_RGBA_MULT)  # прозрачность
    surface.blit(mysurface, (0, 0))

def BattlePlayer_kb_pressed(target, buttonid):
    if buttonid == pygame.K_DOWN: target.keys['down'] = True
    if buttonid == pygame.K_UP: target.keys['up'] = True
    if buttonid == pygame.K_LEFT: target.keys['left'] = True
    if buttonid == pygame.K_RIGHT: target.keys['right'] = True

def BattlePlayer_kb_released(target, buttonid):
    if buttonid == pygame.K_DOWN: target.keys['down'] = False
    if buttonid == pygame.K_UP: target.keys['up'] = False
    if buttonid == pygame.K_LEFT: target.keys['left'] = False
    if buttonid == pygame.K_RIGHT: target.keys['right'] = False

def BattlePlayer_room_start(target):
    target.keys = {'up': False,
                   'down': False,
                   'right': False,
                   'left': False} # на всякий сбрашиваем клавишы
    pygame.mixer.music.load('data/fight.mp3')
    pygame.mixer.music.play(-1)
    target.x, target.y = mylastpos_onfield
    target.image_angle = mylastrot_onfield
    target.armor = maxarmor

def BattlePlayer_room_end(target):
    global mylastpos_inbattle, mylastrot_inbattle
    mylastpos_inbattle = target.x, target.y
    mylastrot_inbattle = target.image_angle

EntBattlePlayer = engine.Entity(event_create=BattlePlayer_create, event_step=BattlePlayer_step,
                                event_draw=BattlePlayer_draw,
                                event_kb_pressed=BattlePlayer_kb_pressed, event_kb_released=BattlePlayer_kb_released,
                                event_room_start=BattlePlayer_room_start,
                                event_room_end=BattlePlayer_room_end)
#endregion
#region [BATTLE PL BULLET]
def BattlePlBullet_create(target):
    target.x = 0
    target.y = 0
    target.direction = 90
    target.speed = UPF(150*bulletspeed)
    target.image = img_bullet_test
    target.mask = mask_bullet

def BattlePlBullet_step(target):
    target.x += engine.lengthdir_x(target.speed, target.direction)
    target.y += engine.lengthdir_y(target.speed, target.direction)

    if (not (0-16 < target.x < screen.get_canvas_width()+16)) or \
       (not (0-16 < target.y < screen.get_canvas_height()+16)): # за пределами экрана
        del EntBattlePlBullet.instances[EntBattlePlBullet.instances.index(target)] # самоуничтожение

def BattlePlBullet_step_after(target):
    if target in EntBattlePlBullet.instances:
        if target.mask.overlap(benemy.mask, (
        target.x - benemy.x - benemy.image.get_width() // 2, target.y - benemy.y)):  # попал в противника
            del EntBattlePlBullet.instances[EntBattlePlBullet.instances.index(target)]  # самоуничтожение

def BattlePlBullet_draw(target, surface: pygame.Surface):
    surface.blit(target.image, (target.x - target.image.get_width()//2, target.y - target.image.get_height()//2))

def BattlePlBullet_room_end(target):
    if target in EntBattlePlBullet.instances:
        del EntBattlePlBullet.instances[EntBattlePlBullet.instances.index(target)]  # самоуничтожение

EntBattlePlBullet = engine.Entity(event_create=BattlePlBullet_create,
                                  event_step=BattlePlBullet_step, event_step_after=BattlePlBullet_step_after,
                                  event_draw=BattlePlBullet_draw,
                                  event_room_end=BattlePlBullet_room_end)
#endregion
#region [BATTLE ENEMY]
def BattleEnemy_create(target):
    target.image = img_enemy0
    target.x = 0
    target.y = 0
    target.posphase = 0
    target.show_step = 0
    target.maxhp = 100
    target.hp = target.maxhp//2
    target.mask = mask_enemy0

    target.font = font_small
    target.string = 'Название корабля'
    target.text_color = 'white'

    instance_render_text(target)

    r = 16
    target.points = []
    for ang in range(0, 361):
        target.points.append((screen.get_canvas_halfwidth() + engine.lengthdir_x(r, ang),
                              screen.get_canvas_halfheight() + engine.lengthdir_y(r, ang)))

    target.gotofield_step = 0

def BattleEnemy_step(target):
    global killedboss
    target.show_step = engine.clamp(target.show_step+UPF(2), 0, 1)

    target.x = screen.get_canvas_halfwidth() + 128 * sin(radians(target.posphase))
    target.y = 64*target.show_step - 64

    target.posphase = (target.posphase + UPF(15)) % 360

    for bullet in EntBattlePlBullet.instances:
        if target.mask.overlap(mask_bullet, (target.x + target.image.get_width()//2 - bullet.x, target.y - bullet.y)):
            target.hp -= bulletdamage

    if target.hp <= 0:
        if enemyid == 5: # был босс
            killedboss = True
        if target.gotofield_step >= 1:
            engine.rooms.change_current_room(room_field)
        else:
            target.gotofield_step += UPF(1/4)

def BattleEnemy_draw(target, surface: pygame.Surface):
    if target.hp <= 0:
        ang = int(target.gotofield_step * len(target.points))
        if ang >= 2:
            pygame.draw.polygon(surface, 'white', target.points[:ang]+target.points[:ang][::-1], 3)

        text1 = font_default.render(str(ceil(4*(1-target.gotofield_step))), 0, 'white')
        surface.blit(text1, ((surface.get_width() - text1.get_width())//2,
                            (surface.get_height() - text1.get_height())//2))
        text2 = font_small.render('Возвращаем на поле...', 0, 'white')
        surface.blit(text2, ((surface.get_width() - text2.get_width())//2,
                            (surface.get_height() - text2.get_height())//2 + 32))
    else:
        surface.blit(target.image, (target.x - target.image.get_width()//2, target.y))

def BattleEnemy_draw_after(target, surface: pygame.Surface):
    mysurface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    rectw = 480
    recth = 12
    rectx = surface.get_width()//2 - rectw//2
    recty = 8
    pygame.draw.rect(mysurface, (155, 55, 55), (rectx,recty,rectw,recth))
    pygame.draw.rect(mysurface, (255, 55, 55), (rectx,recty,rectw*(target.hp/target.maxhp),recth))
    pygame.draw.rect(mysurface, 'black', (rectx,recty,rectw,recth), 1)
    mysurface.blit(target.text[0], (surface.get_width() // 2 - target.text[0].get_width() // 2, recty + recth + 2))
    paint_surface(mysurface, (255,255,255,125), pygame.BLEND_RGBA_MULT) # прозрачность
    surface.blit(mysurface, (0, 0))

def BattleEnemy_room_start(target):
    print(enemyid)
    if enemyid == 5: # босс / Небесный
        target.image = img_boss
        target.mask = mask_boss
    elif enemyid == 0: # синий
        target.image = img_enemy0
        target.mask = mask_enemy0
    elif enemyid == 1: # черный
        target.image = img_enemy1
        target.mask = mask_enemy1
    elif enemyid == 2: # ???
        target.image = img_enemy0
        target.mask = mask_enemy0
    elif enemyid == 3: # ???
        target.image = img_enemy1
        target.mask = mask_enemy1
    elif enemyid == 4: # ???
        target.image = img_enemy0
        target.mask = mask_enemy0
    target.string = enemyname[enemyid]
    instance_render_text(target)

    target.maxhp = 100
    target.hp = target.maxhp // 2
    target.gotofield_step = 0
    target.posphase = 0
    target.show_step = 0

EntBattleEnemy = engine.Entity(event_create=BattleEnemy_create, event_step=BattleEnemy_step,
                               event_draw=BattleEnemy_draw, event_draw_after=BattleEnemy_draw_after,
                               event_room_start=BattleEnemy_room_start)
#endregion
#region [BATTLE EN BULLET]
EntBattleEnBullet = engine.Entity()
#endregion
#region [SHOP BG]
def ShopBG_create(target):
    target.image = pygame.Surface(img_bg.get_size(), pygame.SRCALPHA)
    target.image.blit(img_bg, (0, 0))
    target.image.fill((100, 100, 100, 255), special_flags=pygame.BLEND_RGBA_MULT)
    target.image = pygame.transform.scale(target.image,
                                          (target.image.get_width()**2 / target.image.get_height(),
                                           target.image.get_width())) # растягиваем так чтобы помещалась в экран
    target.angle = 0

def ShopBG_step(target):
    target.angle = (target.angle+UPF(5)) % 360

def ShopBG_draw_before(target, surface: pygame.Surface):
    myimage = pygame.transform.rotate(target.image, target.angle)
    ox = (surface.get_width()/2)-(myimage.get_width()/2)
    oy = (surface.get_height()/2)-(myimage.get_height()/2)
    surface.blit(myimage, (ox, oy))

EntShopBG = engine.Entity(event_create=ShopBG_create,
                          event_step=ShopBG_step,
                          event_draw_before=ShopBG_draw_before)
#endregion
#region [SHOP BUTTON]
def ShopButton_text0():
    return ['Увеличивает',
            'максимальное',
            'здоровье вашего',
            'корабля на',
            '1 ячейку.',
            f'Сейчас {maxhp} MAXHP.']

def ShopButton_text1():
    return ['Увеличивает',
            'частоту стрельбы',
            'на 50%.',
            f'Сейчас {int(20*shootspeed)}%.']

def ShopButton_text2():
    return ['Увеличивает',
            'количество брони.',
            'Броня',
            'восстановляется',
            'перед каждой',
            'битвой. Брони не',
            'может быть больше',
            'чем макс. здоровье.',
            f'Сейчас {maxarmor} ARMOR.']

def ShopButton_user0(target): # hp
    global money, maxhp, hp
    if money >= target.cost:
        sfx_buy.play()
        money -= target.cost
        maxhp += 1
        hp += 1
        target.cost += 15
    else:
        sfx_nobuy.play()


def ShopButton_user1(target): # shooting speed
    global money, shootspeed, bulletspeed
    if money >= target.cost:
        sfx_buy.play()
        money -= target.cost
        shootspeed += 2.5
        target.cost += 15
    else:
        sfx_nobuy.play()


def ShopButton_user2(target): # armor
    global money, maxarmor, maxhp
    if money >= target.cost and maxarmor < maxhp:
        sfx_buy.play()
        money -= target.cost
        maxarmor += 1
        target.cost += 15
    else:
        sfx_nobuy.play()

def ShopButton_create(target):
    target.x = 0
    target.y = 0
    target.color = (0,0,0)
    target.string = "Кнопочка"
    target.font = font_default
    target.text_color = target.color
    target.press_link = None
    target.text_link = None
    target.cost = 0

    target.width = 2 * 64
    target.height = 3 * 64

    instance_render_text(target)

def ShopButton_draw(target, surface: pygame.Surface):
    bgcolor = (target.color[0]//2, target.color[1]//2, target.color[2]//2)

    frame_x = target.x - target.width//2
    frame_y = target.y - target.height//2

    pygame.draw.rect(surface, bgcolor, (frame_x, frame_y, target.width, target.height), 0, 10)
    pygame.draw.rect(surface, target.color, (frame_x, frame_y, target.width, target.height), 2, 10)

    surface.blit(target.text[0], (target.x-target.text[0].get_width()//2, frame_y+8))

    cost = font_default.render(str(target.cost), False, 'white')

    surface.blit(cost, (target.x - cost.get_width()//2 - 1 - img_credit.get_width()//2, frame_y + target.height - 16))
    surface.blit(img_credit, (target.x + cost.get_width()//2 + 1 - img_credit.get_width()//2, frame_y + target.height - 16 + 4))

    if target.text_link is not None:
        lh = 16 # line height
        text = target.text_link()
        oy = frame_y + target.height - (lh*len(text)) - 32
        for line in text:
            oy += lh
            linerender = font_small.render(line, False, target.color)
            surface.blit(linerender, (target.x - linerender.get_width()//2, oy))


def ShopButton_mouse_pressed(target, mousepos, buttonid):
    xrange = target.x - target.width//2 <= mousepos[0] <= target.x + target.width//2
    yrange = target.y - target.height//2 <= mousepos[1] <= target.y + target.height//2

    if (xrange and yrange) and (target.press_link is not None):
        target.press_link(target)

EntShopButton = engine.Entity(event_create=ShopButton_create,
                              event_draw=ShopButton_draw,
                              event_mouse_pressed=ShopButton_mouse_pressed)
#endregion
#region [SHOP CONTINUE]
def ShopContinue_create(target):
    target.x, target.y = 0, 0
    target.font = font_default
    target.string = 'Следующий цикл'
    target.text_color = 'black'
    instance_render_text(target)

    target.gotofield = 0
    target.gotofield_step = 0

def ShopContinue_step(target):
    if target.gotofield:
        if target.gotofield_step < 1:
            target.gotofield_step += UPF(1/2)
        else:
            FieldBoard_init_level(fboard)
            engine.rooms.change_current_room(room_field)

def ShopContinue_draw(target, surface: pygame.Surface):
    tw = target.text[0].get_width()
    th = target.text[0].get_height()
    fs = 16  # размер поля между прямоугольником и текстом
    rect_coords = (target.x - ((tw + fs) // 2), target.y - ((th + fs) // 2), tw + fs, th + fs)
    text_coords = (target.x - (tw // 2), target.y - (th // 2))
    rounding = 4  # величина скругления задника
    pygame.draw.rect(surface, 'white', rect_coords, 0, rounding)  # задник
    pygame.draw.rect(surface, 'gray', rect_coords, 3, rounding)  # обводка задника
    surface.blit(target.text[0], text_coords)

def ShopContinue_draw_after(target, surface: pygame.Surface):
    width, height = surface.get_size()

    half_diagonal = (((width ** 2) + (height ** 2)) ** 0.5) / 2
    circle_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    circle_surface2 = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    circle_surface.fill('black')
    pygame.draw.circle(circle_surface2, 'black', (width / 2, height / 2),
                       half_diagonal * (max(0, 1.4 * (1 - target.gotofield_step) - 0.4)), 0)
    circle_surface.blit(circle_surface2, (0, 0), None, pygame.BLEND_RGBA_SUB)
    surface.blit(circle_surface, (0, 0), None)

def ShopContinue_mouse_pressed(target, mousepos, buttonid):
    tw = target.text[0].get_width()
    th = target.text[0].get_height()
    fs = 16  # размер поля между прямоугольником и текстом
    xrange = target.x - ((tw + fs) // 2) <= mousepos[0] <= target.x + ((tw + fs) // 2)
    yrange = target.y - ((th + fs) // 2) <= mousepos[1] <= target.y + ((th + fs) // 2)
    if xrange and yrange and not target.gotofield: target.gotofield = 1

def ShopContinue_room_start(target):
    target.gotofield = 0
    target.gotofield_step = 0


EntShopContinue = engine.Entity(event_create=ShopContinue_create,
                                event_step=ShopContinue_step,
                                event_draw=ShopContinue_draw,
                                event_draw_after=ShopContinue_draw_after,
                                event_mouse_pressed=ShopContinue_mouse_pressed,
                                event_room_start=ShopContinue_room_start)
#endregion
#endregion

#region [ОБЪЯВЛЕНИЕ ROOM]
global_entities = [EntGlobalCredits, EntGlobalCheats] # должны быть во всех комнатах

room_mainmenu = engine.Room([EntGlobalCheats, EntMainMenuBG, EntMainMenuText, EntMainMenuButton, EntMainMenuInstr,
                             EntMainMenuSettings])

room_field = engine.Room([EntGlobalCredits, EntGlobalCheats, EntFieldBG, EntFieldBoard, EntFieldPortal, EntFieldEnemy,
                          EntFieldBoss, EntFieldPlayer])

room_battle = engine.Room([EntGlobalCredits, EntGlobalCheats, EntFieldBG, EntBattlePlayer, EntBattlePlBullet,
                           EntBattleEnemy, EntBattleEnBullet])

room_shop = engine.Room([EntGlobalCredits, EntGlobalCheats, EntShopBG, EntShopButton, EntShopContinue])

engine.rooms.change_current_room(room_mainmenu)
#engine.rooms.change_current_room(room_shop)
#endregion

#region [СОЗДАНИЕ INSTANCE]
cheats = EntGlobalCheats.instance()
credit_counter = EntGlobalCredits.instance()

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

ourlicense = EntMainMenuText.instance()
ourlicense.x = screen.get_canvas_width() - 152
ourlicense.y = screen.get_canvas_height() - 44
ourlicense.font = font_small
ourlicense.text_align = 2
ourlicense.string = 'Лицензия: CC BY-NC 4.0\nДля Яндекс.Лицея, 2021'
instance_render_text(ourlicense)

controls = EntMainMenuText.instance()
controls.x = screen.get_canvas_halfwidth()
controls.y = screen.get_canvas_height() - 80
controls.font = font_small
controls.text_align = 1
#controls.string = 'Управление:\nСтрелочки/WASD - движение\nSpace - способность\nEsc (удерж.) - выход в главное меню'
controls.string = 'Управление:\nСтрелочки/WASD - движение\nEsc (удерж.) - выход в главное меню'
instance_render_text(controls)

instr = EntMainMenuInstr.instance()

settings = EntMainMenuSettings.instance()

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
mmb2.press_link = MainMenuButton_user1

mmb3 = EntMainMenuButton.instance()
mmb3.x = screen.get_canvas_halfwidth()
mmb3.y = screen.get_canvas_halfheight() + 48
mmb3.string = 'Выйти'
instance_render_text(mmb3)
mmb3.press_link = MainMenuButton_user2



fboard = EntFieldBoard.instance()

bg2 = EntFieldBG.instance()
bg2.image = img_bg

fplayer = EntFieldPlayer.instance()
fplayer.myboard = fboard

fportal = EntFieldPortal.instance()
fportal.pl_ins = fplayer
fportal.myboard = fboard

# fenemytest = EntFieldEnemy.instance()
# fenemytest.myboard = fboard
# fenemytest.pl_ins = fplayer
# fenemytest.detect_method = FieldEnemy_detect0
# fenemytest.image = img_board_enemy0
# fenemytest.cellx = fenemytest.celly = 4
# fenemytest.x, fenemytest.y = FieldBoard_get_cell_coords(fboard, 4, 4)

bplayer = EntBattlePlayer.instance()

benemy = EntBattleEnemy.instance()



shopbg = EntShopBG.instance()

shopbutton1 = EntShopButton.instance()
shopbutton1.color = (155, 255, 155)
shopbutton1.string = '+1 МАКС ХП'
shopbutton1.text_color = shopbutton1.color
shopbutton1.x = screen.get_canvas_halfwidth()
shopbutton1.y = screen.get_canvas_halfheight()
shopbutton1.cost = 10
shopbutton1.press_link = ShopButton_user0
shopbutton1.text_link = ShopButton_text0
instance_render_text(shopbutton1)

shopbutton2 = EntShopButton.instance()
shopbutton2.color = (255, 155, 155)
shopbutton2.string = 'СКР СТРЕЛЬБ'
shopbutton2.text_color = shopbutton2.color
shopbutton2.x = screen.get_canvas_halfwidth() - 160
shopbutton2.y = screen.get_canvas_halfheight()
shopbutton2.cost = 10
shopbutton2.press_link = ShopButton_user1
shopbutton2.text_link = ShopButton_text1
instance_render_text(shopbutton2)

shopbutton3 = EntShopButton.instance()
shopbutton3.color = (155, 155, 255)
shopbutton3.string = '+1 БРОНЯ'
shopbutton3.text_color = shopbutton3.color
shopbutton3.x = screen.get_canvas_halfwidth() + 160
shopbutton3.y = screen.get_canvas_halfheight()
shopbutton3.cost = 40
shopbutton3.press_link = ShopButton_user2
shopbutton3.text_link = ShopButton_text2
instance_render_text(shopbutton3)

shopcontinue = EntShopContinue.instance()
shopcontinue.x = screen.get_canvas_halfwidth()
shopcontinue.y = screen.get_canvas_height() - 24
#endregion

#region [КОНСТАНТЫ, ПЕРЕМЕННЫЕ И Т.Д.]
mylastpos_onfield = (0, 0) # последнее положение на поле
mylastpos_inbattle = (0, 0) # последнее положение в бою
mylastrot_onfield = 0
mylastrot_inbattle = 0
whodetected = None

money = 0
level = 1
maxhp = 8
hp = 6
maxarmor = 0
abilityid = 0
bulletdamage = 1
shootspeed = 5
bulletspeed = 2

enemyid = 0
enemyname = ['MIM Lighter 5', 'KLICH-Sh Shadow', 'ULTIMATA VII', 'Mnvr K5', 'VSTK SiegeEye \'88', 'BFG-ZBS M33 "Небесный"']
killedboss = False
cycle = 1

cheats_enabled = False # читы для разработчика
cheats_nodetect = False # никто не замечает игрока

show_mode = 0 # режим отображения окна
#endregion

#region [ГЛАВНЫЙ ЦИКЛ]
print('Запуск главного цикла...')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.load('data/mainmenu.mp3')
pygame.mixer.music.play(-1)
game_running = 1
# Добавление события начала боя

# Событие меняет фон если установлено значение 1
# Функция отображения текста
def draw_text(words, screen, pos, size, colour, font_name='arial', centered=False):
    if type(font_name) is not pygame.font.Font:
        font = pygame.font.SysFont(font_name, size)
    else:
        font = font_name
    text = font.render(words, False, colour)
    text_size = text.get_size()
    if centered:
        pos[0] = pos[0] - text_size[0] // 2
        pos[1] = pos[1] - text_size[1] // 2
    screen.blit(text, pos)

def paint_surface(surface: pygame.Surface,
                  color: Union[Tuple[int, int, int], Tuple[int, int, int, int], pygame.Color],
                  method: int):
    '''Красит pygame.Surface по определенному методу pygame.'''
    ns = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    surface.blit(ns, (0, 0))
    ns.fill(color, special_flags=method)


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

    screen.get_canvas().fill('black')
    engine.rooms.current_room.do_step(screen.get_canvas())
    screen.draw_screen()
    pygame.display.flip()
    clock.tick(FPS)
#endregion