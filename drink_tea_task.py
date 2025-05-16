#!/usr/bin/env python3

"""
Simplified script to run the Tea Cannabis task on participants from sample_index.csv
"""

################################################################################################################
## IMPORTS
################################################################################################################

from selenium import webdriver
from selenium.webdriver.common.by import By
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

################################################################################################################
## SETUP
################################################################################################################

start_time = time.time()

# Setup Chrome options
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--start-maximized")

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

# Set up counter
tasks_completed = 0
tasks_failed = 0

################################################################################################################
## LOGIN
################################################################################################################

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

# Navigate to the login page
driver.get("https://islands.smp.uq.edu.au/login.php")
driver.implicitly_wait(1)

# Set the PHPSESSID cookie
driver.delete_all_cookies()  # Clear existing cookies
driver.add_cookie(
    {
        "name": "PHPSESSID",
        "value": session_id,
        "path": "/",
        "domain": "islands.smp.uq.edu.au",
    }
)

# Go to index page
driver.get("https://islands.smp.uq.edu.au/index.php")
time.sleep(2)

# Check if login was successful
if "login.php" in driver.current_url:
    print("Login failed - still on login page. Check if your session ID is valid.")
    driver.quit()
    exit(1)
else:
    print("Successfully logged in!")

################################################################################################################
## LOAD SAMPLE DATA
################################################################################################################

# Load the sample data from CSV
try:
    df = pd.read_csv("sample_index.csv")
    city_index = df["city_index"]
    sample_index = df["sample_index"]
    person_index = df["person_index"]

    SAMPLE_SIZE = len(df)
    print(f"Loaded {SAMPLE_SIZE} samples from sample_index.csv")
except FileNotFoundError:
    print("Error: sample_index.csv not found. Please create this file first.")
    driver.quit()
    exit(1)
except Exception as e:
    print(f"Error loading sample data: {e}")
    driver.quit()
    exit(1)

################################################################################################################
## MAIN LOOP
################################################################################################################

for df_count in range(0, SAMPLE_SIZE):
    try:
        print(f"\nProcessing sample {df_count+1}/{SAMPLE_SIZE}")

        # Make sure we're on the index page
        if "index.php" not in driver.current_url:
            driver.get("https://islands.smp.uq.edu.au/index.php")
            time.sleep(2)

        # Clean up windows if needed
        if len(driver.window_handles) > 1:
            original_window = driver.current_window_handle
            for handle in driver.window_handles:
                if handle != original_window:
                    driver.switch_to.window(handle)
                    driver.close()
            driver.switch_to.window(driver.window_handles[0])

        # Find cities and buttons
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

        # Check if city index is valid
        current_city_index = city_index[df_count]
        if current_city_index < 0 or current_city_index >= len(buttons):
            print(f"Invalid city index {current_city_index}, skipping")
            tasks_failed += 1
            continue

        # Click the city
        print(f"Clicking city {current_city_index}")
        click_btn = ActionChains(driver)
        click_btn.move_to_element(buttons[current_city_index])
        click_btn.click()
        click_btn.perform()
        time.sleep(2)

        # Find houses
        houses = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "house"))
        )

        # Check if house index is valid
        current_sample_index = sample_index[df_count]
        if current_sample_index < 0 or current_sample_index >= len(houses):
            print(f"Invalid house index {current_sample_index}, skipping")
            tasks_failed += 1
            continue

        # Click the house
        print(f"Clicking house at index {current_sample_index}")
        houses[current_sample_index].click()
        time.sleep(2)

        # Find residents
        resident_links = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//a[starts-with(@href, "islander.php")]')
            )
        )

        if len(resident_links) == 0:
            print("Empty house, no residents found")
            tasks_failed += 1
            continue

        # Check if person index is valid
        current_person_index = person_index[df_count]
        if current_person_index < 0 or current_person_index >= len(resident_links):
            print(f"Invalid person index {current_person_index}, using 0 instead")
            current_person_index = 0

        # Click the person
        resident_links[current_person_index].click()
        time.sleep(2)

        # Get the person's name
        try:
            name = wait.until(EC.presence_of_element_located((By.ID, "title"))).text
            print(f"Selected person: {name}")
        except:
            name = "Unknown Person"

        # Go to Tasks tab
        try:
            tab = wait.until(EC.element_to_be_clickable((By.ID, "t2tab")))
            tab.click()
            time.sleep(1)

            # Check if we need consent
            obtain_elements = driver.find_elements(By.ID, "obtain")
            if len(obtain_elements) > 0:
                try:
                    obtain = wait.until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                '//a[starts-with(@href, "javascript:getConsent")]',
                            )
                        )
                    )
                    obtain.click()
                    time.sleep(2)

                    # Check if consent was given
                    task_result = driver.find_elements(By.CLASS_NAME, "taskresulttask")
                    if not task_result or "consented" not in task_result[-1].text:
                        print(f"Person declined consent")
                        tasks_failed += 1
                        continue
                except Exception as e:
                    print(f"Error getting consent: {e}")
                    tasks_failed += 1
                    continue

            # Run the Cannabis task
            try:
                # Look for the task
                cannabis_task = None

                # First check tasksrecent
                try:
                    tasks_recent = wait.until(
                        EC.presence_of_element_located((By.ID, "tasksrecent"))
                    )
                    cannabis_spans = tasks_recent.find_elements(
                        By.XPATH,
                        ".//span[contains(@onclick, \"startTask('cannabis')\")]",
                    )

                    if cannabis_spans:
                        cannabis_task = cannabis_spans[0]
                except:
                    pass

                # If not found in tasksrecent, check taskspossible
                if not cannabis_task:
                    try:
                        tasks_possible = wait.until(
                            EC.presence_of_element_located((By.ID, "taskspossible"))
                        )
                        cannabis_spans = tasks_possible.find_elements(
                            By.XPATH,
                            ".//span[contains(@onclick, \"startTask('cannabis')\")]",
                        )

                        if cannabis_spans:
                            cannabis_task = cannabis_spans[0]
                    except:
                        pass

                # If still not found, look everywhere
                if not cannabis_task:
                    cannabis_spans = driver.find_elements(
                        By.XPATH,
                        "//span[contains(@onclick, \"startTask('cannabis')\")]",
                    )

                    if cannabis_spans:
                        cannabis_task = cannabis_spans[0]

                # Click the task if found
                if cannabis_task:
                    print("Found cannabis task, clicking...")
                    cannabis_task.click()
                    time.sleep(2)

                    # Check for the specific detail box that shows the task has started
                    try:
                        detail_box = wait.until(
                            EC.presence_of_element_located((By.ID, "detailbox"))
                        )
                        detail_text = driver.find_element(By.ID, "detail").text

                        # Check if the task has started correctly
                        if (
                            "drinking 250 mL of tea" in detail_text
                            and "cannabis" in detail_text
                        ):
                            tasks_completed += 1
                            print(
                                f"✅ Cannabis task successfully started for {name}! Total tasks: {tasks_completed}"
                            )
                            print(f"Task details: {detail_text}")

                            # Optional: Wait for a moment to see the progress
                            time.sleep(3)
                        else:
                            print(
                                f"Task may have started but with unexpected text: {detail_text}"
                            )
                            tasks_completed += (
                                1  # Still count it as completed since the task started
                            )
                    except Exception as e:
                        print(f"Could not verify task started: {e}")
                        # Check for any task result as a backup method
                        task_results = driver.find_elements(
                            By.CLASS_NAME, "taskresulttask"
                        )
                        if task_results and "cannabis" in task_results[-1].text.lower():
                            tasks_completed += 1
                            print(f"Task appears to have started based on task results")
                        else:
                            tasks_failed += 1
                            print("Could not confirm if task started successfully")
                else:
                    print("Cannabis task not found for this person")
                    tasks_failed += 1

            except Exception as e:
                print(f"Error running cannabis task: {e}")
                tasks_failed += 1
        except Exception as e:
            print(f"Error with tasks tab: {e}")
            tasks_failed += 1

        # Return to index page for next iteration
        try:
            driver.get("https://islands.smp.uq.edu.au/index.php")
            time.sleep(2)
        except Exception as e:
            print(f"Error returning to index: {e}")

    except Exception as e:
        print(f"Unexpected error processing sample {df_count+1}: {e}")
        tasks_failed += 1

        # Try to recover
        try:
            driver.get("https://islands.smp.uq.edu.au/index.php")
            time.sleep(2)
        except:
            print("Could not recover, refreshing session")
            driver.quit()
            driver = webdriver.Chrome(options=chrome_options)

            # Re-login
            driver.get("https://islands.smp.uq.edu.au/login.php")
            time.sleep(1)
            driver.delete_all_cookies()
            driver.add_cookie(
                {
                    "name": "PHPSESSID",
                    "value": session_id,
                    "path": "/",
                    "domain": "islands.smp.uq.edu.au",
                }
            )
            driver.get("https://islands.smp.uq.edu.au/index.php")
            time.sleep(2)

# Final report
end_time = time.time()
execution_time = end_time - start_time

print("\n" + "=" * 50)
print("TASK EXECUTION SUMMARY")
print("=" * 50)
print(f"Total samples attempted: {SAMPLE_SIZE}")
print(f"Successfully completed tasks: {tasks_completed}")
print(f"Failed tasks: {tasks_failed}")
print(f"Success rate: {tasks_completed/SAMPLE_SIZE*100:.1f}%")
print(f"Script runtime: {str(datetime.timedelta(seconds=execution_time))}")
print("=" * 50)

time.sleep(5)
driver.close()
