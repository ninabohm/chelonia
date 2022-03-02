from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By

# app = Flask(__name__)
driver = webdriver.Chrome('./chromedriver')


def open_booking():
    url = "https://pretix.eu/Baeder/74/"
    datetime_selector = ".event-time[data-time='2022-03-04T14:30:00+00:00']"
    driver.get(url)
    booking_date = driver.find_element(By.CSS_SELECTOR, datetime_selector)
    booking_date.click()

    voucher_field = driver.find_element(By.ID, "voucher")
    voucher_field.click()
    voucher_field.send_keys("urbansportsclub")

    voucher_submit_button = driver.find_element(By.CSS_SELECTOR, "button[class='btn btn-block btn-primary']")
    voucher_submit_button.click()

    add_to_cart_button = driver.find_element(By.ID, "btn-add-to-cart")
    add_to_cart_button.click()

    checkout_button = driver.find_element(By.CSS_SELECTOR, "button[class='btn btn-block btn-primary']")
    checkout_button.click()

# @app.route('/')
# def hello():
#     return 'Hello World :)'


if __name__ == '__main__':
    open_booking()
