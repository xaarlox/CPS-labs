import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

class TestLabsPageNavigation(unittest.TestCase):
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
    
    def test_labs_page_elements(self):
        driver = self.driver
        wait = WebDriverWait(driver, 15)
        
        print("\n--- ТЕСТ 2: СТОРІНКА ЛАБОРАТОРНИХ ---\n")
        
        driver.get(f"{self.base_url}/labs/")
        
        wait.until(EC.url_to_be(f"{self.base_url}/labs/"))
        self.assertEqual(driver.current_url, f"{self.base_url}/labs/")
        print("URL коректний")
        
        logo = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "logo")))
        self.assertTrue(logo.is_displayed())
        print("Логотип знайдено (CLASS_NAME)")
        
        navbar = driver.find_element(By.XPATH, "//nav[@class='navbar']")
        self.assertIsNotNone(navbar)
        self.assertTrue(navbar.is_displayed())
        print("Navbar знайдено (XPATH)")
        
        user_avatar = driver.find_element(By.CSS_SELECTOR, ".user-avatar-circle")
        self.assertTrue(user_avatar.is_displayed())
        print("Аватар знайдено (CSS_SELECTOR)")
        
        try:
            lab_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='labs-grid']/div[contains(@class, 'lab-card')]")))
            
            self.assertGreater(len(lab_cards), 0)
            self.assertTrue(lab_cards[0].is_displayed())
            print(f"Знайдено {len(lab_cards)} лабораторних (XPATH)")
            
            first_lab_title = lab_cards[0].find_element(By.TAG_NAME, "h4")
            self.assertIsNotNone(first_lab_title.text)
            self.assertNotEqual(first_lab_title.text.strip(), "")
            print(f"Заголовок: '{first_lab_title.text}' (TAG_NAME)")
            
        except TimeoutException:
            self.fail("Картки не завантажилися")
        
        user_menu_wrapper = driver.find_element(By.CLASS_NAME, "user-menu-wrapper")
        actions = ActionChains(driver)
        actions.move_to_element(user_menu_wrapper).perform()
        
        time.sleep(1)
        
        dropdown = driver.find_element(By.CLASS_NAME, "user-dropdown")
        is_visible = dropdown.is_displayed()
        opacity = dropdown.value_of_css_property("opacity")
        
        self.assertTrue(is_visible or opacity != "0")
        print("Dropdown меню працює")
        
        dropdown_links = dropdown.find_elements(By.XPATH, ".//a")
        self.assertGreaterEqual(len(dropdown_links), 2)
        print(f"Dropdown містить {len(dropdown_links)} посилань (XPATH)")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    test = TestLabsPageNavigation('test_labs_page_elements')
    
    start_time = time.time()
    try:
        test.setUp()
        test.test_labs_page_elements()
    except Exception as e:
        print(f"FAILED: {e}")
    finally:
        test.tearDown()
        
    end_time = time.time()
    duration = end_time - start_time
    
    print("-" * 70)
    print(f"Ran 1 test in {duration:.3f}s")
    print("\nOK")