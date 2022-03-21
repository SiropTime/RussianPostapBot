from random import randint

MAIN_SKILL = 20
ADD_SKILL = 100


class Location:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.coordinates = (0.0, 0.0)
        self.neighbours = ""

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Animal:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.area = ""


class Item:
    def __init__(self):
        self.name = ""
        self.quantity = 0
        self.description = ""

    def __str__(self):
        return self.name + " " + self.description + " " + str(self.quantity)

    def __repr__(self):
        return self.name + " " + self.description + " " + str(self.quantity)


def check_skill(skill: int, bonuses=0, limit=(-5, 105)) -> bool:
    if type is None:
        if randint(limit[0], limit[1]) < skill + bonuses:
            return True
        else:
            return False
