#!/usr/bin/env python3

"""
Random Sampling Function:
- Choose a random city, a random house, and a random person
- If the person isnt a working class citizen(age 15 to 64), then redraw
- If participant declines, then redraw
- obtain n = 220 samples
"""

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
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)

import pandas as pd
import time
import datetime
import os

start_time = time.time()

################################################################################################################
## HELPERS
################################################################################################################


# Save data as we go with automatic file numbering
def get_available_filename(base_name, extension=".csv"):
    """Find an available filename by appending numbers if the file exists"""
    if not os.path.exists(f"{base_name}{extension}"):
        return f"{base_name}{extension}"

    counter = 1
    while os.path.exists(f"{base_name}{counter}{extension}"):
        counter += 1

    return f"{base_name}{counter}{extension}"


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
    with open("session_cookie", "r") as cookie_file:
        session_id = cookie_file.read().strip()
        print(f"Read session ID from file: {session_id}")
except FileNotFoundError:
    print(
        "Error: session_cookie file not found. Please create this file with your session ID."
    )
    driver.quit()
    exit(1)
except Exception as e:
    print(f"Error reading session_cookie file: {e}")
    driver.quit()
    exit(1)

# Check if session ID is empty
if not session_id:
    print(
        "Error: session_cookie file is empty. Please add your session ID to this file."
    )
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
    driver.add_cookie(
        {
            "name": "PHPSESSID",
            "value": session_id,
            "path": "/",
            "domain": "islands.smp.uq.edu.au",
        }
    )
else:
    # Modify the existing cookie
    print(f"Found existing PHPSESSID: {phpsessid_cookie['value']}")
    # Replace with session ID from file
    driver.delete_cookie("PHPSESSID")
    driver.add_cookie(
        {
            "name": "PHPSESSID",
            "value": session_id,
            "path": "/",
            "domain": "islands.smp.uq.edu.au",
        }
    )

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

# Set up a WebDriverWait object for explicit waits
wait = WebDriverWait(driver, 10)

################################################################################################################
## ENUMERATE CONSTANTS AND GLOBAL VARS(LOAD INDEX DATA TOO)
################################################################################################################

# making dataframe
df = pd.read_csv("participant_ids.csv")
city_index = df["city_index"]
sample_index = df["sample_index"]
person_index = df["person_index"]

SAMPLE_SIZE = len(df)
people_sampled = 0

try:
    cities = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, '//a[starts-with(@href, "village")]')
        )
    )
    NUM_CITIES = len(cities)

    buttons = []
    for j in cities:
        try:
            button = j.find_element(
                By.XPATH, './/div[starts-with(@class, "town town")]'
            )
            buttons.append(button)
        except NoSuchElementException:
            try:
                button = j.find_element(
                    By.XPATH, './/div[starts-with(@class, "towndot towndot")]'
                )
                buttons.append(button)
            except NoSuchElementException:
                print(
                    f"Warning: Could not find button for city {j.get_attribute('href')}"
                )

    print(f"Found {len(buttons)} cities out of {NUM_CITIES}")
    assert len(buttons) > 0
except Exception as e:
    print(f"Error finding cities: {e}")
    driver.quit()
    exit(1)

# make data vectors
name_vec = []
result_vec = []

################################################################################################################
## RUNTIME BODY
################################################################################################################

for df_count in range(0, SAMPLE_SIZE):
    try:
        print(f"\nProcessing sample {df_count+1}/{SAMPLE_SIZE}")

        ## window check 1
        # Store the ID of the original window
        original_window = driver.current_window_handle

        # Loop through until we find a new window handle
        if (
            driver.current_window_handle == original_window
            and len(driver.window_handles) > 1
        ):
            driver.close()

        driver.switch_to.window(driver.window_handles[0])

        # Check we don't have other windows open already
        assert len(driver.window_handles) == 1

        # Make sure we're on the islands page
        if "index.php" not in driver.current_url:
            print("Not on index page, navigating back")
            driver.get("https://islands.smp.uq.edu.au/index.php")
            time.sleep(2)

        # Re-fetch cities and buttons to prevent stale elements
        try:
            cities = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//a[starts-with(@href, "village")]')
                )
            )
            buttons = []
            for j in cities:
                try:
                    button = j.find_element(
                        By.XPATH, './/div[starts-with(@class, "town town")]'
                    )
                    buttons.append(button)
                except NoSuchElementException:
                    try:
                        button = j.find_element(
                            By.XPATH, './/div[starts-with(@class, "towndot towndot")]'
                        )
                        buttons.append(button)
                    except NoSuchElementException:
                        continue

            # Check if we have a valid city index
            current_city_index = city_index[df_count]
            if current_city_index < 0 or current_city_index >= len(buttons):
                print(
                    f"Warning: City index {current_city_index} out of range, skipping"
                )

                # Initialize empty data for skipped entries
                name_vec.append("NA")
                result_vec.append(0)
                continue

            # Click on the city
            click_btn = ActionChains(driver)
            click_btn.move_to_element(buttons[current_city_index])
            click_btn.click()
            click_btn.perform()
            time.sleep(2)

        except Exception as e:
            print(f"Error finding/clicking city: {e}")
            driver.get("https://islands.smp.uq.edu.au/index.php")
            time.sleep(2)
            continue

        ## window check 2
        # Store the ID of the original window
        original_window = driver.current_window_handle

        # Loop through until we find a new window handle
        if (
            driver.current_window_handle == original_window
            and len(driver.window_handles) > 1
        ):
            driver.close()

        driver.switch_to.window(driver.window_handles[0])

        # Check we don't have other windows open already
        assert len(driver.window_handles) == 1

        # initialize vars
        name = "NA"
        result = 0

        try:
            # Wait for houses to load
            houses = wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "house"))
            )

            # Check if the sample index is valid
            current_sample_index = sample_index[df_count]
            if current_sample_index < 0 or current_sample_index >= len(houses):
                print(
                    f"Warning: House index {current_sample_index} out of range, skipping"
                )

                # Initialize empty data for skipped entries
                name_vec.append("NA")
                result_vec.append(0)

                # Go back to the index page
                driver.get("https://islands.smp.uq.edu.au/index.php")
                time.sleep(2)
                continue

            # Click the house
            houses[current_sample_index].click()
            time.sleep(2)

            # Wait for resident links to load
            try:
                resident_links = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, '//a[starts-with(@href, "islander.php")]')
                    )
                )
                num_residents = len(resident_links)

                if num_residents == 0:
                    print("Empty house, no residents found")

                    # Initialize empty data for skipped entries
                    name_vec.append("NA")
                    result_vec.append(0)

                    # Go back to the index page
                    driver.get("https://islands.smp.uq.edu.au/index.php")
                    time.sleep(2)
                    continue

                # Check if person index is valid
                current_person_index = person_index[df_count]
                if current_person_index < 0 or current_person_index >= num_residents:
                    print(
                        f"Warning: Person index {current_person_index} out of range, using index 0"
                    )
                    current_person_index = 0

                # Click on the person
                resident_links[current_person_index].click()
                time.sleep(2)

                ### Perform Data Collection ###
                try:
                    # Get the person's name
                    isl = wait.until(EC.presence_of_element_located((By.ID, "title")))
                    print("touched " + isl.text)

                    # Get name from header
                    try:
                        header = driver.find_element(
                            By.CLASS_NAME, "crumb"
                        ).text.split()
                        if len(header) >= 3:
                            name = header[1] + " " + header[2]
                    except Exception as e:
                        print(f"Error getting name: {e}")

                    # Try to click on "Tasks" tab if present
                    try:
                        tab = wait.until(EC.element_to_be_clickable((By.ID, "t2tab")))
                        tab.click()
                        time.sleep(1)

                        # Get result information
                        try:
                            task_results = driver.find_elements(
                                By.CLASS_NAME, "taskresultresult"
                            )

                            if task_results and len(task_results) > 0:
                                result = task_results[0].text
                        except Exception as e:
                            print(f"Error getting result info: {e}")
                    except Exception as e:
                        print(f"Error clicking tasks tab: {e}")

                except Exception as e:
                    print(f"Error collecting person data: {e}")

            except Exception as e:
                print(f"Error finding residents: {e}")
        except Exception as e:
            print(f"Error finding houses: {e}")

        # append the data
        name_vec.append(name)
        result_vec.append(result)

        print(f"Collected data for sample {df_count+1}: {name}, result {result}")

        # Return to home page
        try:
            # First try to click the menu button
            try:
                island_home = wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "menu"))
                )
                island_home.click()
                time.sleep(2)
            except Exception:
                # If that fails, navigate directly to index page
                driver.get("https://islands.smp.uq.edu.au/index.php")
                time.sleep(2)
        except Exception as e:
            print(f"Error returning to home: {e}")
            driver.get("https://islands.smp.uq.edu.au/index.php")
            time.sleep(2)

    except Exception as e:
        print(f"Unexpected error processing sample {df_count+1}: {e}")

        # Add empty data for skipped entries
        name_vec.append("NA")
        result_vec.append(0)

        # Try to get back to the index
        try:
            driver.get("https://islands.smp.uq.edu.au/index.php")
            time.sleep(2)
        except:
            print("Could not navigate back to index")

## Create data frame and write to csv
data = pd.DataFrame(
    {
        "name": name_vec,
        "result": result_vec,
    }
)

print(data.head())

try:
    # Get a filename that doesn't exist yet
    filename = get_available_filename("latest_result")
    data.to_csv(filename)
    print(f"Data saved successfully to {filename}")
except Exception as e:
    print(f"Error saving data: {e}")
    # Try to save to a backup location
    try:
        backup_filename = get_available_filename("latest_result_backup")
        data.to_csv(backup_filename)
        print(f"Data saved to backup file {backup_filename}")
    except Exception as e:
        print(f"Could not save data to backup file: {e}")

end_time = time.time()

if __name__ == "__main__":
    execution_time = end_time - start_time
    print("Script completed normally.")
    print("Script runtime: " + str(datetime.timedelta(seconds=execution_time)))
    print(f"Data collected for {len(data)} samples")

    time.sleep(5)
    driver.close()
