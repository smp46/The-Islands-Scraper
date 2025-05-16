# The Islands Scraper
Faithful fork of the very based [island-scrape by BryanMui1](https://github.com/BryanMui1/island-scrape/).

The Islanders Scraper is a scraping tool built for the statistical simulation website [The Islands](https://islands.smp.uq.edu.au/login.php), it is a python script that allows researchers to automate sample collection. 

Collecting research samples from people:  
![Collecting research samples from people](https://github.com/user-attachments/assets/ce564d7f-a93b-4b9a-9dd2-d892f7cdfdcb)

Map of the entire Island: There's a lot of cities and people!  
![Map of the entire Island: There's a lot of cities and people!](https://github.com/user-attachments/assets/ab4bc1ce-92de-4c95-96b2-a75467515f53)

## Features:  
+ sample.py - automated sample choosing and collection
+ collect.py - automated collection of experiment results
+ cache.py - caching script that makes data collection exponentially faster

# Instructions:

1) Clone this repo:
```
git clone https://github.com/smp46/The-Islands-Scraper
```
2) Install dependencies with pip and ensure [Google Chrome](https://www.google.com/intl/en_au/chrome/) is installed on the system:
```
pip install -r requirements.txt
```
or
```
pip install selenium
pip install numpy
pip install pandas
```


3) Find your session cookie by following The Islands link on your Blackboard page. Then once The Islands is loaded, press `F12` to open the Developers Console. Navigate to `Application` and click on Cookies > `https://islands.smp.uq.edu.au`. The copy the value under the `Value` column for the row with  the name `PHPSESSID`. Paste this directly into the `session_cookie` file in the repo directory, and then save the file.

Cookies location: ![image](https://github.com/user-attachments/assets/e8819253-bbba-4c80-b67a-d6a767832e13)

Value to copy: ![image](https://github.com/user-attachments/assets/9c5741d3-7607-4d84-8be4-cf3f00c19800)


5) Generate a the cache file by running `cache.py`, this will open a Chrome window pre-load the islands for faster access later on.
```
python3 cache.py
```  


5) In sample.py edit the `SAMPLE_SIZE` constant on Line 3, then run `sample.py` to collect the samples.
```
python sample.py
```  
Outputs a **sample_index** csv file that notes the indices of the people that you sampled

6) collect the data by editing the data collection script collect.py. change the ###DO SOMETHING### block to your choosing and run it using:
```
python collect.py
```  
Visits every person sampled, collects the data and outputs it into a csv file

The data will be outputed into a file named **"data1.csv"** or can be chaneged to your choosing

**This project was built using Selenium and Python3, and works with the integrated Chrome Web Driver**
