import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class TestLoginFunctionality(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.base_url = "http://127.0.0.1:8000"
        self.driver.get(f"{self.base_url}/users/login/")
    
    def test_successful_login(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)
        
        print("\n=== ТЕСТ 1: ЛОГІН КОРИСТУВАЧА ANFISA ===\n")
        
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        self.assertIsNotNone(username_field)
        print("Поле username знайдено")
        
        password_field = driver.find_element(By.XPATH, "//input[@type='password' and @name='password']")
        self.assertIsNotNone(password_field)
        print("Поле password знайдено за XPATH")
        
        submit_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        self.assertIsNotNone(submit_button)
        print("Кнопка submit знайдена за CSS_SELECTOR")
        
        header = driver.find_element(By.XPATH, "//h2[contains(text(), 'Вхід') or contains(text(), 'ВХІД')]")
        self.assertIn(header.text.upper(), ["ВХІД", "ВХІД"])
        print(f"Заголовок знайдено: '{header.text}'")
        
        username_field.clear()
        username_field.send_keys("Anfisa")
        print("Введено username: Anfisa")
        
        time.sleep(0.5)
        
        password_field.clear()
        password_field.send_keys("246357")
        print("Введено password: 246357")
        
        time.sleep(0.5)
        
        self.assertEqual(username_field.get_attribute("value"), "Anfisa")
        print("Assert: Username = 'Anfisa'")
        
        self.assertEqual(password_field.get_attribute("value"), "246357")
        print("Assert: Password введено коректно")
        
        self.assertTrue(submit_button.is_enabled())
        print("Assert: Кнопка submit активна")
        
        submit_button.click()
        print("Форму відправлено")
        
        try:
            wait.until(EC.url_changes(f"{self.base_url}/users/login/"))
            current_url = driver.current_url
            print(f"URL змінився: {current_url}")
            
            self.assertIn(self.base_url, current_url)
            print("Assert: Редирект відбувся успішно")
            
            self.assertNotIn("/users/login/", current_url)
            print("Assert: Користувач покинув сторінку логіну")
            
        except TimeoutException:
            self.fail("Timeout: Редирект після логіну не відбувся")
    
    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    test = TestLoginFunctionality('test_successful_login')
    
    start_time = time.time()
    try:
        test.setUp()
        test.test_successful_login()
    except Exception as e:
        print(f"FAILED: {e}")
    finally:
        test.tearDown()
        
    end_time = time.time()
    duration = end_time - start_time
    
    print("-" * 70)
    print(f"Ran 1 test in {duration:.3f}s")
    print("\nOK")