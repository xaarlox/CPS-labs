<?php
if (!defined('ABSPATH')) exit;

class IPZE_Poll_Ajax {

    public function __construct() {
        add_action('wp_ajax_ipze_submit_poll', [$this, 'submit_poll']);
        add_action('wp_ajax_nopriv_ipze_submit_poll', [$this, 'submit_poll']);
    }

    public function submit_poll() {
        $poll_id = isset($_POST['poll_id']) ? intval($_POST['poll_id']) : 0;
        
        if (!$poll_id) {
            wp_send_json_error(['message' => 'ID опитування не знайдено']);
        }

        // Збираємо відповіді
        $user_answers = [];
        foreach ($_POST as $key => $val) {
            if (strpos($key, 'question_') === 0) {
                // Для checkbox масиви приходять як question_0, question_1 тощо
                // Перевіряємо чи це масив (множинний вибір)
                if (is_array($val)) {
                    $user_answers[$key] = array_map('sanitize_text_field', $val);
                } else {
                    $user_answers[$key] = sanitize_text_field($val);
                }
            }
        }

        if (empty($user_answers)) {
            wp_send_json_error(['message' => 'Немає відповідей']);
        }

        // Отримуємо існуючі результати
        $results = get_post_meta($poll_id, '_ipze_poll_results', true);
        if (!is_array($results)) {
            $results = [];
        }

        // Додаємо нові відповіді
        $results[] = $user_answers;
        
        // Зберігаємо
        $updated = update_post_meta($poll_id, '_ipze_poll_results', $results);

        if ($updated !== false) {
            wp_send_json_success([
                'message' => 'Відповіді збережено',
                'total_responses' => count($results)
            ]);
        } else {
            wp_send_json_error(['message' => 'Помилка при збереженні']);
        }
    }
}