import os
import sys

from typing import List, Tuple, Union
from math import sin, cos, radians, degrees, floor, ceil

import pygame


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

       ВСЕ СОБЫТИЯ:
       event_create - событие, выполняемое Instance сразу же после его создания.
       event_step - событие, выполняемое Instance каждый игровой кадр.
       event_step_before - событие, выполняемое Instance каждый игровой кадр, но до event_step всех Instnace.
       event_step_after - событие, выполняемое Instance каждый игровой кадр, но после event_step всех Instance.
       event_alerts[i] - событие, выполняемое Instance в случае, если alerts[i] = 0. каждый alerts[i] понижается на 1 каждый игровой кадр, пока не достигнет -1.
       event_user[i] - пользовательское событие, выполняемое Instance в случае его прямого вызова.'''
    def __init__(self, event_create = None, event_step = None, event_step_before = None, event_step_after = None, event_alerts = [], alerts = [], event_user = []):
        self.instances: List[Instance] = []

        self.event_create = event_create
        self.event_step = event_step
        self.event_step_before = event_step_before
        self.event_step_after = event_step_after
        self.event_alerts = event_alerts
        self.alerts = alerts
        self.event_user = event_user

    def instance(self):
        '''Создает новый Instance данного Entity, перенимающий с него все события.'''
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

    def do_alerts(self):
        '''Выполнение будильников'''
        for alert in range(len(self.entity.alerts)):
            getalert = self.entity.alerts[alert]
            if getalert == 0:
                self.entity.event_alerts[alert](target=self)
            if getalert >= 0:
                self.entity.alerts[alert] -= 1

    def do_user(self, index: int):
        '''Выполнение '''
        self.entity.event_user[index](target=self)


class EntityGroup:
    def __init__(self, entities: List[Entity] = None):
        if entities is None:
            self.entities = []
        else:
            self.entities = entities

    def do_step(self):
        running = []
        for ent in self.entities:
            for ins in ent.instances:
                running.append(ins)

        for ins in running: ins.do_step_before()
        for ins in running: ins.do_step()
        for ins in running: ins.do_step_after()
        for ins in running: ins.do_alerts()


class Screen:
    '''Класс окна. В нем есть холст (на который наносятся нарисованные объекты) и дисплей (то, что показывается).
       Есть возможность создания полноэкранного режима.

       fullscreen_mode - числовой аргумент от 0 до 2 включительно:
       | 0 - оконный режим
       | 1 - полноэкранный режим
       | 2 - смешанный режим (оконнный на весь экран)'''
    def __init__(self, canvas_size: Tuple[int, int], realscreen_size: Tuple[int, int], fullscreen_mode: int = 0, resizable_mode: bool = True):
        self.cs = self.csw, self.csh = canvas_size
        if fullscreen_mode == 2:
            self.ss = self.ssw, self.ssh = SCREENSIZE
        else:
            self.ss = self.ssw, self.ssh = realscreen_size
        self.canvas = pygame.Surface(self.cs)
        self.fm = clamp(fullscreen_mode, 0, 2)
        self.rm = bool(resizable_mode)
        if self.fm == 1:
            self.screen = pygame.display.set_mode(self.ss, pygame.FULLSCREEN)
        elif self.fm == 2:
            self.screen = pygame.display.set_mode(SCREENSIZE, pygame.NOFRAME)
        else:
            self.screen = pygame.display.set_mode(self.ss, (self.rm * pygame.RESIZABLE))

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

    def update_screen(self, size: Tuple[int, int] = None, fullscreen_mode: int = None, resizable_mode: bool = None):
        '''Обновить данные экрана. Значение None в аргументах означает сохранение предыдущего значения.'''
        if size is None:
            size = self.ss
        if fullscreen_mode is None:
            fullscreen_mode = self.fm
        if resizable_mode is None:
            resizable_mode = self.rm

        if self.fm == 2:
            self.ss = self.ssw, self.ssh = SCREENSIZE
        else:
            self.ss = self.ssw, self.ssh = size

        self.fm = clamp(fullscreen_mode, 0, 2)
        self.rm = bool(resizable_mode)
        if self.fm == 1:
            self.screen = pygame.display.set_mode(self.ss, pygame.FULLSCREEN)
        elif self.fm == 2:
            self.screen = pygame.display.set_mode(SCREENSIZE, pygame.NOFRAME)
        else:
            self.screen = pygame.display.set_mode(self.ss, (self.rm * pygame.RESIZABLE))

    def draw_screen(self):
        scale_level = min(self.ssw/self.csw, self.ssh/self.csh)
        scaled_size = (self.csw * scale_level, self.csh * scale_level)
        delta_width = self.ssw - scaled_size[0]
        delta_height = self.ssh - scaled_size[1]
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