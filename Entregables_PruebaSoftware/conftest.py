"""Configuración común. Ajustar BASE_URL, API_URL y los selectores data-testid a la app real."""
import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = os.getenv("GTD_BASE_URL", "https://staging.gtd-app.example.com")
API_URL = os.getenv("GTD_API_URL", "https://staging.gtd-app.example.com/api")
USER = os.getenv("GTD_USER", "qa_user")
PASSWORD = os.getenv("GTD_PASS", "change_me")


@pytest.fixture
def driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1366,900")
    d = webdriver.Chrome(options=opts)
    d.implicitly_wait(0)  # solo esperas explícitas, para evitar pruebas inestables (flaky)
    yield d
    d.quit()


@pytest.fixture
def logged_driver(driver):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    driver.get(f"{BASE_URL}/login")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='login-user']"))).send_keys(USER)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-pass']").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "[data-testid='login-submit']").click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='capture-input']")))
    return driver
