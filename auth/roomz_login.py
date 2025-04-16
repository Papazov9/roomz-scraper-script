from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def login_to_roomz(email, password, headless=False):
    chrome_options = Options()

    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    if headless:
        chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://my.roomz.io")
        wait = WebDriverWait(driver, 15)

        roomz_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(@class, 'toggle-form') and contains(., 'Roomz')]",
                )
            )
        )
        roomz_button.click()

        email_input = wait.until(EC.visibility_of_element_located((By.ID, "Email")))
        password_input = wait.until(
            EC.visibility_of_element_located((By.ID, "Password"))
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", email_input)
        email_input.send_keys(email)
        driver.execute_script("arguments[0].scrollIntoView(true);", password_input)
        password_input.send_keys(password)

        login_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[@type='submit' and contains(., 'Sign In')]")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
        login_button.click()

        wait.until(EC.presence_of_element_located((By.ID, "root")))

        print("✅ Logged in — ")

        return driver

    except Exception as e:
        print("Login error:", e)
        print("Current URL after failure:", driver.current_url)
        print("Page content snippet:", driver.page_source[:2000])
        driver.quit()
        raise e
