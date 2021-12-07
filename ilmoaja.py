# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 22:03:48 2021

@author: Aapo Kössi
"""

from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse
import time

parser = argparse.ArgumentParser(description = 'yrittää ilmoittautua annetulle nettisivulle ilmomasiinassa')
parser.add_argument('URL',help='tapahtuman sivun täydellinen URL')
args = parser.parse_args()

server = Server("C:\\Utility\\browsermob-proxy-2.1.4\\bin\\browsermob-proxy")
server.start()
proxy = server.create_proxy()
selenium_proxy = proxy.selenium_proxy()

capabilities = webdriver.DesiredCapabilities.CHROME.copy()
selenium_proxy.add_to_capabilities(capabilities)
options = webdriver.ChromeOptions()
options.add_argument('ignore-certificate-errors')
options.add_argument('ignore-ssl-errors')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(desired_capabilities=capabilities, options = options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.get(args.URL)

try:
    buttons = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'button'))
    )
except: 
    pass

while True:
    button = driver.find_element(By.TAG_NAME, 'button')
    disabled = button.get_attribute('disabled')
    if disabled:
        time.sleep(0.1)
    else: break

button.click()
#leaves webdriver open for the user to fill out the signup form

