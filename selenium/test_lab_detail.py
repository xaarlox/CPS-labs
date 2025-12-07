import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestLabDetailPage(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.base_url = "http://127.0.0.1:8000"
        
        self.driver.get(f"{self.base_url}/users/login/")
        wait = WebDriverWait(self.driver, 10)
        
        username = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password = self.driver.find_element(By.NAME, "password")
        
        username.send_keys("Anfisa")
        password.send_keys("246357")
        password.send_keys(Keys.RETURN)
        time.sleep(2)
    
    def test_lab_detail_page_interaction(self):
        driver = self.driver
        wait = WebDriverWait(driver, 15)
        
        print("\n--- ТЕСТ 3: ДЕТАЛІ ЛАБОРАТОРНОЇ ---\n")
        
        driver.get(f"{self.base_url}/labs/")
        
        lab_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'lab-card')]")))
        self.assertGreater(len(lab_cards), 0)
        print(f"Знайдено {len(lab_cards)} карток (XPATH)")
        
        first_card = lab_cards[0]
        action_button = first_card.find_element(By.XPATH, ".//a[contains(@class, 'btn-lab-action') and contains(@class, 'btn-action')]")
        
        self.assertTrue(action_button.is_displayed())
        self.assertTrue(action_button.is_enabled())
        
        button_text = action_button.text
        print(f"Кнопка '{button_text}' знайдена (XPATH)")
        
        action_button.click()
        
        wait.until(EC.url_contains("/lab/"))
        current_url = driver.current_url
        self.assertIn("/lab/", current_url)
        print(f"Перехід на деталі: {current_url}")
        
        h1_title = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        self.assertNotEqual(h1_title.text.strip(), "")
        print(f"Заголовок: '{h1_title.text}' (TAG_NAME)")
        
        meta_cards = driver.find_elements(By.CLASS_NAME, "meta-card")
        self.assertGreaterEqual(len(meta_cards), 3)
        print(f"Знайдено {len(meta_cards)} мета-карток (CLASS_NAME)")
        
        simulation_button = driver.find_element(By.XPATH, "//a[contains(@class, 'btn-primary')]")
        self.assertTrue(simulation_button.is_displayed())
        print("Кнопка 'Розпочати симуляцію' є (XPATH)")
        
        back_button = driver.find_element(By.CSS_SELECTOR, "a.btn-secondary")
        self.assertTrue(back_button.is_displayed())
        print("Кнопка 'Повернутися' є (CSS_SELECTOR)")
        
        description = driver.find_element(By.CLASS_NAME, "description")
        self.assertIsNotNone(description.text)
        print("Опис лабораторної присутній")
        
        back_button.click()
        wait.until(EC.url_to_be(f"{self.base_url}/labs/"))
        self.assertEqual(driver.current_url, f"{self.base_url}/labs/")
        print("Повернення на /labs/ успішне")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    test = TestLabDetailPage('test_lab_detail_page_interaction')
    
    start_time = time.time()
    try:
        test.setUp()
        test.test_lab_detail_page_interaction()
    except Exception as e:
        print(f"FAILED: {e}")
    finally:
        test.tearDown()
        
    end_time = time.time()
    duration = end_time - start_time
    
    print("-" * 70)
    print(f"Ran 1 test in {duration:.3f}s")
    print("\nOK")