import scrapy
from twisted.internet.defer import inlineCallbacks
from selenium import webdriver
import os
import time
from random import randint
import urllib.request
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class RecaptchaEngine(object):

    CAPTCHA_XPATH = '//iframe[contains(@src, "recaptcha")]/@src'

    def __init__(self, crawler):
        self.crawler = crawler

    def wait_between_random(self, min, max):
        time.sleep(randint(min, max))

    def download_audio(self, url):
        urllib.request.urlretrieve(url, "audio.mp3")

    def has_captcha(self, response):
        sel = scrapy.Selector(response)
        return len(sel.xpath(self.CAPTCHA_XPATH)) > 0

    def solve_captcha(self, response):
        sel = scrapy.Selector(response)

        curfilePath = os.path.abspath(__file__)
        curDir = os.path.abspath(
        os.path.join(curfilePath, os.pardir))
        parentDir = os.path.abspath(os.path.join(curDir, os.pardir))

        drive_path = os.path.join(parentDir, "geckodriver")
        driver = webdriver.Firefox(executable_path=drive_path)
        driver.get(response.url)
        recaptcha_iframe = driver.find_elements_by_tag_name("iframe")[0]
        recaptcha_challenge_iframe = driver.find_elements_by_tag_name("iframe")[1]
        recaptcha_url = recaptcha_iframe.get_attribute('src')
        btnSubmit = driver.find_element_by_id('recaptcha-demo-submit')

        driver.switch_to.frame(recaptcha_iframe)

        btnCheck = driver.find_element_by_id('recaptcha-anchor')
        btnCheck.click()
        self.wait_between_random(3,9)

        driver.switch_to.default_content()
        try:
            driver.switch_to.frame(recaptcha_challenge_iframe)

            recaptcha_audio_button = driver.find_element_by_id('recaptcha-audio-button')
            recaptcha_audio_button.click()

            recaptcha_audio = driver.find_element_by_id('audio-source')
            audio_url = recaptcha_audio.get_attribute('src')
            self.download_audio(audio_url)

            # TODO: Solve using speech recognition
            print('Recaptcha solved!')

        finally:
            print("No recaptcha challenge!")

        btnSubmit.click()
        driver.quit()
