#!/usr/bin/env python3

'''
caching function that stores all of the indices of cities

speeds up the lookup time drastically
'''

################################################################################################################
## IMPORTS
################################################################################################################

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import numpy as np
import pandas as pd

import time
import datetime

import pickle

start_time = time.time()

################################################################################################################
## LOGIN
################################################################################################################

# Setup Chrome options
# Setup Chrome options
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--start-maximized")  # Still useful for viewport size
chrome_options.add_argument("--headless=new")  # This runs Chrome in background
chrome_options.add_argument("--disable-gpu")  # Recommended for headless
chrome_options.add_argument("--window-size=1920,1080")  # Set viewport explicitly
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)

# Read session cookie from file
try:
    with open('session_cookie', 'r') as cookie_file:
        session_id = cookie_file.read().strip()
        print(f"Read session ID from file: {session_id}")
except FileNotFoundError:
    print("Error: session_cookie file not found. Please create this file with your session ID.")
    driver.quit()
    exit(1)
except Exception as e:
    print(f"Error reading session_cookie file: {e}")
    driver.quit()
    exit(1)

# Check if session ID is empty
if not session_id:
    print("Error: session_cookie file is empty. Please add your session ID to this file.")
    driver.quit()
    exit(1)

# Navigate to the login page
driver.get("https://islands.smp.uq.edu.au/login.php")

# Wait for page to load
driver.implicitly_wait(1)

# Get the current PHPSESSID cookie (if it exists)
phpsessid_cookie = driver.get_cookie("PHPSESSID")
print(phpsessid_cookie)

# If the cookie doesn't exist yet, create a new one
if not phpsessid_cookie:
    print("PHPSESSID cookie not found, creating new one")
    # Use session ID from file
    driver.add_cookie({
        'name': 'PHPSESSID',
        'value': session_id,
        'path': '/',
        'domain': 'islands.smp.uq.edu.au'
    })
else:
    # Modify the existing cookie
    print(f"Found existing PHPSESSID: {phpsessid_cookie['value']}")
    # Replace with session ID from file
    driver.delete_cookie("PHPSESSID")
    driver.add_cookie({
        'name': 'PHPSESSID',
        'value': session_id,
        'path': '/',
        'domain': 'islands.smp.uq.edu.au'
    })

# Verify the cookie was set
updated_cookie = driver.get_cookie("PHPSESSID")
print(f"Updated PHPSESSID: {updated_cookie['value']}")

# Refresh the page to apply the cookie
driver.get("https://islands.smp.uq.edu.au/index.php")
driver.implicitly_wait(3)

# Check if login was successful
if "login.php" in driver.current_url:
    print("Login failed - still on login page. Check if your session ID is valid.")
    driver.quit()
    exit(1)
else:
    print("Successfully logged in!")

################################################################################################################
## ENUMERATE CONSTANTS AND DATA STRUCTURES
################################################################################################################

cities = driver.find_elements(By.XPATH, '//a[starts-with(@href, "village")]')
NUM_CITIES = len(cities)

buttons = []
for j in cities:
    buttons.append(j.find_element(By.XPATH, './/div[starts-with(@class, "town town")]'))

assert(len(buttons) == NUM_CITIES)

# cache datastructure
cache = []


################################################################################################################
## ITERATE
################################################################################################################

for cityindex in range(NUM_CITIES):
    #reprocess island page
    cities = driver.find_elements(By.XPATH, '//a[starts-with(@href, "village")]')
    buttons = []
    for j in cities:
        buttons.append(j.find_element(By.XPATH, './/div[starts-with(@class, "town town")]'))
    buttons[cityindex].click()
    driver.implicitly_wait(3)

    ### PERFORM SOME TASK HERE ###
    isl = driver.find_element(By.ID, "title")
    print("touched " + isl.text)

    houses = driver.find_elements(By.CLASS_NAME, "house")

    ids = driver.find_elements(By.CLASS_NAME, "houseid")

    hashid = {}
    trueindics = np.array(range(0, len(ids)))
    houseids = np.array([id.text for id in ids])
    setids = set(houseids)

    for house, indic in zip(houseids, trueindics):
        hashid[house] = int(indic)

    ### find the number of houses 
    NUM_HOUSES = houseids[-1]

    cache.append(hashid)

    ### END TASK//

    driver.back()
    driver.implicitly_wait(3)


print("cities cached: " + str(len(cache)))

# save the cache into a file
file = open(r'cache', 'wb')
pickle.dump(cache, file)
file.close()


end_time = time.time()

if __name__ == '__main__':
    execution_time = end_time - start_time
    print("Script completed normally.")
    print("Script runtime: " + str(datetime.timedelta(seconds=execution_time)))

    time.sleep(10)
    driver.close()
