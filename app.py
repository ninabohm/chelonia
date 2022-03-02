from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# app = Flask(__name__)
driver = webdriver.Chrome('./chromedriver')


def open_booking():
    url = "https://pretix.eu/Baeder/11/"
    driver.get(url)
    event_date = "2022-03-04"



# @app.route('/')
# def hello():
#     return 'Hello World :)'


if __name__ == '__main__':
    open_booking()
