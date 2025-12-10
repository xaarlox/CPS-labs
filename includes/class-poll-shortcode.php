<?php
if (!defined('ABSPATH')) exit;

class IPZE_Poll_Shortcode {

    public function __construct() {
        add_shortcode('ipze_poll', [$this, 'render_poll']);
    }

    public function render_poll($atts) {
        $atts = shortcode_atts(['id' => null], $atts);
        $poll_id = intval($atts['id']);

        // Якщо ID не вказано, беремо поточний пост
        if (!$poll_id) {
            global $post;
            if ($post && $post->post_type === 'ipze_poll') {
                $poll_id = $post->ID;
            }
        }

        if (!$poll_id) {
            return '<div class="ipze-error-message">Опитування не знайдено. Будь ласка, вкажіть ID опитування.</div>';
        }

        $post = get_post($poll_id);

        if (!$post || $post->post_type !== 'ipze_poll') {
            return '<div class="ipze-error-message">Опитування не знайдено. Перевірте правильність ID.</div>';
        }

        if ($post->post_status !== 'publish') {
            return '<div class="ipze-error-message">Це опитування ще не опубліковано.</div>';
        }

        // Виправлено: використовуємо правильний ключ мета-поля
        $questions = get_post_meta($poll_id, '_ipze_questions', true);
        
        if (!$questions || !is_array($questions) || empty($questions)) {
            return '<div class="ipze-error-message">У цьому опитуванні ще немає питань. Додайте питання в адмінці.</div>';
        }

        // Підключаємо шаблон
        ob_start();
        include plugin_dir_path(__FILE__) . '../templates/poll-form.php';
        return ob_get_clean();
    }
}