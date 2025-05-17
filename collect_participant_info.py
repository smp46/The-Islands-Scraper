#!/usr/bin/env python3

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

import numpy as np
import pandas as pd
import time
import datetime

start_time = time.time()

################################################################################################################
## LOGIN
################################################################################################################

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
age_vec = []
gender_vec = []
island_vec = []
house_num_vec = []
education_vec = []
income_vec = []

################################################################################################################
## RUNTIME BODY
################################################################################################################

for df_count in range(0, SAMPLE_SIZE):
    try:
        print(f"\nGetting participant info {df_count+1}/{SAMPLE_SIZE}")

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
                age_vec.append(0)
                gender_vec.append("NA")
                island_vec.append("NA")
                house_num_vec.append(0)
                education_vec.append("NA")
                income_vec.append(0)
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
        age = 0
        gender = "NA"
        island = "NA"
        house_num = 0
        education_level = "NA"
        income = 0

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
                age_vec.append(0)
                gender_vec.append("NA")
                island_vec.append("NA")
                house_num_vec.append(0)
                education_vec.append("NA")
                income_vec.append(0)

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
                    age_vec.append(0)
                    gender_vec.append("NA")
                    island_vec.append("NA")
                    house_num_vec.append(0)
                    education_vec.append("NA")
                    income_vec.append(0)

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

                    # Try to click on "Stats" tab if present
                    try:
                        tab = wait.until(EC.element_to_be_clickable((By.ID, "t1tab")))
                        tab.click()
                        time.sleep(1)

                        # Find education and age
                        try:
                            summary = driver.find_elements(By.XPATH, "//tr")

                            # Education function
                            def get_education():
                                summary_string = ""
                                for element in summary:
                                    summary_string += " " + element.text
                                if summary_string.find("University") != -1:
                                    return "university"
                                elif summary_string.find("High School") != -1:
                                    return "high school"
                                elif summary_string.find("Elementary School") != -1:
                                    return "elementary school"
                                else:
                                    return "none"

                            education_level = get_education()

                            # Age
                            if len(summary) > 1:
                                age_parts = summary[1].text.split()
                                if len(age_parts) > 0:
                                    age = age_parts[0]

                            # Income, Island, House number
                            temp = 0
                            while temp < len(summary):
                                if "$" in summary[temp].text:
                                    income_text = summary[temp].text.split("$")
                                    if len(income_text) > 1:
                                        income = income_text[1].replace(",", "")

                                if "Lives in" in summary[temp].text:
                                    location = summary[temp].text.split()
                                    if len(location) > 3:
                                        island = location[2]
                                        house_num = location[3]
                                temp += 1
                        except Exception as e:
                            print(f"Error processing stats: {e}")
                    except Exception as e:
                        print(f"Error clicking stats tab: {e}")

                    # Try to click on "Chat" tab if present for gender
                    try:
                        tab = wait.until(EC.element_to_be_clickable((By.ID, "t3tab")))
                        tab.click()
                        time.sleep(1)

                        # Try to chat for gender
                        try:
                            chatbox = wait.until(
                                EC.presence_of_element_located((By.ID, "chatbox"))
                            )
                            chatbox.clear()
                            chatbox.send_keys("Are you male or female?")

                            submit_chat = wait.until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, '//button[@type="submit"]')
                                )
                            )
                            submit_chat.click()
                            time.sleep(2)

                            # Get response
                            chat_responses = driver.find_elements(
                                By.CLASS_NAME, "chatbot"
                            )
                            if chat_responses and len(chat_responses) > 0:
                                response = chat_responses[0].text
                                if (
                                    "male" in response.lower()
                                    and "female" not in response.lower()
                                ):
                                    gender = "male"
                                elif "female" in response.lower():
                                    gender = "female"
                                else:
                                    print("gender failed.")
                        except Exception as e:
                            print(f"Error with chat for gender: {e}")
                    except Exception as e:
                        print(f"Error clicking chat tab: {e}")

                except Exception as e:
                    print(f"Error collecting person data: {e}")

            except Exception as e:
                print(f"Error finding residents: {e}")
        except Exception as e:
            print(f"Error finding houses: {e}")

        # append the data
        name_vec.append(name)
        age_vec.append(age)
        gender_vec.append(gender)
        island_vec.append(island)
        house_num_vec.append(house_num)
        education_vec.append(education_level)
        income_vec.append(income)

        print(
            f"Collected info for participant {df_count+1}: {name}, age {age}, gender {gender}\n"
        )

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
        print(f"Unexpected error processing participant {df_count+1}: {e}")

        # Add empty data for skipped entries
        name_vec.append("NA")
        age_vec.append(0)
        gender_vec.append("NA")
        island_vec.append("NA")
        house_num_vec.append(0)
        education_vec.append("NA")
        income_vec.append(0)

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
        "age": age_vec,
        "gender": gender_vec,
        "island": island_vec,
        "house_num": house_num_vec,
        "education_level": education_vec,
        "income": income_vec,
    }
)

print(data.head())

# Save data as we go - create a backup in case the script crashes
try:
    data.to_csv("participant_info.csv")
    print("Data saved successfully to participant_info.csv")
except Exception as e:
    print(f"Error saving data: {e}")
    # Try to save to a backup location
    try:
        data.to_csv("participant_info_backup.csv")
        print("Data saved to backup file participant_info_backup.csv")
    except:
        print("Could not save data to backup file")

end_time = time.time()

if __name__ == "__main__":
    execution_time = end_time - start_time
    print("Script completed normally.")
    print("Script runtime: " + str(datetime.timedelta(seconds=execution_time)))
    print(f"Data collected for {len(data)} participants")

    time.sleep(5)
    driver.close()
