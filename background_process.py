import pyautogui as pag
import random


def process(pag, random):
    pag.FAILSAFE = False

    while True:
        a = random.randint(1, 10)
        b = 1

        while b <= a:
            pag.PAUSE = random.randint(1, 5)
            pag.moveRel(random.randint(-500, 500), random.randint(-500, 500), duration=1)
            b += 1

        pag.press('capslock')
        pag.PAUSE = random.randint(1, 5)
        pag.press('capslock')
