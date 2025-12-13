<?php
/**
 * Unit тести для класу IPZE_Poll_Ajax
 */

use PHPUnit\Framework\TestCase;

class PollAjaxTest extends TestCase
{
    private $ajax;
    private $test_poll_id = 456;
    
    protected function setUp(): void
    {
        global $mock_post_meta;
        $mock_post_meta = [];
        
        // Mock функція wp_send_json_success
        if (!function_exists('wp_send_json_success')) {
            function wp_send_json_success($data) {
                global $wp_json_response;
                $wp_json_response = ['success' => true, 'data' => $data];
            }
        }
        
        // Mock функція wp_send_json_error
        if (!function_exists('wp_send_json_error')) {
            function wp_send_json_error($data) {
                global $wp_json_response;
                $wp_json_response = ['success' => false, 'data' => $data];
            }
        }
        
        $this->ajax = new IPZE_Poll_Ajax();
    }
    
    /**
     * Тест 5: Збереження відповідей на опитування
     */
    public function testSavePollResponses()
    {
        // Симулюємо POST дані
        $_POST['poll_id'] = $this->test_poll_id;
        $_POST['question_0'] = 'Варіант A';
        $_POST['question_1'] = ['Варіант 1', 'Варіант 2'];
        $_POST['question_2'] = 'Текстова відповідь користувача';
        
        // Викликаємо метод
        $this->ajax->submit_poll();
        
        // Отримуємо збережені результати
        $results = get_post_meta($this->test_poll_id, '_ipze_poll_results', true);
        
        // Перевірки
        $this->assertIsArray($results, 'Результати мають бути масивом');
        $this->assertCount(1, $results, 'Має бути 1 відповідь');
        
        $response = $results[0];
        $this->assertArrayHasKey('question_0', $response, 'Має бути відповідь на питання 0');
        $this->assertArrayHasKey('question_1', $response, 'Має бути відповідь на питання 1');
        $this->assertArrayHasKey('question_2', $response, 'Має бути відповідь на питання 2');
        
        // Перевірка типів
        $this->assertIsString($response['question_0'], 'Single відповідь - рядок');
        $this->assertIsArray($response['question_1'], 'Multiple відповідь - масив');
        $this->assertCount(2, $response['question_1'], 'Multiple має 2 варіанти');
        
        echo "✓ Тест збереження відповідей пройдено\n";
    }
    
    /**
     * Тест 6: Перевірка санітизації відповідей
     */
    public function testSanitizeResponses()
    {
        $_POST['poll_id'] = $this->test_poll_id;
        $_POST['question_0'] = '<script>alert("hack")</script>Відповідь';
        $_POST['question_1'] = ['<b>Bold</b>', 'Normal'];
        
        $this->ajax->submit_poll();
        $results = get_post_meta($this->test_poll_id, '_ipze_poll_results', true);
        
        $response = $results[0];
        
        // Перевірка що HTML очищено
        $this->assertStringNotContainsString('<script>', $response['question_0'], 
            'Script теги мають бути видалені');
        $this->assertStringNotContainsString('<b>', $response['question_1'][0], 
            'HTML теги мають бути видалені');
        
        echo "✓ Тест санітизації відповідей пройдено\n";
    }
    
    /**
     * Тест 7: Множинні відповіді від різних користувачів
     */
    public function testMultipleUserResponses()
    {
        // Перша відповідь
        $_POST['poll_id'] = $this->test_poll_id;
        $_POST['question_0'] = 'Варіант A';
        $this->ajax->submit_poll();
        
        // Друга відповідь
        $_POST['question_0'] = 'Варіант B';
        $this->ajax->submit_poll();
        
        // Третя відповідь
        $_POST['question_0'] = 'Варіант A';
        $this->ajax->submit_poll();
        
        $results = get_post_meta($this->test_poll_id, '_ipze_poll_results', true);
        
        // Перевірки
        $this->assertCount(3, $results, 'Має бути 3 відповіді');
        $this->assertEquals('Варіант A', $results[0]['question_0']);
        $this->assertEquals('Варіант B', $results[1]['question_0']);
        $this->assertEquals('Варіант A', $results[2]['question_0']);
        
        echo "✓ Тест множинних відповідей пройдено\n";
    }
}