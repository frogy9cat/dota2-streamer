from PIL import ImageGrab
import time

def create_tmp_image():                                         #for creating samples
    time.sleep(2)
    tmp_screen = ImageGrab.grab(bbox=(1700, 1025, 1900, 1075))
    tmp_screen.save("is_start_tmp.png")

create_tmp_image()