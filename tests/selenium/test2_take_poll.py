from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_take_poll():
    """Тест 2: Проходження опитування на фронтенді"""
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    
    try:
        print("🧪 Тест 2: Проходження опитування")
        print("-" * 50)
        
        # 1. Відкрити сторінку з опитуванням
        driver.get("http://studrada.local/usefultips/")  # ЗМІНИ URL!
        print("✓ Відкрито сторінку опитування")
        
        # 2. EXPLICIT WAIT: Очікування титульної сторінки
        welcome_screen = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".ipze-welcome-screen"))
        )
        
        # 3. ASSERT #1: Титульна сторінка відображається
        assert welcome_screen.is_displayed(), "Титульна сторінка має бути видима"
        print("✓ ASSERT: Титульна сторінка відображається")
        
        # 4. ЛОКАТОР #1: Заголовок опитування за CLASS NAME
        poll_title = driver.find_element(By.CLASS_NAME, "ipze-poll-title")
        title_text = poll_title.text
        
        # 5. ASSERT #2: Заголовок не порожній
        assert len(title_text) > 0, "Заголовок опитування не може бути порожнім"
        print(f"✓ ASSERT: Заголовок опитування: '{title_text}'")
        
        # 6. ЛОКАТОР #2: Кнопка "Почати" за CSS SELECTOR
        start_button = driver.find_element(By.CSS_SELECTOR, ".ipze-start-btn")
        
        # 7. ASSERT #3: Кнопка видима та активна
        assert start_button.is_displayed() and start_button.is_enabled(), \
            "Кнопка 'Почати' має бути видимою та активною"
        print("✓ ASSERT: Кнопка 'Почати' доступна")
        
        start_button.click()
        print("✓ Натиснуто 'Почати'")
        
        # 8. EXPLICIT WAIT: Очікування появи першого питання
        first_question = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".ipze-question-screen[data-question='0']")
            )
        )
        print("✓ Перше питання відображається")
        
        # 9. ЛОКАТОР #3: XPath для прогрес-бару (ОБОВ'ЯЗКОВО!)
        progress_text = driver.find_element(
            By.XPATH, 
            "//div[@class='ipze-progress-text']"
        )
        progress_value = progress_text.text
        
        # 10. ASSERT #4: Прогрес-бар показує питання 1
        assert "Питання 1" in progress_value, "Прогрес-бар має показувати 'Питання 1'"
        print(f"✓ ASSERT: Прогрес-бар: '{progress_value}'")
        
        # 11. ЛОКАТОР #4: XPath для першого варіанта відповіді
        first_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//label[@class='ipze-option'][1]")
            )
        )
        first_option.click()
        print("✓ Обрано перший варіант")
        
        # 12. IMPLICIT WAIT: Чекаємо на оновлення UI
        time.sleep(0.5)
        
        # 13. ЛОКАТОР #5: Перевірка вибраного radio button за CSS
        checked_radio = driver.find_element(
            By.CSS_SELECTOR, 
            "input[type='radio']:checked"
        )
        
        # 14. ASSERT #5: Radio button вибраний
        assert checked_radio.is_selected(), "Варіант відповіді має бути вибраний"
        print("✓ ASSERT: Варіант відповіді вибрано")
        
        # 15. ЛОКАТОР #6: XPath для кнопки "Завершити"
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'ipze-submit-btn')]")
            )
        )
        
        # 16. ASSERT #6: Кнопка "Завершити" видима
        assert submit_button.is_displayed(), "Кнопка 'Завершити' має бути видима"
        print("✓ ASSERT: Кнопка 'Завершити' відображається")
        
        submit_button.click()
        print("✓ Натиснуто 'Завершити'")
        
        # 17. EXPLICIT WAIT: Очікування повідомлення про успіх
        success_screen = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".ipze-success-screen"))
        )
        
        # 18. ASSERT #7: Повідомлення "Дякуємо" відображається
        success_text = success_screen.text
        assert "Дякуємо" in success_text, "Має бути повідомлення 'Дякуємо'"
        print(f"✓ ASSERT: Показано повідомлення: '{success_text}'")
        
        # 19. ЛОКАТОР #7: Іконка успіху за CLASS NAME
        success_icon = driver.find_element(By.CLASS_NAME, "ipze-success-icon")
        icon_text = success_icon.text
        
        # 20. ASSERT #8: Іконка - галочка
        assert icon_text == "✓", "Іконка успіху має бути галочкою"
        print("✓ ASSERT: Іконка успіху відображається")
        
        print("\n" + "="*50)
        print("✅ ТЕСТ 2 PASSED: Опитування успішно пройдено!")
        print("="*50 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        driver.save_screenshot("test2_assertion_error.png")
        raise
        
    except Exception as e:
        print(f"\n❌ ТЕСТ 2 FAILED: {e}")
        driver.save_screenshot("test2_error.png")
        raise
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_take_poll()