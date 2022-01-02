import os
import sys

from typing import List, Tuple, Union
from math import sin, cos, radians, degrees, floor, ceil

import pygame


def lengthdir_x(len, dir):
    '''координата x конца вектора с длиной len и углом dir.'''
    return len * cos(radians(dir))

def lengthdir_y(len, dir):
    '''координата x конца вектора с длиной len и углом dir.'''
    return len * -sin(radians(dir))


def interpolate(x, y, power: int = 1, side: Union[int, bool] = 0):
    '''Функция интерполяции.
       Или же поиска значения между x и y, при power = 1 равного средне-арифмитическому,
       но при power > 1 значение будет отступать от средне-арифметического пропорционально значению power
       к x или y в зависимости от side = 0 или 1 соответственно.

       Полезно для ежекадровых функций где объекту нужно изменять значение своей переменной с x до y с ускорением или торможением.
       Чем выше значение power, тем торможение или начальное ускорение будет мягче.

       Аргументы:
           x, y
               Значения, преимущественно числовые.
           power
               Степень рекурсии интерполяции.
               При power > 1, x или y (в завис. от side) заменится на interpolate(x,y,power-1,side).
           side
               Сторона (0/1). Важно когда power > 1. При side=0, функция вернет значение ближе к x нежели к y.'''
    power = max(power, 1)
    div = 2**power
    if side:
        return (x*1/div) + (y*(div-1)/div)
    else:
        return (x*(div-1)/div) + (y*1/div)
    # if power == 1:
    #     return (x+y)/2
    # else:
    #     if side:
    #         return (interpolate(x, y, power - 1, side) + y) / 2
    #     else:
    #         return (x + interpolate(x, y, power - 1, side)) / 2


def speed_upf(units_per_second, fps):
    '''Возвращает скорость units per frame (т. е. едениц за кадр).
    Необходимо для ежекадровых функций объектов, которые отсчитывают время или двигают объекты.

       Аргументы на вход:
       units_per_second - сколько едениц должно быть в секунду
       fps              - сколько кадров в секунду'''
    return units_per_second/fps


def clamp(value: int, mn: int, mx: int) -> int:
    '''Возвращает значение, равное аргументу value или нижней или верхней грани (mn и mx соответственно), если value выходит за них.'''
    return min(mx, max(mn, value))


def gcd(a: int, b: int) -> int:
    '''Наибольший общий делитель.'''
    if a == 0 or b == 0:
        return a+b
    if a > b:
        return gcd(a%b, b)
    else:
        return gcd(a, b%a)


def pygame_init():
    '''Вызывает pygame.init().'''
    pygame.init()


def pygame_videoinfo():
    '''Возвращает _VidInfo путем вызова pygame.display.Info(). Необходимо для get_screensize(videinfo) в качестве аргумента.
       Работает только после вызова pygame.init().'''
    return pygame.display.Info()

def get_screensize(videoinfo) -> Tuple[int, int]:
    '''Получить размер экрана формата (Ширина, Высота).
       В качестве аргумента нужно вставить _VidInfo, получаемый командой pygame.display.Info().
       pygame.display.Info() также можно получить командой pygame_videoinfo().'''
    return (videoinfo.current_w, videoinfo.current_h)


def load_image(name, dirname='data'):
    path = os.path.join(dirname, name)
    if not os.path.isfile(path):
        raise RuntimeError
    img = pygame.image.load(path)
    return img


class Entity:
    '''Класс для наследования классов для создания внутреигровых одинаковых, но уникальных объектов.
       Главная способность классов, наследовавших Entity - создавание объектов Instance.

       ВСЕ СОБЫТИЯ (в порядке их выполнения):
       event_create - событие, выполняемое сразу же после создания. Не выполняется повторно.

       event_step_before - событие, выполняемое каждый игровой кадр, но до event_step всех Instance.
       event_step - событие, выполняемое каждый игровой кадр.
       event_step_after - событие, выполняемое каждый игровой кадр, но после event_step всех Instance.

       event_draw_before - событие, выполняемое каждый игровой кадр, но до event_draw всех Instance.
       event_draw - событие, выполняемое каждый игровой кадр.
       event_draw_after - событие, выполняемое каждый игровой кадр, но после event_draw всех Instance.'''
    def __init__(self, event_create = None,
                       event_step = None, event_step_before = None, event_step_after = None,
                       event_draw = None, event_draw_before = None, event_draw_after = None,
                       event_room_start = None, event_room_end = None):
        self.instances: List[Instance] = []

        self.event_create = event_create
        self.event_step = event_step
        self.event_step_before = event_step_before
        self.event_step_after = event_step_after
        self.event_draw = event_draw
        self.event_draw_before = event_draw_before
        self.event_draw_after = event_draw_after
        self.event_room_start = event_room_start
        self.event_room_end = event_room_end

    def instance(self):
        '''Создает новый Instance данного Entity, перенимающий с него все события.

        В качестве **specific (kw_args) можно задать специфические значения переменных, заданных в event_create.'''
        new_instance = Instance(entity = self)
        self.instances.append(new_instance)
        return new_instance


class Instance:
    def __init__(self, entity: Entity):
        self.entity = entity
        if self.entity.event_create is not None:
            self.entity.event_create(target=self)

    def do_step(self):
        '''Выполнение шага'''
        if self.entity.event_step is not None:
            self.entity.event_step(target=self)

    def do_step_before(self):
        '''Выполнение до-шага'''
        if self.entity.event_step_before is not None:
            self.entity.event_step_before(target=self)

    def do_step_after(self):
        '''Выполнение после-шага'''
        if self.entity.event_step_after is not None:
            self.entity.event_step_after(target=self)

    def do_draw(self, surface):
        '''Отрисовка'''
        if self.entity.event_draw is not None:
            self.entity.event_draw(target=self, surface=surface)

    def do_draw_before(self, surface):
        '''До-отрисовка'''
        if self.entity.event_draw_before is not None:
            self.entity.event_draw_before(target=self, surface=surface)

    def do_draw_after(self, surface):
        '''После-отрисовка'''
        if self.entity.event_draw_after is not None:
            self.entity.event_draw_after(target=self, surface=surface)

    def do_room_start(self):
        '''Вход в комнату'''
        if self.entity.event_room_start is not None:
            self.entity.event_room_start(target=self)

    def do_room_end(self):
        '''Выход из комнаты'''
        if self.entity.event_room_end is not None:
            self.entity.event_room_end(target=self)


class Room:
    '''Класс комнат. Комнаты помогают управлять несколькими "игровыми экранами" и ежекадровыми функциями.
       На вход принимает список объектов Entity, Instance которых будут выполнять ежекадровые события
       при вызове метода do_step() или одиночные события event_room_stand и event_room_end при вызове
       методов start() и end() соответственно.'''
    def __init__(self, entities: List[Entity] = None):
        if entities is None:
            self.entities = []
        else:
            self.entities = entities

    def do_step(self, surface_to_draw: pygame.Surface = None):
        running = []
        for ent in self.entities:
            for ins in ent.instances:
                running.append(ins)

        for ins in running: ins.do_step_before()
        for ins in running: ins.do_step()
        for ins in running: ins.do_step_after()
        if surface_to_draw is not None:
            for ins in running: ins.do_draw_before(surface_to_draw)
            for ins in running: ins.do_draw(surface_to_draw)
            for ins in running: ins.do_draw_after(surface_to_draw)

    def start(self):
        for ent in self.entities:
            for ins in ent.instances:
                ins.do_room_start()

    def end(self):
        for ent in self.entities:
            for ins in ent.instances:
                ins.do_room_end()


class rooms:
    '''Здесь хранится действительная комната.
       Не создавать экземпляры класса - переменная current_room хранится у самого класса.
       Есть также функция rooms.change_current_room, позволяющая изменить переменную current_room
       с последовательным вызовом метода end для предыдущего current_room и start для нового.'''
    current_room = None
    @staticmethod
    def change_current_room(new_room: Room):
        if rooms.current_room is not None:
            rooms.current_room.end()
        rooms.current_room = new_room
        rooms.current_room.start()


class Screen:
    '''Класс окна. В нем есть холст (на который наносятся нарисованные объекты) и дисплей (то, что показывается).
       Есть возможность создания полноэкранного режима.

       fullscreen_mode - числовой аргумент от 0 до 2 включительно:
       | 0 - оконный режим
       | 1 - полноэкранный режим
       | 2 - смешанный режим (оконнный на весь экран)'''
    def __init__(self, canvas_size: Tuple[int, int], realscreen_size: Tuple[int, int], fullscreen_mode: int = 0, resizable_mode: bool = True):
        self.cs = self.cw, self.ch = canvas_size
        if fullscreen_mode == 2:
            self.ss = self.sw, self.sh = SCREENSIZE
        else:
            self.ss = self.sw, self.sh = realscreen_size
        self.canvas = pygame.Surface(self.cs)
        self.fm = clamp(fullscreen_mode, 0, 2)
        self.rm = bool(resizable_mode)
        if self.fm == 1:
            self.screen = pygame.display.set_mode(self.ss, pygame.FULLSCREEN)
        elif self.fm == 2:
            self.screen = pygame.display.set_mode(SCREENSIZE, pygame.NOFRAME)
        else:
            self.screen = pygame.display.set_mode(self.ss, (self.rm * pygame.RESIZABLE))

        self.cd = ceil(((self.cw**2)+(self.ch**2))**0.5)
        self.sd = ceil(((self.sw**2)+(self.sh**2))**0.5)

        self.cw2 = self.cw//2
        self.ch2 = self.ch//2
        self.cd2 = self.cd//2
        self.sw2 = self.sw//2
        self.sh2 = self.sh//2
        self.sd2 = self.sd//2

    def get_canvas(self) -> pygame.Surface:
        return self.canvas

    def get_screen(self) -> pygame.Surface:
        return self.screen

    def get_fullscreen(self) -> int:
        return self.fm

    def get_resizable(self) -> bool:
        return self.rm

    def get_canvas_size(self) -> Tuple[int, int]:
        return self.cs

    def get_screen_size(self) -> Tuple[int, int]:
        return self.ss

    def get_canvas_width(self) -> int:
        return self.cw

    def get_canvas_height(self) -> int:
        return self.ch

    def get_screen_width(self) -> int:
        return self.sw

    def get_screen_height(self) -> int:
        return self.sh

    def get_canvas_halfwidth(self) -> int:
        return self.cw2

    def get_canvas_halfheight(self) -> int:
        return self.ch2

    def get_screen_halfwidth(self) -> int:
        return self.sw2

    def get_screen_halfheight(self) -> int:
        return self.sh2

    def get_canvas_diagonal(self) -> int:
        return self.cd

    def get_canvas_halfdiagonal(self) -> int:
        return self.cd2

    def get_screen_diagonal(self) -> int:
        return self.sd

    def get_screen_halfdiagonal(self) -> int:
        return self.sd2

    def update_screen(self, size: Tuple[int, int] = None, fullscreen_mode: int = None, resizable_mode: bool = None):
        '''Обновить данные экрана. Значение None в аргументах означает сохранение предыдущего значения.'''
        if size is None:
            size = self.ss
        if fullscreen_mode is None:
            fullscreen_mode = self.fm
        if resizable_mode is None:
            resizable_mode = self.rm

        if self.fm == 2:
            self.ss = self.sw, self.sh = SCREENSIZE
        else:
            self.ss = self.sw, self.sh = size

        self.fm = clamp(fullscreen_mode, 0, 2)
        self.rm = bool(resizable_mode)
        if self.fm == 1:
            self.screen = pygame.display.set_mode(self.ss, pygame.FULLSCREEN)
        elif self.fm == 2:
            self.screen = pygame.display.set_mode(SCREENSIZE, pygame.NOFRAME)
        else:
            self.screen = pygame.display.set_mode(self.ss, (self.rm * pygame.RESIZABLE))

        self.cd = ceil(((self.cw ** 2) + (self.ch ** 2)) ** 0.5)
        self.sd = ceil(((self.sw ** 2) + (self.sh ** 2)) ** 0.5)

        self.cw2 = self.cw // 2
        self.ch2 = self.ch // 2
        self.cd2 = self.cd // 2
        self.sw2 = self.sw // 2
        self.sh2 = self.sh // 2
        self.sd2 = self.sd // 2

    def draw_screen(self):
        scale_level = min(self.sw/self.cw, self.sh/self.ch)
        scaled_size = (self.cw * scale_level, self.ch * scale_level)
        delta_width = self.sw - scaled_size[0]
        delta_height = self.sh - scaled_size[1]
        self.screen.fill('black')
        self.screen.blit(pygame.transform.scale(self.canvas, scaled_size), (delta_width//2, delta_height//2))


if __name__ == '__main__':
    pygame_init()
    SCREENSIZE = get_screensize(pygame_videoinfo())
    print('TEST RUN')
    print(f'SCREENSIZE is: {SCREENSIZE[0]}, {SCREENSIZE[1]}')

    canvas_w = 200
    canvas_h = 100
    pixel_size = 2
    canvas_size = (canvas_w, canvas_h)
    screen_size = (canvas_w*pixel_size, canvas_h*pixel_size)
    s = Screen(canvas_size, screen_size, 0, True)

    running = 1
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = 0
            if e.type == pygame.VIDEORESIZE:
                s.update_screen((e.w, e.h))

        pygame.draw.rect(s.get_canvas(), 'yellow', (0,0, *canvas_size), 4)
        pygame.draw.line(s.canvas, 'white', (0,0), canvas_size, 2)
        s.draw_screen()

        pygame.display.flip()