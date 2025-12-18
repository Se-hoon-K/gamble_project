import random
import math


def get_random_int(min_val, max_val):
    return random.randint(min_val, max_val)


def random_normal():
    u1 = random.random()
    u2 = random.random()

    return math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)


def random_float(min_val, max_val):
    return random.uniform(min_val, max_val)