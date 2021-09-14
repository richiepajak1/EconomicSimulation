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


def update_all(businesses):
    agents.update(businesses)
    businesses.update()


class Agent(pygame.sprite.Sprite):
    def __init__(self):
        super(Agent, self).__init__()
        self.size = 15
        self.speed = 3
        self.objective = 0
        self.food = 0
        self.surf = pygame.Surface((self.size, self.size))
        self.surf.fill((random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)))
        self.rect = self.surf.get_rect()
        self.home = find_empty_home()
        self.destination = self.home
        if self.home is None:
            self.rect.center = (0, 0)
        else:
            self.rect.center = self.home.rect.center
        self.prio_list = {
            "food": 20 - self.food,
        }

    def update(self, businesses):
        curr_prio = self.calc_prios(self.prio_list)

        if curr_prio == 'food':
            for x in businesses:
                if x.product_type == 'food':
                    self.destination = x


        self.move()

    def calc_prios(self, prio_list):
        prio_list['food'] = 20
        greatest_prio = max(prio_list, key=prio_list.get)
        return greatest_prio

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
        self.product_amount = 5
        self.product_type = type
        self.is_worked = False

    def update(self):
        return


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

num_homes = 15
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

running = True
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False

    screen.fill((255, 255, 255))
    update_all(businesses)
    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)
    clock.tick(60)

    pygame.display.flip()
