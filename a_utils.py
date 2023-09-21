import pydirectinput
import time
import pyautogui
from pynput.keyboard import Controller


keyboard = Controller()

def open_write_console(command):
    pydirectinput.press('`')
    for char in command:
        keyboard.press(char)
        keyboard.release(char)
    pydirectinput.press('enter')
    time.sleep(0.01)
    pydirectinput.press('esc')


def cusotom_click(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.click()


def select_hero(num):
    if num == 1:
        cusotom_click(575, 20)
    elif num == 2:
        cusotom_click(638, 20)
    elif num == 3:
        cusotom_click(700, 20)
    elif num == 4:
        cusotom_click(762, 20)
    elif num == 5:
        cusotom_click(825, 20)
    elif num == 6:
        cusotom_click(1092, 20)
    elif num == 7:
        cusotom_click(1155, 20)
    elif num == 8:
        cusotom_click(1217, 20)
    elif num == 9:
        cusotom_click(1281, 20)
    elif num == 10:
        cusotom_click(1338, 20)
    pyautogui.moveTo(800, 100)