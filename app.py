import pyautogui
from flask import Flask


# app = Flask(__name__)


def initialize_clicking():
    screen_width, screen_height = pyautogui.size()
    current_mouse_x = pyautogui.position()
    current_mouse_y = pyautogui.position()
    print(screen_width, screen_height, current_mouse_x, current_mouse_y)
    pyautogui.moveTo(100, 150)
    pyautogui.click()
    pyautogui.click(100, 200)
    pyautogui.write("hello world")


# @app.route('/')
# def hello():
#     return 'Hello World :)'


if __name__ == '__main__':
    initialize_clicking()
