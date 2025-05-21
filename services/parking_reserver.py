# services/parking_reserver.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    WebDriverException,
    StaleElementReferenceException,
)


def select_furthest_available_date(driver):
    wait = WebDriverWait(driver, 10)

    date_wrapper = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.css-1tn2x14"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", date_wrapper)
    date_wrapper.click()

    while True:
        try:
            driver.find_element(By.CSS_SELECTOR, "button[disabled].css-tkykqg")
            break
        except:
            next_arrow = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.css-tkykqg"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", next_arrow)
            next_arrow.click()
            time.sleep(0.5)

    available_days = driver.find_elements(
        By.CSS_SELECTOR, "div.rmdp-day:not(.rmdp-disabled) .day"
    )

    if not available_days:
        raise Exception("❌ No available days found in the calendar.")

    last_day = available_days[-1]
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_day)
    last_day.click()
    print("✅ Clicked the furthest available day.")


def reserve_parking(
    driver,
    building_name="BG - Plovdiv",
    subarea="Parking Spaces Plovdiv",
    spot_prefix="PB",
):
    wait = WebDriverWait(driver, 20)

    try:
        first_row_xpath = "(//tr[contains(@class, 'buildings-table-row')])[1]"
        first_row = wait.until(EC.element_to_be_clickable((By.XPATH, first_row_xpath)))
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", first_row
        )
        time.sleep(0.5)
        try:
            first_row.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", first_row)
    except Exception as e:
        raise Exception(f"Couldn't click first building row: {building_name}", e)

    time.sleep(2)

    try:
        subarea_xpath = (
            f"//div[contains(@class, 'text-ellipsis') and contains(., '{subarea}')]"
        )
        subarea_elem = wait.until(EC.element_to_be_clickable((By.XPATH, subarea_xpath)))
        subarea_elem.click()
    except Exception as e:
        raise Exception(f"Couldn't find or click subarea: {subarea}", e)

    time.sleep(2)

    try:
        list_button_xpath = "//button[.//h6[text()='List']]"
        list_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, list_button_xpath))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", list_button)
        list_button.click()
        time.sleep(2)
    except Exception as e:
        raise Exception("Couldn't switch to list view", e)

    try:
        select_furthest_available_date(driver)
        time.sleep(2)
    except Exception as e:
        raise Exception("Failed to select furthest available date. Error: " + str(e))

    find_available_parking_spot(driver, spot_prefix)

    time.sleep(2)

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "booking-container")))
        container = wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "interactive-loading-button-container")
            )
        )

        book_btn = container.find_element(
            By.XPATH, ".//button[contains(string(), 'Book')]"
        )

        print(book_btn.get_attribute("outerHTML"))

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", book_btn
        )
        time.sleep(0.3)

        try:
            actions = ActionChains(driver)
            actions.move_to_element(book_btn).pause(0.5).click().perform()
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: "Release"
                    in d.find_element(
                        By.CLASS_NAME, "interactive-loading-button-container"
                    ).text
                )
                print("[✓] Reservation confirmed (button changed to Release).")
            except StaleElementReferenceException:
                print(
                    "[✓] Reservation likely confirmed — DOM updated and original element became stale."
                )
            except TimeoutException:
                print(
                    "[!] Timeout waiting for confirmation. Might be a slow UI update."
                )

        except ElementClickInterceptedException:
            print("[!] Normal click failed. Trying JS click...")
            driver.execute_script("arguments[0].click();", book_btn)
            print("[✓] BOOK button clicked via JavaScript.")

    except TimeoutException:
        print("[!] BOOK button not found in time.")
    except Exception as e:
        print(f"[!] Unexpected error clicking BOOK: {e}")

    return f"Reserved parking at {building_name} > {subarea}"


def find_available_parking_spot(driver, spot_prefix="PB"):
    wait = WebDriverWait(driver, 15)
    try:
        xpath = f"""
        //li[contains(@class, 'list-item') and 
             .//h5[starts-with(text(), '{spot_prefix}')] and 
             count(.//h6[text()='Available']) = 2]
        """
        spot_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", spot_element)
        spot_element.click()
        print(f"Successfully clicked on available {spot_prefix} spot.")
    except Exception as e:
        raise Exception(
            f"Couldn't find or click a fully available '{spot_prefix}' parking spot",
            e,
        )
