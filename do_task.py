#!/usr/bin/env python3

"""
Script to run tasks on participants from participants_ids.csv with complete task menu
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
import sys

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
## TASK MENU CONFIGURATION
################################################################################################################

# Dictionary of all available task categories and their tasks
task_menu = {
    "Documents": {
        "tasks": {
            "Academic Transcript": "gpa",
            "Birth Certificate": "birth",
            "Food Diary": "fooddiary",
            "Hypnogram": "hypnogram",
            "Report Card": "reportcard",
            "Tax Records": "taxrecords",
        },
    },
    "Physiology": {
        "tasks": {
            "Blood Pressure": "bloodpressure",
            "Body Temperature": "temperature",
            "Head Circumference": "head",
            "Height": "height",
            "Liver Size": "liver",
            "Oximeter": "spo2",
            "Oxygen Uptake Submaximal": "submax",
            "Peak Flow Meter": "peakflow",
            "Perceptual Voice Evaluation": "pve",
            "Pressure Pain Threshold Biceps": "pptbiceps",
            "Pressure Pain Threshold Trapezius": "ppttrapezius",
            "Pulse Meter": "pulse",
            "Respiratory Rate 2 mins": "breathing",
            "Skin Colouration": "skin",
            "Sleep Stage": "sleep",
            "Spirometer": "fev",
            "Visual Acuity": "visualacuity",
            "Vocal Frequency": "vocalfreq",
            "Waist Circumference": "waist",
            "Weight": "weight",
        },
    },
    "Blood Tests": {
        "tasks": {
            "Blood Adrenaline": "bloodadrenaline",
            "Blood Alcohol": "breathalyzer",
            "Blood APTT": "aptt",
            "Blood Cholesterol": "cholesterol",
            "Blood Cortisol": "cortisol",
            "Blood Endorphin": "endorphin",
            "Blood Estrogen": "estrogen",
            "Blood Ghrelin": "ghrelin",
            "Blood Glucose": "bloodglucose",
            "Blood Hematocrit": "hematocrit",
            "Blood Magnesium": "bloodmg",
            "Blood Melatonin": "melatonin",
            "Blood Oxygen": "pao2",
            "Blood Oxytocin": "oxytocin",
            "Blood Potassium": "potassium",
            "Blood Serotonin": "serotonin",
            "Blood Sodium": "sodium",
            "Blood Testosterone": "testosterone",
            "Blood Type": "bloodtype",
            "Blood Vitamin D": "vitd",
            "CDZ Lymphocyte Count": "cdz",
            "Gene Array (Chromosome A)": "genes1",
            "Gene Array (Chromosome B)": "genes2",
            "Gene Array (Combined)": "genes3",
            "White Blood Cell Count": "wbc",
        },
    },
    "Mental Tasks": {
        "tasks": {
            "Attention Test 10 mins": "attention",
            "Code Transmission Test 10 mins": "codetransmission",
            "Comprehension Test 10 mins": "comprehension",
            "Grooved Pegboard Test": "pegboard",
            "Happy Memories 1 min": "happy",
            "IQ Test": "iq",
            "Memory Game": "memorygame",
            "Memory Test Cards": "memorycards",
            "Memory Test Vocabulary": "memoryvocab",
            "Mental Arithmetic Basic 4 mins": "mental",
            "Mental Arithmetic Difficult 4 mins": "mentalhard",
            "Mini-Cog Test": "minicog",
            "Monetary Incentive": "money",
            "Personality Test": "ocean",
            "Play Chess Black": "chessblack",
            "Play Chess White": "chesswhite",
            "Problem Solving Basic 20 mins": "solving",
            "Puzzle Cube": "puzzlecube",
            "Sad Memories 1 min": "sad",
            "Stroop Test Control": "stroop1",
            "Stroop Test Interference": "stroop2",
            "Trivial Pursuit 5 mins": "trivial",
            "Vigilance Test": "vigilance",
        },
    },
    "Exercise": {
        "tasks": {
            "Arm Curl Test 30 s": "armcurl",
            "Arm Strength": "armstrength",
            "Brisk Walk Indoors 30 mins": "briskin30",
            "Brisk Walk Outdoors 30 mins": "brisk30",
            "Bungy Jump 25 m": "bungie25",
            "Bungy Jump 50 m": "bungie50",
            "Climb Tree 3 mins": "climbtree",
            "High-Intensity Interval Training 20 mins": "hiit",
            "Hop Outdoors 100 m": "hop100",
            "Jog Downhill 200 m": "jogdown",
            "Jog on the Spot 1 min": "jog",
            "Jog Outdoors 30 mins": "jog30",
            "Jog Uphill 200 m": "jogup",
            "Jumping 30 s": "jumping",
            "Light Jogging 30 mins": "joglight30",
            "Light Jogging 5 mins": "joglight",
            "Multistage Shuttle Run Test": "beep",
            "Relaxing Walk Indoors 60 mins": "walkin",
            "Relaxing Walk Outdoors 30 mins": "walk30",
            "Relaxing Walk Outdoors 60 mins": "walk",
            "Run Indoors 1 km": "runin1000",
            "Run Indoors 100 m": "runin100",
            "Run Indoors 30 mins": "runin30",
            "Run Indoors 5 km": "runin5000",
            "Run Outdoors 1 km": "run1000",
            "Run Outdoors 100 m": "run100",
            "Run Outdoors 30 mins": "run30",
            "Run Outdoors 5 km": "run5000",
            "Run Outdoors 5 km with Nadeline": "run5000f",
            "Strength Training 30 mins": "resistance",
            "Stretching and Holding 30 mins": "stretching30",
            "Stretching and Holding 5 mins": "stretching",
            "Swim Freestyle 1500 m": "freestyle1500",
            "Swim Freestyle 200 m": "freestyle200",
            "Swim Freestyle 30 mins": "swim30",
            "Swim Freestyle 50 m": "freestyle50",
            "Walk 7 m": "walk7",
            "Yoga 30 mins": "yoga",
        },
    },
    "Coordination": {
        "tasks": {
            "Balance Test Eyes Closed": "balance",
            "Balance Test Eyes Open": "balanceopen",
            "Ball Bounce Test 1 min": "bounce",
            "Clap Hands 1 min": "clapping",
            "Light Flash Test": "lightbulb",
            "Ruler Test": "ruler",
            "Timed Up and Go Test": "tug",
            "Timed Up and Go Test Cognitive": "tugc",
            "Timed Up and Go Test Manual": "tugm",
        },
    },
    "Alcoholic Drinks": {
        "tasks": {
            "Beer Light 250 mL": "lightbeer",
            "Beer Regular 250 mL": "regularbeer",
            "Guinness 250 mL": "guinness",
            "Mai Tai 100 mL": "maitai",
            "Red Wine 250 mL": "redwine",
            "Tequila 30 mL": "tequila",
            "Vodka 30 mL": "vodka",
            "White Wine 250 mL": "whitewine",
        },
    },
    "Cold Drinks": {
        "tasks": {
            "Apple Juice 250 mL": "applejuice",
            "Beer Non-alcoholic 250 mL": "nabeer",
            "Cola Caffeinated 250 mL": "cola",
            "Cola Caffeine-free 250 mL": "coladecaf",
            "Energy Drink 250 mL": "energydrink",
            "Energy Drink Caffeine-free 250 mL": "energydrinkcf",
            "Energy Drink Caffeine-free Sugar-free 250 mL": "energydrinkcfsf",
            "Energy Drink Sugar-free 250 mL": "energydrinksf",
            "Isotonic Drink 250 mL": "isotonic",
            "Kava 250 mL": "kava",
            "Lemonade 250 mL": "lemonade",
            "Lemonade Sugar-free 250 mL": "lemonadesf",
            "Milk Cold 250 mL": "milkcold",
            "Monosodium Glutamate 250 mL": "msg",
            "Muddy Water 250 mL": "muddy",
            "Nonalcoholic White Wine 250 mL": "nawine",
            "Salt Water 250 mL": "salt",
            "Sports Drink 250 mL": "sports",
            "Sports Drink Caffeinated 250 mL": "sportscaf",
            "Sugar Water 250 mL": "sugar",
            "Vitamin C Drink 250 mL": "vitc",
            "Water 250 mL": "water250",
            "Water 60 mL": "water60",
        },
    },
    "Hot Drinks": {
        "tasks": {
            "Coffee 250 mL": "coffee",
            "Coffee Decaffeinated 250 mL": "coffeedecaf",
            "Coffee Espresso 60 mL": "espresso",
            "Coffee Espresso Sugar 60 mL": "espressosugar",
            "Honey Drink 250 mL": "honeywater",
            "Milk Warm 250 mL": "milkwarm",
            "Tea 250 mL": "tea",
            "Tea Green 250 mL": "greentea",
            "Tea Herbal 250 mL": "herbaltea",
        },
    },
    "Injections": {
        "tasks": {
            "Adrenaline 10 µg": "adrenaline",
            "Erythropoietin 1000IU": "epo",
            "Glucose 10%": "glucose10",
            "Glucose 5%": "glucose5",
            "Hypertonic Saline 3 mL": "salinehyper",
            "Hypotonic Saline 3 mL": "salinehypo",
            "Influenza W42 50 µg": "w42",
            "Methamphetamine 10 mg": "meth10",
            "Methamphetamine 50 mg": "meth",
            "Morphine 20 mg": "morphineinj",
            "Natural Insulin 1 unit": "naturalinsulin",
            "Saline 3 mL": "saline",
            "Serotonin 10 µg": "serotonin10",
            "Somatropin 1000 µg": "somatropin",
            "Synthetic Insulin 1 unit": "syntheticinsulin",
            "Testosterone Enanthate 100 mg": "te",
        },
    },
    "Tablets": {
        "tasks": {
            "Alprazolam 1 mg": "alprazolam",
            "Aspirin 500 mg": "aspirin",
            "Caffeine Tablet 100 mg": "caffeine",
            "Codeine 60 mg": "codeine",
            "Dextroamphetamine 10 mg": "dextro",
            "Diazepam 10 mg": "valium",
            "Fish Oil 500 mg": "fishoil",
            "Isotretinoin 50 mg": "isotretinoin",
            "Lactose Tablet": "lactose",
            "Lysergic Acid Diethylamide 100 µg": "lsd",
            "Magnesium Tablet 250 mg": "magnesium",
            "Methamphetamine 10 mg": "meth10t",
            "Methylenedioxymethamphetamine 50 mg": "ecstasy",
            "Morphine 50 mg": "morphine",
            "Nicotine 2 mg": "nicotine",
            "Olive Oil 500 mg": "oliveoil",
            "Oxycodone 5 mg": "oxycodone",
            "Paracetemol 500 mg": "paracetemol",
            "Pseudoephedrine 30 mg": "pse",
            "Sildenafil Citrate 25 mg": "viagra25",
            "Sugar Tablet": "placebo",
            "Tramadol 50 mg": "tramadol",
            "Triazolam 250 µg": "triazolam",
            "Valerian 1 g": "valerian",
            "Vitamin D 50 µg": "vitamind",
        },
    },
    "Other Drugs": {
        "tasks": {
            "Chew Betel Nut 10 mins": "areca",
            "Chew Coca Leaves 10 mins": "coca",
            "Chew Dalpa Leaves 10 mins": "dalpa",
            "Chew Gum 10 mins": "chewinggum",
            "Chew Khat Leaves 10 mins": "khat",
            "Cigarette": "cigarette",
            "Cocaine Insufflation 50 mg": "cocaine",
            "Herbal Cigarette": "herbal",
            "Menthol Cigarette": "menthol",
            "Menthol Inhaler": "inhaler",
            "Nicotine Inhaler 2 mg": "inhalernicotine",
            "Psilocybin Mushrooms 10 g": "psilocybin",
            "Reefer": "marijuana",
            "Tea Cannabis 250 mL": "cannabis",
        },
    },
    "Environment": {
        "tasks": {
            "Imagine Professor 5 mins": "professor",
            "Immerse in Fresh Water 60 mins": "immersefresh",
            "Immerse in Salt Water 60 mins": "immersesalt",
            "Nap 15 mins": "nap15",
            "Nap 30 mins": "nap",
            "Nap 60 mins": "nap60",
            "Oxygen 15% 10 mins": "oxygen15",
            "Oxygen 30% 10 mins": "oxygen30",
            "Oxygen 35% 10 mins": "oxygen35",
            "Oxygen 40% 10 mins": "oxygen",
            "Read Book 30 mins": "book",
            "Rocking Chair 10 mins": "rocking",
            "Sit 10 mins": "sitting",
            "Sit 30 mins": "sitting30",
            "Sit at -20°C 10 mins": "freezer",
            "Sit at 40°C 10 mins": "heat40",
            "Sit at 5°C 10 mins": "cold",
            "Sit with Pet Cat 10 mins": "petcat",
            "Sit with Pet Crocodile 10 mins": "petcroc",
            "Sit with Pet Dog 10 mins": "petdog",
            "Socialising with Nadeline 60 mins": "social",
            "Sunbathe 30 mins": "sunbathe",
            "Swedish Massage 10 mins": "massage10",
            "Swedish Massage 2 mins": "massage",
            "Watch Television 30 mins": "tv",
            "Watch Television 60 mins": "tv60",
            "Water Salinity": "salinity",
        },
    },
    "Interventions": {
        "tasks": {
            "Cervical Cancer Education": "cervical",
            "Chlorine Tablet 28 days": "chlorine",
            "Exercise Education 14 days": "exerciseed",
            "Garden Project 14 days": "garden",
            "Hand Washing 28 days": "hands",
            "Healthy Food 14 days": "healthyfood",
            "Ketogenic Diet 14 days": "keto",
            "Reduce Alcohol 14 days": "sobriety",
            "Social Sports 14 days": "socialsports",
            "Vegetarian Diet 14 days": "vegetarian",
            "Water Filtration 28 days": "filter",
        },
    },
    "Food": {
        "tasks": {
            "Banana 100 g": "banana",
            "Bran Flakes 30 g": "branflakes",
            "Carrots 100 g": "carrots",
            "Chocolate Dark (40% cocoa) 50 g": "chocdark",
            "Chocolate Dark (70% cocoa) 50 g": "chocdark70",
            "Chocolate Dark (85% cocoa) 50 g": "chocdark85",
            "Chocolate Dark (99% cocoa) 50 g": "chocdark99",
            "Chocolate Milk 50 g": "chocmilk50",
            "Chocolate White 50 g": "chocwhite",
            "Corn Flakes 30 g": "cornflakes",
            "Cream Cheese 50 g": "creamcheese",
            "Fried Chips 50 g": "fries",
            "Liquorice 50 g": "liquorice",
            "Lollies 50g": "lollies",
            "Lollies Sugar-free 50g": "lolliessf",
            "Oranges 100 g": "oranges",
            "Pear 100 g": "pear",
            "Shiitake Mushrooms 10 g": "shiitake",
            "Watermelon 100 g": "watermelon",
            "White Bread 50 g": "bread",
            "White Button Mushroom 100 g": "button",
        },
    },
    "Music": {
        "tasks": {
            "Classical Music 10 mins": "musicclassical",
            "Country Music 10 mins": "musiccountry",
            "Dance Music 10 mins": "musicdance",
            "Heavy Metal Music 10 mins": "musicmetal",
            "Play Cello 10 mins": "cello",
            "Play Flute 10 mins": "flute",
            "Play Piano 10 mins": "piano",
        },
    },
    "Saliva Tests": {"tasks": {"Salivary Cortisol": "cortisal"}},
    "Urine Tests": {
        "tasks": {
            "Empty Bladder": "bladder",
            "Urine Amphetamines": "uamph",
            "Urine Creatinine": "creatinine",
            "Urine Dopamine": "dopamine",
            "Urine Ketones": "uketone",
            "Urine pH": "urineph",
        },
    },
    "Miscellaneous": {
        "tasks": {
            "Examine Wounds": "wound",
            "Glyphosate 360 g/L": "glyphosate",
            "Helium 500 mL": "helium",
            "Hypothalamic Lesion": "hypothalamus",
            "Lacerate": "lacerate",
            "Masturbate": "masturbate",
            "Radiation 1 Gy": "radiation",
            "Roll 20 dice": "dice20",
            "Roll a die": "die",
        },
    },
}

################################################################################################################
## HELPERS
################################################################################################################


def verify_task_started(driver):
    """Check if a task has started by looking for the progress canvas"""
    try:
        # Check if detailbox is displayed
        detailbox = driver.find_element(By.ID, "detailbox")
        if detailbox.get_attribute("style") == "display: block;":
            # Check for progress canvas
            try:
                progress_canvas = driver.find_element(By.ID, "progress")
                if progress_canvas:
                    # Get task details if available
                    try:
                        detail_text = driver.find_element(By.ID, "detail").text
                        return True, detail_text
                    except:
                        return True, "Task in progress (no detail text)"
            except:
                pass

        # Secondary check: look for recent task result
        try:
            task_results = driver.find_elements(By.CLASS_NAME, "taskresulttask")
            if task_results and len(task_results) > 0:
                return True, f"Task completed: {task_results[0].text}"
        except:
            pass

        return False, "Could not verify task started"
    except Exception as e:
        return False, f"Error checking task progress: {e}"


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
    df = pd.read_csv("participants_ids.csv")
    city_index = df["city_index"]
    sample_index = df["sample_index"]
    person_index = df["person_index"]

    SAMPLE_SIZE = len(df)
    print(f"Loaded {SAMPLE_SIZE} samples from participants_ids.csv")
except FileNotFoundError:
    print("Error: participants_ids.csv not found. Please create this file first.")
    driver.quit()
    exit(1)
except Exception as e:
    print(f"Error loading sample data: {e}")
    driver.quit()
    exit(1)

################################################################################################################
## TASK MENU SELECTION
################################################################################################################


def show_task_menu():
    """Display the task menu and get user selection"""
    print("\n" + "=" * 70)
    print("ISLAND TASK MENU".center(70))
    print("=" * 70)

    # Display categories
    categories = list(task_menu.keys())
    for i, category in enumerate(categories):
        print(f"{i+1}. {category}")

    # Get category selection
    while True:
        try:
            cat_choice = input("\nSelect a category (or 'q' to quit): ")
            if cat_choice.lower() == "q":
                return None, None

            cat_index = int(cat_choice) - 1
            if 0 <= cat_index < len(categories):
                selected_category = categories[cat_index]
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

    # Display tasks for selected category
    print("\n" + "-" * 70)
    print(f"TASKS IN: {selected_category}".center(70))
    print("-" * 70)

    tasks = list(task_menu[selected_category]["tasks"].keys())
    for i, task in enumerate(tasks):
        print(f"{i+1}. {task}")

    # Get task selection
    while True:
        try:
            task_choice = input("\nSelect a task (or 'b' to go back): ")
            if task_choice.lower() == "b":
                return show_task_menu()

            task_index = int(task_choice) - 1
            if 0 <= task_index < len(tasks):
                selected_task = tasks[task_index]
                task_code = task_menu[selected_category]["tasks"][selected_task]
                break
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

    return selected_task, task_code


print("Welcome to the Islands Task Runner")
print(
    "This script will run your selected task on participants from participants_ids.csv"
)
selected_task, task_code = show_task_menu()

if not selected_task or not task_code:
    print("Task selection cancelled. Exiting...")
    driver.quit()
    exit(0)

# Confirm selection
confirm = input(f"\nYou selected: {selected_task} ({task_code})\nProceed? (y/n): ")
if confirm.lower() != "y":
    print("Task cancelled. Exiting...")
    driver.quit()
    exit(0)

print(f"\nPreparing to run task: {selected_task}")
time.sleep(1)

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

            # Run the task
            try:
                # Look for the specified task
                task_span = None

                # First look in all potential task locations
                try:
                    task_spans = driver.find_elements(
                        By.XPATH,
                        f"//span[contains(@onclick, \"startTask('{task_code}')\")]",
                    )

                    if task_spans:
                        task_span = task_spans[0]
                except:
                    pass

                # Click the task if found
                if task_span:
                    print(f"Found {selected_task}, clicking...")
                    task_span.click()
                    time.sleep(2)

                    # Check for the specific detail box that shows the task has started
                    try:
                        # Verify that the task started correctly
                        success, detail_text = verify_task_started(driver)

                        if success:
                            tasks_completed += 1
                            print(
                                f"✅ Task successfully started for {name}! Total tasks: {tasks_completed}"
                            )
                            print(f"Task details: {detail_text}")

                            # Optional: Wait for a moment to see the progress
                            time.sleep(2)
                        else:
                            print(f"⚠️ Could not verify task started: {detail_text}")
                            tasks_failed += 1
                    except Exception as e:
                        print(f"Could not verify task started: {e}")
                        # Check for any task result as a backup method
                        task_results = driver.find_elements(
                            By.CLASS_NAME, "taskresulttask"
                        )
                        if task_results and task_code in task_results[-1].text.lower():
                            tasks_completed += 1
                            print(f"Task appears to have started based on task results")
                        else:
                            tasks_failed += 1
                            print("Could not confirm if task started successfully")
                else:
                    print(f"{selected_task} not found for this person")
                    tasks_failed += 1

            except Exception as e:
                print(f"Error running task: {e}")
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

print("\n" + "=" * 70)
print(f"TASK EXECUTION SUMMARY: {selected_task}".center(70))
print("=" * 70)
print(f"Total samples attempted: {SAMPLE_SIZE}")
print(f"Successfully completed tasks: {tasks_completed}")
print(f"Failed tasks: {tasks_failed}")
print(f"Success rate: {tasks_completed/SAMPLE_SIZE*100:.1f}%")
print(f"Script runtime: {str(datetime.timedelta(seconds=execution_time))}")
print("=" * 70)

time.sleep(5)
driver.close()
