# Richie Pajak independent study

import csv
import os
import pandas as pd
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
        self.surf = pygame.Surface((self.size, self.size))
        self.surf.fill((random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)))
        self.rect = self.surf.get_rect()
        self.food = random.randint(5, 10)
        self.water = random.randint(5, 10)
        self.money = 100
        self.home = find_empty_home()
        self.destination = self.home
        self.at_home = True
        self.consumer = True
        self.business_options = []

        if self.home is None:
            self.rect.center = (0, 0)
        else:
            self.rect.center = self.home.rect.center

        self.curr_prio = None

        self.work_prio = -1 * self.money

        self.prio_list = {
            'food': -1 * self.food,
            'water': -1 * self.water
        }

    def update(self, businesses):

        if self.curr_prio == 'home':
            self.destination = self.home
        elif self.curr_prio == 'work':
            for x in businesses:
                if x.being_worked() is False:
                    self.destination = x
                    x.set_worked(True)
                    break
        else:
            if len(self.business_options) != 0:
                min_price = float('inf')
                best_option = None
                for x in self.business_options:
                    if x.get_sell_price() < min_price:
                        if x.get_product_amount() > 0:
                            min_price = x.get_sell_price()
                            best_option = x
                if best_option is None:
                    best_option = self.home
                    self.curr_prio = 'home'
                self.destination = best_option
                if self.rect.colliderect(self.destination.rect):
                    if self.buy(self.destination):
                        self.curr_prio = 'home'
                        self.business_options.clear()
                    else:
                        self.business_options.pop(0)
            else:
                self.curr_prio = 'home'

        self.move()

        if self.rect.center == self.home.rect.center:
            self.at_home = True
        else:
            self.at_home = False

    def determine_business(self, businesses):
        for x in businesses:
            if x.product_type == self.curr_prio:
                self.business_options.append(x)

    def buy(self, business):
        num_purchases = 4
        success = False
        while num_purchases > 0:
            if self.money >= business.get_sell_price():
                if business.sell():
                    success = True
                    self.spend_money(business.get_sell_price())
                    if business.product_type == 'food':
                        self.food = self.food + 1
                    if business.product_type == 'water':
                        self.water = self.water + 1

            num_purchases = num_purchases - 1
        return success

    def spend_money(self, amount):
        self.money = self.money - amount

    def gain_money(self, amount):
        self.money = self.money + amount

    def calc_prios(self):
        print(self.food, self.water, self.money)
        self.prio_list['food'] = 20 - self.food
        self.prio_list['water'] = 20 - self.water
        self.work_prio = 100 - self.money

    def lose_products(self):
        self.food = self.food - 1
        self.water = self.water - 1

    def get_highest_prio(self):
        prio_options = ['food']
        for x in self.prio_list:
            if self.prio_list.get(x) > self.prio_list[prio_options[0]]:
                prio_options.clear()
                prio_options.append(x)
            elif self.prio_list.get(x) == self.prio_list[prio_options[0]]:
                prio_options.append(x)
        index = random.randint(0, len(prio_options) - 1)
        self.curr_prio = prio_options[index]

    def set_curr_prio(self, prio):
        self.curr_prio = prio

    def get_curr_prio(self):
        return self.curr_prio

    def get_work_prio(self):
        return self.work_prio

    def set_worker(self):
        self.consumer = False

    def set_consumer(self):
        self.consumer = True

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
            direction_x = 1
        if self.rect.centerx > x:
            direction_x = -1
        if self.rect.centery < y:
            direction_y = 1
        if self.rect.centery > y:
            direction_y = -1

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
        self.product_amount = 12
        self.product_type = type
        self.sell_price = 5
        self.money = 0
        self.production_amount = 10
        self.is_worked = False
        self.worker = None

    def update(self):
        if self.product_type == 'food':
            self.surf.fill((255, 0, 0))
        elif self.product_type == 'water':
            self.surf.fill((0, 255, 0))
        else:
            self.surf.fill((0, 0, 255))
        return

    def get_sell_price(self):
        return self.sell_price

    def get_product_amount(self):
        return self.product_amount

    def sell(self):
        if self.product_amount > 0:
            self.money = self.money + self.sell_price
            self.product_amount = self.product_amount - 1
            return True
        return False

    def give_profits(self):
        self.worker.gain_money(self.money)
        self.money = 0

    def produce(self):
        self.product_amount = self.production_amount

    def find_worker(self, agents):
        current_worker = None
        prio = -1000
        for x in agents:
            if x.get_work_prio() > prio and x.get_curr_prio() != 'work':
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

    def price_change(self):
        if self.product_amount > 0:
            if self.sell_price > 1:
                self.sell_price = self.sell_price - 1
                print("decrease", self.sell_price)
        else:
            self.sell_price = self.sell_price + 1
            print("increase", self.sell_price)

    def set_production_amount(self, amount):
        self.production_amount *= amount

    def reset_production_amount(self):
        self.production_amount = 10


class Home(pygame.sprite.Sprite):
    def __init__(self):
        super(Home, self).__init__()
        self.size = 35
        self.surf = pygame.Surface((self.size, self.size))
        self.surf.fill((random.randint(0, 200), random.randint(0, 200), random.randint(0, 200)))
        self.rect = self.surf.get_rect()
        self.owned = False
        self.rect.center = find_home_location()


#def covid():

#def drought():

#def hurricane():

#def tornado():

#def stimulus():

#def aid():






pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
homes = pygame.sprite.Group()
agents = pygame.sprite.Group()
businesses = pygame.sprite.Group()



num_homes = 40
num_agents = 40
num_businesses = 10
num_food_businesses = 0
num_water_businesses = 0
day_count = 0
disaster_day = 0
disaster_type = ''
disaster_severity = 0.0
i = 0
while i < num_homes:
    create_home()
    i += 1
i = 0
while i < num_agents:
    create_agent()
    i += 1
i = 0
while i < num_businesses:
    if random.randint(0, 1) == 0:
        create_business('food')
        num_food_businesses += 1
    else:
        create_business('water')
        num_water_businesses += 1
    i += 1

phase = 0
all_consumers_at_home = True
all_agents_at_work = True
all_agents_at_home = True

filename = "selectiondata.csv"
f = open(filename, "w+")
f.close()

filename = "sagentdata.csv"
f = open(filename, "w+")
f.close()

with open('selectiondata.csv', 'a', newline='') as csvfile:
    mywriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
    mywriter.writerow(('average food price', 'average water price'))

header = []
for x in range(0, num_agents):
    header.append('Agent_{}'.format(x))
    header.append('Agent_{}'.format(x))
    header.append('Agent_{}'.format(x))

header2 = []
for x in range(0, num_agents):
    header2.append('Money')
    header2.append('Food')
    header2.append('Water')

with open('sagentdata.csv', 'a', newline='') as csvfile:
    mywriter = csv.writer(csvfile, delimiter=',', lineterminator='\n')
    mywriter.writerow(header)
    mywriter.writerow(header2)

running = True
while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
                filepath = os.path.dirname(os.path.abspath(__file__))

                read_file = pd.read_csv(filepath + '\selectiondata.csv')
                read_file.to_excel(filepath + '\selectiondata.xlsx', index=None, header=True)
                read_file2 = pd.read_csv(filepath +'\sagentdata.csv')
                read_file2.to_excel(filepath + '\sagentdata.xlsx', index=None, header=True)
        elif event.type == QUIT:
            running = False
            filepath = os.path.dirname(os.path.abspath(__file__))

            read_file = pd.read_csv(filepath + '\selectiondata.csv')
            read_file.to_excel(filepath + '\selectiondata.xlsx', index=None, header=True)
            read_file2 = pd.read_csv(filepath + '\sagentdata.csv')
            read_file2.to_excel(filepath + '\sagentdata.xlsx', index=None, header=True)
    if phase == 0:
        day_count += 1
        for x in agents:
            x.get_highest_prio()
        for x in businesses:
            x.worker = x.find_worker(agents)
        phase = 1
    elif phase == 1:
        businesses.update()
        for x in agents:
            if x.consumer == False:
                x.update(businesses)
        all_agents_at_work = True
        for x in agents:
            if x.consumer == False and not x.rect.colliderect(x.destination.rect):
                all_agents_at_work = False
        for x in agents:
            if x.rect.colliderect(x.destination.rect) and x.consumer == False:
                x.rect.center = x.destination.rect.center
        if all_agents_at_work is True:
            phase = 2
            for x in agents:
                x.determine_business(businesses)
    elif phase == 2:
        for x in agents:
            if x.consumer:
                x.update(businesses)

        all_consumers_at_home = True
        for x in agents:
            if x.consumer:
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
        food_sum = 0
        water_sum = 0
        for x in businesses:
            x.give_profits()
            x.clear_worker()
            x.price_change()
            x.produce()
            if x.product_type == 'food':
                food_sum += x.sell_price
            else:
                water_sum += x.sell_price
            print(x.product_amount, x.product_type)
        for x in agents:
            x.calc_prios()
            x.set_consumer()
            x.set_curr_prio('')
            x.lose_products()
            x.type = 0
            # if x.food > 15:
            # if num_agents < num_homes:
            # create_agent()
            # x.food = x.food - 10
            # if x.food < 0:
            # x.home.owned = False
            # x.kill()
        food_average = food_sum / num_food_businesses
        water_average = water_sum / num_water_businesses
        with open('selectiondata.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')
            csv_writer.writerow((food_average, water_average))

        row = []
        for x in agents:
            row.append(x.money)
            row.append(x.food)
            row.append(x.water)
        with open('sagentdata.csv', 'a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', lineterminator='\n')
            csv_writer.writerow(row)

        print('food:', food_average)
        print('water:', water_average)

        if day_count > disaster_day:
            if disaster_type == 'covid':
                for x in businesses:
                    x.set_production_amount(disaster_severity)

        phase = 0

    screen.fill((255, 255, 255))

    for entity in all_sprites:
        screen.blit(entity.surf, entity.rect)
    img = font.render(str(day_count), True, (0, 0, 0))
    screen.blit(img, (20, 20))
    clock.tick()

    pygame.display.flip()
