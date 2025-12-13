<?php
/**
 * Unit тести для класу IPZE_Poll_Shortcode
 */

use PHPUnit\Framework\TestCase;

class PollShortcodeTest extends TestCase
{
    private $shortcode;
    private $test_post_id = 789;
    
    protected function setUp(): void
    {
        global $mock_post_meta;
        $mock_post_meta = [];
        
        // Створюємо тестові питання
        $questions = [
            [
                'question' => 'Ваш улюблений колір?',
                'type' => 'single',
                'options' => ['Червоний', 'Синій', 'Зелений']
            ]
        ];
        update_post_meta($this->test_post_id, '_ipze_questions', $questions);
        
        $this->shortcode = new IPZE_Poll_Shortcode();
    }
    
    /**
     * Тест 8: Перевірка відсутності опитування (спрощена версія)
     */
    public function testMissingPoll()
    {
        $output = $this->shortcode->render_poll(['id' => 99999]);
        
        // Перевіряємо що є повідомлення про помилку
        $this->assertStringContainsString('ipze-error-message', $output, 
            'Має бути клас помилки');
        $this->assertIsString($output, 'Вивід має бути рядком');
        
        echo "✓ Тест відсутнього опитування пройдено\n";
    }
    
    /**
     * Тест 9: Перевірка опитування без питань
     */
    public function testPollWithoutQuestions()
    {
        update_post_meta($this->test_post_id, '_ipze_questions', []);
        
        $output = $this->shortcode->render_poll(['id' => $this->test_post_id]);
        
        $this->assertStringContainsString('немає питань', $output, 
            'Має бути повідомлення про відсутність питань');
        
        echo "✓ Тест опитування без питань пройдено\n";
    }
}