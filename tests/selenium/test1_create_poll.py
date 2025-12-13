from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_create_poll():
    """Тест 1: Створення опитування в адмінці WordPress"""
    
    # Ініціалізація драйвера Chrome
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    
    try:
        print("🧪 Тест 1: Створення опитування")
        print("-" * 50)
        
        # 1. Відкрити сторінку логіну
        driver.get("http://studrada.local/wp-admin")
        print("✓ Відкрито сторінку логіну")
        
        # 2. ЛОКАТОР #1: Знайти поле логіну за ID
        username_field = driver.find_element(By.ID, "user_login")
        username_field.send_keys("Anfisa")
        print("✓ Введено логін")
        
        # 3. ЛОКАТОР #2: Знайти поле пароля за NAME
        password_field = driver.find_element(By.NAME, "pwd")
        password_field.send_keys("246357")  # ЗМІНИ!
        print("✓ Введено пароль")
        
        # 4. ЛОКАТОР #3: Знайти кнопку входу за CSS SELECTOR
        login_button = driver.find_element(By.CSS_SELECTOR, "#wp-submit")
        login_button.click()
        print("✓ Натиснуто кнопку входу")
        
        # 5. EXPLICIT WAIT: Очікування завантаження дашборду
        WebDriverWait(driver, 10).until(
            EC.url_contains("wp-admin")
        )
        print("✓ Успішний вхід в адмінку")
        
        # 6. ASSERT #1: Перевірка URL
        current_url = driver.current_url
        assert "wp-admin" in current_url, "URL має містити 'wp-admin'"
        print("✓ ASSERT: URL містить 'wp-admin'")
        
        # 7. Перехід до створення опитування
        driver.get("http://studrada.local/wp-admin/post-new.php?post_type=ipze_poll")
        
        # 8. EXPLICIT WAIT: Очікування завантаження редактора
        title_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "title"))
        )
        
        # 9. Введення назви опитування
        poll_title = f"Автотест: Опитування {int(time.time())}"
        title_field.send_keys(poll_title)
        print(f"✓ Введено назву: {poll_title}")
        
        # 10. ЛОКАТОР #4: XPath (ОБОВ'ЯЗКОВО!) - кнопка додавання питання
        add_question_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@id='ipze-add-question']"))
        )
        add_question_btn.click()
        print("✓ Натиснуто 'Додати питання'")
        
        # 11. IMPLICIT WAIT: Чекаємо появу форми
        time.sleep(1)
        
        # 12. ЛОКАТОР #5: XPath для поля питання
        question_input = driver.find_element(
            By.XPATH, 
            "//input[@name='ipze_questions[0][question]']"
        )
        
        # 13. ASSERT #2: Перевірка видимості елемента
        assert question_input.is_displayed(), "Поле питання має бути видимим"
        print("✓ ASSERT: Поле питання відображається")
        
        # 14. Ввести текст питання
        question_input.send_keys("Ваш улюблений колір?")
        print("✓ Введено текст питання")
        
        # 15. ЛОКАТОР #6: XPath з contains - кнопка публікації
        try:
            # Спроба 1: Кнопка "Опублікувати"
            publish_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Опублікувати')]")
                )
            )
        except:
            try:
                # Спроба 2: Кнопка "Publish" (англійською)
                publish_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[@id='publish']")
                    )
                )
            except:
                try:
                    # Спроба 3: Input type submit
                    publish_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "input#publish")
                        )
                    )
                except:
                    # Спроба 4: Будь-яка кнопка з publish
                    publish_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//*[contains(@id, 'publish')]")
                        )
                    )

        print("✓ Знайдено кнопку публікації")
        # 16. ASSERT #3: Перевірка що кнопка активна
        assert publish_button.is_enabled(), "Кнопка 'Опублікувати' має бути активною"
        print("✓ ASSERT: Кнопка 'Опублікувати' активна")
        
        publish_button.click()
        print("✓ Натиснуто 'Опублікувати'")
        
        # 17. EXPLICIT WAIT: Очікування збереження
        WebDriverWait(driver, 10).until(
            EC.url_contains("post=")
        )
        
        # 18. ASSERT #4: Перевірка що URL містить ID поста
        final_url = driver.current_url
        assert "post=" in final_url, "URL має містити ID опитування"
        print("✓ ASSERT: Опитування успішно створено (є ID в URL)")
        
        # 19. ASSERT #5: Перевірка заголовка сторінки
        page_title = driver.title
        assert "Редагувати" in page_title, "Заголовок має містити 'Редагувати'"
        print(f"✓ ASSERT: Заголовок сторінки: '{page_title}'")
        
        print("\n" + "="*50)
        print("✅ ТЕСТ 1 PASSED: Опитування успішно створено!")
        print("="*50 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        driver.save_screenshot("test1_assertion_error.png")
        raise
        
    except Exception as e:
        print(f"\n❌ ТЕСТ 1 FAILED: {e}")
        driver.save_screenshot("test1_error.png")
        raise
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_create_poll()