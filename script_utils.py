import pydirectinput
import time
import pyautogui
import cv2
from pynput.keyboard import Controller
import json


keyboard = Controller()

with open("heroes.json", "r") as j:
    heroes = json.loads(j.read())['heroes']

# Finding the HERO via his id
async def get_hero(hero_id):
    result = ""
    for hero in heroes:
        if hero_id == hero["id"]:
            result = hero['localized_name']
    if hero:
        return result
    else:
        return None


def open_write_console(command: list or str):
    pydirectinput.press('`')
    if type(command) == list:
        for one in command:
            for char in one:
                keyboard.press(char)
                keyboard.release(char)
            pydirectinput.press('enter')
    else:
        for char in command:
            keyboard.press(char)
            keyboard.release(char)
        pydirectinput.press('enter')
    time.sleep(0.01)
    pydirectinput.press('esc')


def cusotom_click(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.click()


def get_custom_screen(x1=0, y1=0, x2=0, y2=0):
    from PIL import ImageGrab
    return ImageGrab.grab(bbox=(x1, y1, x2, y2))


def make_img_grey(fp: str):
    img_rgb = cv2.imread(fp)
    img_grey = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)
    return img_grey


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