import random
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

@pytest.fixture(scope="module")
def driver():
    # Set up mobile emulation
    mobile_emulation = {
        "deviceName": "Pixel 2"
    }
    chrome_options = Options()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()

def close_warning_if_present(driver):
    try:
        warning_start_watching_button = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-a-target='content-classification-gate-overlay-start-watching-button']")))
        warning_start_watching_button.click()
    except TimeoutException:
        pass
    except NoSuchElementException:
        pass

def test_twitch_mobile_search(driver):
    driver.get("https://m.twitch.tv/")

    search_icon = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[aria-label='Search']")))
    search_icon.click()
    
    search_input = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[data-a-target='tw-input']")))
    search_input.send_keys("StarCraft II")
    search_input.send_keys(Keys.RETURN)

    # Wait for search results to load
    try:
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "img[class='tw-image']")))
    except TimeoutException:
        pytest.fail("Search results did not load within 10 seconds")

    actions = ActionChains(driver)
    for _ in range(2):
        time.sleep(1)
        actions.send_keys(Keys.PAGE_DOWN).perform()

    
    streamers_list = driver.find_elements(By.CSS_SELECTOR, "img[class='tw-image']")
    random_index = random.randint(0, len(streamers_list) - 1)
    streamer = streamers_list[random_index]
    streamer.click()

    close_warning_if_present(driver)

    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "video[playsinline]")))
    except TimeoutException:
        pytest.fail("Streamer page did not load within 10 seconds")

    driver.save_screenshot("streamer_page.png")