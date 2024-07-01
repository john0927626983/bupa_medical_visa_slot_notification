from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import requests
import threading

# Global flag to stop the loop
stop_flag = False
path = 'api_key.txt'

with open(path) as f:
    api_key = f.readline()

def line_notify(available_date):  
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    text = "\n"
    for x in available_date:
        text += x['Location'] + ', ' + x['Availability'] + '\n'
    params = {"message": text}

    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=params)
    print(r.status_code)  # 200
    
    if r.status_code == 200:
        return True
    else:
        return False
    
def main():
    # Open the website
    driver.get("https://bmvs.onlineappointmentscheduling.net.au/oasis/")

    # Click the "New Individual booking" button
    individual_booking_button = driver.find_element(By.ID, "ContentPlaceHolder1_btnInd")
    individual_booking_button.click()

    # Wait for the new page to load
    time.sleep(2)  # Adjust the sleep time if necessary

    # Enter the location (e.g., 3168)
    location_input = driver.find_element(By.ID, "ContentPlaceHolder1_SelectLocation1_txtSuburb")
    location_input.send_keys("3168")
    location_input.send_keys(Keys.RETURN)

    # Wait for the search button to become clickable and click it
    time.sleep(2)  # Adjust the sleep time if necessary
    search_button = driver.find_element(By.XPATH, "//div[@class='postcode-search']//input[@type='submit' and @value='Search']")
    search_button.click()

    # Wait for the results page to load
    time.sleep(2)  # Adjust the sleep time if necessary

    # Extract data from the resulting page
    # Locate the rows containing location information
    location_rows = driver.find_elements(By.XPATH, "//tbody/tr[contains(@class, 'trlocation')]")

    # Iterate over the rows and print availability for each location
    available_date = []
    for row in location_rows:
        location_name = row.find_element(By.CLASS_NAME, "tdlocNameTitle").text
        availability = row.find_element(By.CLASS_NAME, "tdloc_availability").text
        print(f"Location: {location_name}, Availability: {availability}")
        if availability != 'No available slot':
            available_date.append({"Location": location_name, "Availability": availability})
    
    if len(available_date) != 0:
        is_notified = line_notify(available_date)
        if is_notified:
            print("Success!")
        else:
            print("notify failed!")

def listen_for_stop():
    global stop_flag
    while True:
        user_input = input()
        if user_input.lower() == 'stop':
            stop_flag = True
            break

def main_loop():
    global stop_flag
    while not stop_flag:
        main()
        for _ in range(60):  # Pause for 60 seconds, checking for the stop flag each second
            if stop_flag:
                break
            time.sleep(1)

if __name__ == "__main__":
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--window-size=1920x1080")  # Set window size to avoid issues with element visibility
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

    # Initialize the WebDriver with options
    driver = webdriver.Chrome(options=chrome_options)

    # Start the stop command listener in a separate thread
    stop_listener = threading.Thread(target=listen_for_stop)
    stop_listener.start()

    try:
        main_loop()
    finally:
        driver.quit()
        print("Program exited.")
