#!/usr/bin/env python3

SAMPLE_SIZE = 30

################################################################################################################
## IMPORTS
################################################################################################################

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

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
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--start-maximized")  # Keep the maximized window setting

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
## ENUMERATE CONSTANTS AND GLOBAL VARS
################################################################################################################


people_sampled = 0

# Use WebDriverWait to ensure elements are loaded
wait = WebDriverWait(driver, 10)
cities = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[starts-with(@href, "village")]')))
NUM_CITIES = len(cities)

buttons = []
for j in cities:
    try:
        # Try both class name patterns to handle potential differences
        button = j.find_element(By.XPATH, './/div[starts-with(@class, "town town")]')
        buttons.append(button)
    except NoSuchElementException:
        try:
            button = j.find_element(By.XPATH, './/div[starts-with(@class, "towndot towndot")]')
            buttons.append(button)
        except NoSuchElementException:
            print(f"Warning: Could not find button for city {j.get_attribute('href')}")

print(f"Found {len(buttons)} city buttons out of {NUM_CITIES} cities")
assert(len(buttons) > 0)  # Still need some buttons!

city = [] #rng_city
housers = [] #SAMPLE_INDEX
persons = [] #rng_person

################################################################################################################
## LOAD CACHE
################################################################################################################

try:
    cache_file = open(r'cache', 'rb')
    cache = pickle.load(cache_file)
    cache_file.close()
    # cache check assertion
    print(f"Loaded cache with {len(cache)} cities")
    assert(len(cache) == NUM_CITIES)
except (FileNotFoundError, AssertionError) as e:
    print(f"Error loading cache: {e}")
    exit(1)

################################################################################################################
## RUNTIME BODY
################################################################################################################

while people_sampled < SAMPLE_SIZE:
    try:
        # generate a random city
        rng_city = np.random.randint(0, high=NUM_CITIES-1)

        ## window check 1
        # Store the ID of the original window
        original_window = driver.current_window_handle

        # Loop through until we find a new window handle
        if driver.current_window_handle == original_window and len(driver.window_handles) > 1:
            driver.close()

        driver.switch_to.window(driver.window_handles[0])

        # Check we don't have other windows open already
        assert len(driver.window_handles) == 1

        # Ensure we're on the index page before trying to find cities
        if "index.php" not in driver.current_url:
            print("Not on index page, navigating back")
            driver.get("https://islands.smp.uq.edu.au/index.php")
            time.sleep(2)

        # Re-fetch cities and buttons as they might be stale
        wait = WebDriverWait(driver, 10)
        cities = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[starts-with(@href, "village")]')))
        buttons = []

        # Try both possible button class patterns
        for j in cities:
            try:
                button = j.find_element(By.XPATH, './/div[starts-with(@class, "town town")]')
                buttons.append(button)
            except NoSuchElementException:
                try:
                    button = j.find_element(By.XPATH, './/div[starts-with(@class, "towndot towndot")]')
                    buttons.append(button)
                except NoSuchElementException:
                    continue

        # Click on the random city button
        if rng_city < len(buttons):
            print(f"Clicking on city {rng_city}")
            click_btn = ActionChains(driver)
            click_btn.move_to_element(buttons[rng_city])
            click_btn.click()
            click_btn.perform()
            time.sleep(2)  # Give time for page to load
        else:
            print(f"City index {rng_city} is out of range for buttons array (len={len(buttons)})")
            continue

        ## window check 2
        # Store the ID of the original window
        original_window = driver.current_window_handle

        # Loop through until we find a new window handle
        if driver.current_window_handle == original_window and len(driver.window_handles) > 1:
            driver.close()

        driver.switch_to.window(driver.window_handles[0])

        # Check we don't have other windows open already
        assert len(driver.window_handles) == 1

        # Get houses with proper wait
        try:
            houses = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "house")))
            ids = driver.find_elements(By.CLASS_NAME, "houseid")

            # Find the number of houses
            NUM_HOUSES = int(list(cache[rng_city].keys())[-1])
            setids = set(cache[rng_city].keys())

            ## choose a random house
            # check that the house is valid with people
            max_attempts = 5  # Prevent infinite loops
            attempts = 0
            while attempts < max_attempts:
                rng_house = np.random.randint(1, high=NUM_HOUSES)
                if str(rng_house) in setids:
                    print("sample house " + str(rng_house))
                    break
                else:
                    print("Invalid House. resampling")
                    attempts += 1

            if attempts >= max_attempts:
                print("Too many invalid house attempts, trying a different city")
                driver.get("https://islands.smp.uq.edu.au/index.php")
                time.sleep(2)
                continue

            SAMPLE_INDEX = cache[rng_city][str(rng_house)]

            # Click the house with proper error handling
            try:
                if SAMPLE_INDEX < len(houses):
                    houses[SAMPLE_INDEX].click()
                    time.sleep(1)
                else:
                    print(f"House index {SAMPLE_INDEX} out of range (max={len(houses)-1})")
                    driver.get("https://islands.smp.uq.edu.au/index.php")
                    time.sleep(2)
                    continue
            except (StaleElementReferenceException, IndexError) as e:
                print(f"Error clicking house: {e}")
                driver.get("https://islands.smp.uq.edu.au/index.php")
                time.sleep(2)
                continue

            # Find residents with proper waiting
            try:
                resident_links = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, '//a[starts-with(@href, "islander.php")]')))
                num_residents = len(resident_links)

                if num_residents == 0:
                    print("empty house")
                    driver.get("https://islands.smp.uq.edu.au/index.php")
                    time.sleep(2)
                    continue
                else:
                    if num_residents == 1:
                        rng_person = 0
                    else:
                        rng_person = np.random.randint(low=0, high=num_residents-1)

                    resident_links[rng_person].click()
                    time.sleep(2)

                    # Get the name of the person
                    try:
                        isl = wait.until(EC.presence_of_element_located((By.ID, "title")))
                        print("touched " + isl.text)

                        # Check if their age is in the right age range
                        try:
                            tab = wait.until(EC.element_to_be_clickable((By.ID, "t1tab")))
                            tab.click()
                            time.sleep(1)

                            summary = driver.find_elements(By.XPATH, '//tr')
                            if len(summary) > 1:
                                age_text = summary[1].text.split()
                                if len(age_text) > 0:
                                    age = int(age_text[0])

                                    if age >= 18 and age <= 64:
                                        # Click the "Tasks" tab
                                        try:
                                            tab = wait.until(EC.element_to_be_clickable((By.ID, "t2tab")))
                                            tab.click()
                                            time.sleep(1)

                                            # Try to get consent
                                            try:
                                                obtain_elements = driver.find_elements(By.ID, "obtain")

                                                if len(obtain_elements) > 0:
                                                    try:
                                                        obtain = wait.until(EC.element_to_be_clickable(
                                                            (By.XPATH, '//a[starts-with(@href, "javascript:getConsent")]')))
                                                        obtain.click()
                                                        time.sleep(1)

                                                        # Check if consent was given
                                                        task_result = driver.find_elements(By.CLASS_NAME, "taskresulttask")
                                                        if task_result and "consented" in task_result[-1].text:
                                                            print("consented")

                                                            # Look for tasks_recent with explicit wait and error handling
                                                            try:
                                                                # Wait for the tasksrecent element to be present
                                                                tasks_recent = wait.until(
                                                                    EC.presence_of_element_located((By.ID, "tasksrecent")))

                                                                # Wait for the IQ test button to be clickable
                                                                ruler_test = wait.until(EC.element_to_be_clickable(
                                                                    (By.XPATH, """//span[@onclick="startTask('ruler'); return false;"]""")))
                                                                ruler_test.click()
                                                                time.sleep(1)

                                                                # Record the sample
                                                                city.append(rng_city)
                                                                housers.append(SAMPLE_INDEX)
                                                                persons.append(rng_person)

                                                                people_sampled += 1
                                                                print(f"Successfully sampled person {people_sampled}/{SAMPLE_SIZE}")

                                                            except (TimeoutException, NoSuchElementException) as e:
                                                                print(f"Error with tasks section: {e}")
                                                                # Try to navigate back to start over
                                                                try:
                                                                    island_home = driver.find_element(By.CLASS_NAME, "menu")
                                                                    island_home.click()
                                                                    time.sleep(2)
                                                                except:
                                                                    driver.get("https://islands.smp.uq.edu.au/index.php")
                                                                    time.sleep(2)
                                                        else:
                                                            print("Person declined. sample again")
                                                    except Exception as e:
                                                        print(f"Error getting consent: {e}")
                                                else:
                                                    print("No obtain element found")
                                            except Exception as e:
                                                print(f"Error with consent section: {e}")
                                        except Exception as e:
                                            print(f"Error with tasks tab: {e}")
                                    else:
                                        print(f"Incorrect age ({age}). sample again")
                                else:
                                    print("Could not parse age")
                            else:
                                print("Summary table not found")
                        except Exception as e:
                            print(f"Error with age check: {e}")
                    except Exception as e:
                        print(f"Error getting person info: {e}")
            except Exception as e:
                print(f"Error finding residents: {e}")
        except Exception as e:
            print(f"Error finding houses: {e}")

        # Return to index page for next iteration
        try:
            driver.get("https://islands.smp.uq.edu.au/index.php")
            time.sleep(2)
        except Exception as e:
            print(f"Error returning to index: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")
        # Try to recover and continue
        try:
            driver.get("https://islands.smp.uq.edu.au/index.php")
            time.sleep(2)
        except:
            print("Could not recover, restarting browser")
            driver.quit()
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("https://islands.smp.uq.edu.au/index.php")
            time.sleep(2)

## Create data frame and write to csv
data = pd.DataFrame(
    {
        "city_index": city,
        "sample_index": housers,
        "person_index": persons,
    }
)

print(data.head())
data.to_csv('sample_index.csv')

end_time = time.time()

if __name__ == '__main__':
    execution_time = end_time - start_time
    print("Script completed normally.")
    print("Script runtime: " + str(datetime.timedelta(seconds=execution_time)))
    print(f"Successfully sampled {people_sampled} people")

    time.sleep(10)
    driver.close()

