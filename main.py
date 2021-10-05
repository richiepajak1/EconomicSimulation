# Richie Pajak independent study

import pygame
import random

from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 1000


def find_empty_home():
    for x in homes:
        if not x.owned:
            x.owned = True
            return x
    return None


def find_home_location():
    row = len(homes) // 5
    col = len(homes) % 5
    rowcoord = (row * 100) + 100
    colcoord = (col * 100) + 525
    return colcoord, rowcoord


def find_business_location():
    row = len(businesses) // 2
    col = len(businesses) % 2
    rowcoord = (row * 100) + 100
    colcoord = (col * 100) + 75
    return colcoord, rowcoord


def create_home():
    new_home = Home()
    homes.add(new_home)
    all_sprites.add(new_home)


def create_agent():
    new_agent = Agent()
    agents.add(new_agent)
    all_sprites.add(new_agent)


def create_business(type):
    new_business = Business(type)
    businesses.add(new_business)
    all_sprites.add(new_business)


class Agent(pygame.sprite.Sprite):
    def __init__(self):
        super(Agent, self).__init__()
        self.size = 15
        self.speed = 1
        self.objective = 0
        self.food = 0
        self.money = 100
        self.surf = pygame.Surface((self.size, self.size))
        self.surf.fill((random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)))
        self.rect = self.surf.get_rect()
        self.home = find_empty_home()
        self.destination = self.home
        self.at_home = True
        self.type = 0
        if self.home is None:
            self.rect.center = (0, 0)
        else:
            self.rect.center = self.home.rect.center
        self.curr_prio = None

        self.work_prio = 100 - self.money

        self.prio_list = {
            'food': 20 - self.food,
        }

    def update(self, businesses):

        if self.curr_prio == 'food':
            for x in businesses:
                if x.product_type == 'food':
                    self.destination = x
            if self.rect.colliderect(self.destination):
                self.buy(self.destination)
                self.curr_prio = 'home'

        if self.curr_prio == 'home':
            self.destination = self.home
        if self.curr_prio == 'work':
            for x in businesses:
                if x.being_worked() is False:
                    self.destination = x
                    x.set_worked(True)

        self.move()

        if self.rect.center == self.home.rect.center:
            self.at_home = True
        else:
            self.at_home = False


    def buy(self, business):
        if self.money >= business.get_sell_price():
            self.spend_money(business.get_sell_price())
            business.sell()

    def spend_money(self, amount):
        self.money = self.money - amount

    def gain_money(self, amount):
        self.money = self.money + amount

    def calc_prios(self):
        self.prio_list['food'] = 20 - self.food
        self.work_prio = 100 - self.money

    def get_highest_prio(self):
        self.curr_prio = max(self.prio_list, key=self.prio_list.get)

    def set_curr_prio(self, prio):
        self.curr_prio = prio

    def get_work_prio(self):
        return self.work_prio

    def set_worker(self):
        self.type = 1

    def set_consumer(self):
        self.type = 0

    def is_at_home(self):  # This is a getter function for the variable at_home
        if self.at_home is True:
            return True
        else:
            return False

    def move(self):
        direction = self.get_direction(self.destination.rect.centerx, self.destination.rect.centery)
        self.rect.move_ip(direction)

    def get_direction(self, x, y):  # This function returns the direction that a creature should move based on the
        # coordinates of its destination that are passed in
        direction_x = 0
        direction_y = 0
        if self.rect.centerx < x:
            direction_x = self.speed
        if self.rect.centerx > x:
            direction_x = -self.speed
        if self.rect.centery < y:
            direction_y = self.speed
        if self.rect.centery > y:
            direction_y = -self.speed

        direction = (direction_x, direction_y)
        return direction


class Business(pygame.sprite.Sprite):
    def __init__(self, type):
        super(Business, self).__init__()
        self.size = 50
        self.surf = pygame.Surface((self.size, self.size))
        self.surf.fill((random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)))
        self.rect = self.surf.get_rect()
        self.rect.center = find_business_location()
        self.product_amount = 20
        self.product_type = type
        self.sell_price = 5
        self.money = 0
        self.is_worked = False
        self.worker = None

    def update(self):
        return

    def get_sell_price(self):
        return self.sell_price

    def sell(self):
        if self.product_amount > 0:
            self.money = self.money + self.sell_price
            self.product_amount = self.product_amount - 1
            print('kaching')

    def give_profits(self):
        self.worker.gain_money(self.money)
        self.money = 0

    def find_worker(self, agents):
        current_worker = None
        prio = -1000
        for x in agents:
            print(x.get_work_prio())
            if x.get_work_prio() > prio:
                print('here')
                current_worker = x
                prio = x.get_work_prio()
        current_worker.set_worker()
        current_worker.set_curr_prio('work')
        return current_worker

    def being_worked(self):
        return self.is_worked

    def set_worked(self, status):
        self.is_worked = status

    def clear_worker(self):
        self.worker = None
        self.is_worked = False


class Home(pygame.sprite.Sprite):
    def __init__(self):
        super(Home, self).__init__()
        self.size = 35
        self.surf = pygame.Surface((self.size, self.size))
        self.surf.fill((random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)))
        self.rect = self.surf.get_rect()
        self.owned = False
        self.rect.center = find_home_location()


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
homes = pygame.sprite.Group()
agents = pygame.sprite.Group()
businesses = pygame.sprite.Group()

num_homes = 5
num_agents = 5
num_businesses = 1
i = 0
while i < num_homes:
    create_home()
    i = i + 1
i = 0
while i < num_agents:
    create_agent()
    i = i + 1
i = 0
while i < num_businesses:
    create_business('food')
    i = i + 1

phase = 0
all_consumers_at_home = True
all_agents_at_work = True
all_agents_at_home = True

running = True
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False
    if phase == 0:
        for x in agents:
            x.get_highest_prio()
        for x in businesses:
            x.worker = x.find_worker(agents)
        phase = 1
    elif phase == 1:
        businesses.update()
        for x in agents:
            if x.type == 1:
                x.update(businesses)
        all_agents_at_work = True
        for x in agents:
            if x.type == 1 and not x.rect.colliderect(x.destination.rect):
                all_agents_at_work = False
        for x in agents:
            if x.rect.colliderect(x.destination.rect) and x.type == 1:
                x.rect.center = x.destination.rect.center
        if all_agents_at_work is True:
            phase = 2
    elif phase == 2:
        for x in agents:
            if x.type == 0:
                x.update(businesses)
        all_consumers_at_home = True
        for x in agents:
            if x.type == 0:
                if x.is_at_home() is False:
                    all_consumers_at_home = False
        if all_consumers_at_home:
            phase = 3
    elif phase == 3:
        for x in agents:
            x.set_curr_prio('home')
            x.update(businesses)
        all_agents_at_home = True
        for x in agents:
            if x.is_at_home() is False:
                all_agents_at_home = False
        if all_agents_at_home:
            phase = 4
    elif phase == 4:
        for x in businesses:
            x.give_profits()
            x.clear_worker()
        for x in agents:
            x.calc_prios()
            x.set_consumer()
            x.set_curr_prio('')
            type = 0
        phase = 0

    screen.fill((255, 255, 255))

    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)
    clock.tick(400)

    pygame.display.flip()
