from typing import List, Tuple, Union

import pygame


def clamp(value: int, mn: int, mx: int):
    return min(mx, max(mn, value))


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
    def __init__(self):
        self.instances: List[Instance] = []

        self.event_create = None
        self.event_step = None
        self.event_step_before = None
        self.event_step_after = None
        self.event_alerts = []
        self.alerts = []
        self.event_user = []

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
    def __init__(self, canvas_size: Tuple[int, int], realscreen_size: Tuple[int, int], fullscreen_mode: bool = False):
        self.cs = self.csw, self.csh = canvas_size
        self.ss = self.ssw, self.ssh = realscreen_size
        self.canvas = pygame.Surface(self.cs)
        self.screen = pygame.display.set_mode(self.ss, (bool(fullscreen_mode) * pygame.FULLSCREEN))

    def get_canvas(self):
        return

    def update_screen(self, size: Tuple[int, int] = None, fullscreen_mode: bool = False):
        if size is None:
            size = self.ss
        self.screen = pygame.display.set_mode(size, (bool(fullscreen_mode) * pygame.FULLSCREEN))