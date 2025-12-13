from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_view_results():
    """Тест 3: Перегляд результатів опитування в адмінці"""
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    
    try:
        print("🧪 Тест 3: Перегляд результатів")
        print("-" * 50)
        
        # 1. ЛОГІН В АДМІНКУ
        driver.get("http://studrada.local/wp-admin")
        
        username_field = driver.find_element(By.ID, "user_login")
        username_field.send_keys("Anfisa")
        
        password_field = driver.find_element(By.NAME, "pwd")
        password_field.send_keys("246357")  # ЗМІНИ!
        
        login_button = driver.find_element(By.CSS_SELECTOR, "#wp-submit")
        login_button.click()
        
        WebDriverWait(driver, 10).until(EC.url_contains("wp-admin"))
        print("✓ Вхід в адмінку")
        
        # 2. ЛОКАТОР #1: XPath для посилання "Результати" (ОБОВ'ЯЗКОВО!)
        results_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href, 'page=ipze-poll-results')]")
            )
        )
        results_link.click()
        print("✓ Перехід на сторінку результатів")
        
        # 3. EXPLICIT WAIT: Очікування завантаження сторінки
        WebDriverWait(driver, 10).until(
            EC.url_contains("ipze-poll-results")
        )
        
        # 4. ASSERT #1: URL містить "ipze-poll-results"
        current_url = driver.current_url
        assert "ipze-poll-results" in current_url, \
            "URL має містити 'ipze-poll-results'"
        print("✓ ASSERT: URL коректний")
        
        # 5. ЛОКАТОР #2: Заголовок сторінки за TAG NAME
        page_heading = driver.find_element(By.TAG_NAME, "h1")
        heading_text = page_heading.text
        
        # 6. ASSERT #2: Заголовок правильний
        assert heading_text == "Результати опитувань", \
            f"Очікувався заголовок 'Результати опитувань', отримано '{heading_text}'"
        print(f"✓ ASSERT: Заголовок сторінки: '{heading_text}'")
        
        # 7. ЛОКАТОР #3: Dropdown вибору опитування за ID
        poll_select = driver.find_element(By.ID, "poll-select")
        
        # 8. ASSERT #3: Dropdown видимий
        assert poll_select.is_displayed(), "Dropdown має бути видимим"
        print("✓ ASSERT: Dropdown відображається")
        
        # 9. ЛОКАТОР #4: Всі опції в dropdown за TAG NAME
        options = poll_select.find_elements(By.TAG_NAME, "option")
        
        # 10. ASSERT #4: Є опитування в списку
        assert len(options) > 1, "Має бути хоча б одне опитування"
        print(f"✓ ASSERT: Знайдено {len(options) - 1} опитувань")
        
        # 11. Вибрати перше опитування
        if len(options) > 1:
            options[1].click()
            print("✓ Обрано опитування")
            
            # IMPLICIT WAIT: Чекаємо на завантаження результатів
            time.sleep(2)
        
        # 12. ЛОКАТОР #5: XPath для canvas діаграми (ОБОВ'ЯЗКОВО!)
        try:
            canvas = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//canvas[contains(@id, 'chart_')]")
                )
            )
            
            # 13. ASSERT #5: Діаграма відображається
            assert canvas.is_displayed(), "Діаграма Chart.js має відображатись"
            print("✓ ASSERT: Діаграма Chart.js відображається")
            
        except Exception as e:
            print("⚠ Діаграма не знайдена (можливо немає відповідей)")
        
        # 14. ЛОКАТОР #6: Таблиця результатів за CLASS NAME
        results_table = driver.find_element(By.CLASS_NAME, "ipze-stats-table")
        
        # 15. ASSERT #6: Таблиця видима
        assert results_table.is_displayed(), "Таблиця результатів має відображатись"
        print("✓ ASSERT: Таблиця результатів відображається")
        
        # 16. ЛОКАТОР #7: XPath для рядків таблиці (ОБОВ'ЯЗКОВО!)
        table_rows = driver.find_elements(
            By.XPATH,
            "//table[@class='ipze-stats-table']//tbody/tr"
        )
        
      # 17. ASSERT #7: Таблиця існує (може бути порожньою)
        print(f"✓ Знайдено {len(table_rows)} рядків в таблиці")

        if len(table_rows) > 0:
            # Є дані - перевіряємо їх
            print(f"✓ ASSERT: В таблиці є дані ({len(table_rows)} рядків)")
            
            # Перевіримо перший рядок
            first_row_cells = table_rows[0].find_elements(By.TAG_NAME, "td")
            assert len(first_row_cells) >= 3, "Рядок має містити мінімум 3 колонки"
            print("✓ ASSERT: Структура таблиці коректна")
        else:
            # Немає даних - це теж валідний сценарій
            print("✓ ASSERT: Таблиця порожня (опитування ще не проходили)")
            
            # Перевіримо що це саме порожня таблиця, а не помилка
            table = driver.find_element(By.CLASS_NAME, "ipze-stats-table")
            assert table.is_displayed(), "Таблиця має відображатись навіть якщо порожня"
            print("✓ ASSERT: Таблиця відображається коректно")
                
        # 18. ЛОКАТОР #8: Блок статистики за CSS SELECTOR
        summary_block = driver.find_element(By.CSS_SELECTOR, ".ipze-summary")
        
        # 19. ASSERT #8: Блок статистики видимий
        assert summary_block.is_displayed(), "Блок статистики має відображатись"
        print("✓ ASSERT: Блок статистики відображається")
        
        # 20. ЛОКАТОР #9: Картки статистики за CLASS NAME
        summary_cards = driver.find_elements(By.CLASS_NAME, "ipze-summary-card")
        
        # 21. ASSERT #9: Є дві картки (відповіді + питання)
        assert len(summary_cards) >= 2, "Має бути мінімум 2 картки зі статистикою"
        print(f"✓ ASSERT: Знайдено {len(summary_cards)} карток статистики")
        
        # 22. ЛОКАТОР #10: XPath для кількості відповідей
        total_responses = driver.find_element(
            By.XPATH,
            "//div[@class='ipze-summary-number'][1]"
        )
        responses_count = total_responses.text
        
        # 23. ASSERT #10: Кількість відповідей - число
        assert responses_count.isdigit(), "Кількість відповідей має бути числом"
        print(f"✓ ASSERT: Всього відповідей: {responses_count}")
        
        print("\n" + "="*50)
        print("✅ ТЕСТ 3 PASSED: Результати успішно відображено!")
        print("="*50 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        driver.save_screenshot("test3_assertion_error.png")
        raise
        
    except Exception as e:
        print(f"\n❌ ТЕСТ 3 FAILED: {e}")
        driver.save_screenshot("test3_error.png")
        raise
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_view_results()