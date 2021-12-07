# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 21:25:51 2021

@author: Aapo Kössi
"""

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import argparse


def find_account_button(buttons):
    for button in buttons:
        try:
            action_elem = button.find_element(By.TAG_NAME, 'use')
            action = action_elem.get_attribute('ng-href')
            match = action == '#o-account'
            if match: return button
        except: continue
    
def find_login_confirm_button(driver):
    buttons = driver.find_elements(By.TAG_NAME, 'button')
    for button in buttons:
        try:
            click = button.get_attribute('ng-click')
            match = click == 'login.onLogin()'
            if match: return button
        except: continue
    
def open_login_form(driver):
    flag = False
    items = driver.find_elements(By.TAG_NAME, 'o-menu-item')
    for item in items:
        try: 
            bind = item.get_attribute('ng-bind')
            match = bind == '::origin.localization.menuLogin'
            if match:
                item.click()
                flag = True
                break
        except: continue
    if not flag: print('something went wrong opening the login form :(')
    try:
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, 'input')))
        email, pw, _ = driver.find_elements(By.TAG_NAME, 'input')
    except TimeoutException: print('couldn\'t load login form, try again')
    return email, pw

def find_checkout_button(driver):
    footer_content = driver.find_element(By.TAG_NAME, 'o-dialog__footer__content')
    checkout = footer_content.find_element(By.TAG_NAME, 'button')
    return checkout


parser = argparse.ArgumentParser(description = 'yrittää ilmoittautua annettuun kide.app tapahtumaan')
parser.add_argument('URL',help='tapahtuman sivun täydellinen URL')
parser.add_argument('user',help='email of kide.app account')
parser.add_argument('password',help='password of kide.app account')
parser.add_argument('-n','--num_tickets', help='kuinka monta lippua lisätä ostoskoriin, jos mahdollista valita. Vakiokäyttäytymisenä lisää yhden lipun', default='1')
parser.add_argument('-vn','--variant_num',help='monenteenko ilmoittautumisvaihtoehtoon yrittää', type=int)
parser.add_argument('-v','--variant',help='minkä nimiseen ilmoittautumisvaihtoehtoon yrittää,'\
                    ' tämä priorisoidaan ennen variant_num argumenttia. Toimii siten, että tarkistaa, onko teksti '\
                        'osa jotakin ilmoittautumisvaihtoehtojen teksteistä alkaen ylhäältä sivulla.')

args = parser.parse_args()


capabilities = webdriver.DesiredCapabilities.CHROME.copy()
options = webdriver.ChromeOptions()
options.add_argument('ignore-certificate-errors')
options.add_argument('ignore-ssl-errors')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(desired_capabilities=capabilities, options = options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.get(args.URL)


buttons = driver.find_elements(By.TAG_NAME, 'button')
acc_button = find_account_button(buttons)
while True:
    try:
        WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.TAG_NAME, 'o-splash')))
        break
    except TimeoutException: continue
acc_button.click()
email_field, password_field = open_login_form(driver)

email_field.send_keys(args.user)
password_field.send_keys(args.password)

try:
    login_button = find_login_confirm_button(driver)
    login_button.click()
except: 
    print('login failed')

all_items = driver.find_elements(By.TAG_NAME, 'o-item')
for item in all_items:
    reserve_item = item.get_attribute('ng-repeat-start')
    if reserve_item: test_item = item
WebDriverWait(driver, 10).until(EC.element_to_be_clickable(test_item))

done = False
while True:
    all_items = driver.find_elements(By.TAG_NAME, 'o-item')
    items = []
    for item in all_items:
        reserve_item = item.get_attribute('ng-repeat-start')
        if reserve_item: items.append(item)
    print(len(items))

    texts = list(map(lambda x: x.find_elements(By.TAG_NAME, 'o-text__heading'), items))
    passed = False
    desired_items = [idx for idx, s in enumerate(texts) if args.variant in s]
    if len(desired_items)==0: passed=True
    print(passed)
    print(desired_items)
    if passed:
        if args.variant_num is not None:
            desired_items = [args.variant_num]
        else: desired_items = list(range(len(items)))
    for n in desired_items:
        disabled = items[n].get_attribute('disabled')
        if disabled: continue
        else:
            items[n].click()
            done = True
            try:
                quantity_select = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, 'select')))
                select_obj = Select(quantity_select)
                select_obj.select_by_visible_text(args.num_tickets)
                find_checkout_button(driver).click()
            except TimeoutException: pass
            break
    if done: break
    driver.refresh()
    WebDriverWait(driver, 2).until(EC.invisibility_of_element((By.TAG_NAME, 'o-splash')))
