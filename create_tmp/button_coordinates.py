import pyautogui

screenWidth, screenHeight = pyautogui.size()        # Getting the size of display.
print("Display:", screenWidth, screenHeight)        # 2560, 1440

currentMouseX, currentMouseY = pyautogui.position() # Getting coordinates(XY) of cursor.
print("Cursor: ", currentMouseX, currentMouseY)     # Cursor:  856 : 431
