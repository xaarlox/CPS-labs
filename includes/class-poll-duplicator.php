<?php
if ( ! defined( 'ABSPATH' ) ) exit;

class IPZE_Poll_Duplicator {

    public function __construct() {
        // Додаємо лінку дублювання у список постів
        add_filter('post_row_actions', [$this, 'add_duplicate_action'], 10, 2);
        
        // Обробляємо дублювання
        add_action('admin_init', [$this, 'handle_duplicate']);
    }

    /**
     * Додає лінку "Дублювати" до рядка опитування в списку
     */
    public function add_duplicate_action($actions, $post) {
        if ($post->post_type !== 'ipze_poll') {
            return $actions;
        }

        // Перевіряємо права доступу
        if (!current_user_can('edit_post', $post->ID)) {
            return $actions;
        }

        // Створюємо URL для дублювання
        $duplicate_url = add_query_arg([
            'action' => 'duplicate_ipze_poll',
            'post_id' => $post->ID,
            'nonce' => wp_create_nonce('duplicate_ipze_poll_' . $post->ID)
        ], admin_url('admin.php'));

        $actions['duplicate'] = '<a href="' . esc_url($duplicate_url) . '">Дублювати</a>';

        return $actions;
    }

    /**
     * Обробляє дублювання опитування
     */
    public function handle_duplicate() {
        if (!isset($_GET['action']) || $_GET['action'] !== 'duplicate_ipze_poll') {
            return;
        }

        if (!isset($_GET['post_id']) || !isset($_GET['nonce'])) {
            return;
        }

        $post_id = intval($_GET['post_id']);
        $nonce = sanitize_text_field($_GET['nonce']);

        // Перевіряємо nonce
        if (!wp_verify_nonce($nonce, 'duplicate_ipze_poll_' . $post_id)) {
            wp_die('Помилка безпеки: невалідний nonce');
        }

        // Перевіряємо права доступу
        if (!current_user_can('edit_posts')) {
            wp_die('Помилка прав доступу');
        }

        // Отримуємо оригінальний пост
        $original_post = get_post($post_id);
        if (!$original_post || $original_post->post_type !== 'ipze_poll') {
            wp_die('Опитування не знайдено');
        }

        // Створюємо новий пост
        $new_post = [
            'post_type'    => $original_post->post_type,
            'post_title'   => $original_post->post_title . ' (копія)',
            'post_content' => $original_post->post_content,
            'post_status'  => 'draft',
            'post_author'  => $original_post->post_author,
        ];

        $new_post_id = wp_insert_post($new_post);

        if (is_wp_error($new_post_id)) {
            wp_die('Помилка при створенні копії: ' . $new_post_id->get_error_message());
        }

        // Копіюємо всі meta-поля
        $meta_keys = [
            '_ipze_questions',
        ];

        foreach ($meta_keys as $meta_key) {
            $meta_value = get_post_meta($post_id, $meta_key, true);
            if (!empty($meta_value)) {
                update_post_meta($new_post_id, $meta_key, $meta_value);
            }
        }

        // Також копіюємо всі інші meta-поля, крім внутрішніх
        $all_meta = get_post_meta($post_id);
        foreach ($all_meta as $meta_key => $meta_values) {
            // Пропускаємо внутрішні, результати та вже скопійовані
            if (strpos($meta_key, '_') === 0 || $meta_key === '_ipze_poll_results') {
                continue;
            }

            if (!in_array($meta_key, $meta_keys)) {
                foreach ($meta_values as $meta_value) {
                    add_post_meta($new_post_id, $meta_key, maybe_unserialize($meta_value), true);
                }
            }
        }

        // Перенаправляємо на редагування нового опитування
        $edit_url = add_query_arg('post', $new_post_id, admin_url('post.php'));
        $edit_url = add_query_arg('action', 'edit', $edit_url);
        
        wp_redirect($edit_url);
        exit;
    }
}
