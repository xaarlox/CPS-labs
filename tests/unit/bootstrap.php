<?php
/**
 * PHPUnit Bootstrap для тестування плагіна IPZE Poll
 */

// Визначаємо константу що це тестування
define('IPZE_POLL_TESTING', true);

// Шлях до WordPress test framework
$_tests_dir = getenv('WP_TESTS_DIR');

if (!$_tests_dir) {
    $_tests_dir = rtrim(sys_get_temp_dir(), '/\\') . '/wordpress-tests-lib';
}

// Якщо не встановлений WordPress test framework - використовуємо мок-функції
if (!file_exists($_tests_dir . '/includes/functions.php')) {
    echo "WordPress test framework не знайдено. Використовуємо mock функції.\n";
    
    // Mock WordPress функції для тестування
    if (!function_exists('add_action')) {
        function add_action($hook, $callback) { return true; }
    }
    if (!function_exists('add_filter')) {
        function add_filter($hook, $callback) { return true; }
    }
    if (!function_exists('add_shortcode')) {
        function add_shortcode($tag, $callback) { return true; }
    }
    if (!function_exists('shortcode_atts')) {
        function shortcode_atts($pairs, $atts, $shortcode = '') {
            $result = [];
            foreach ($pairs as $name => $default) {
                if (isset($atts[$name])) {
                    $result[$name] = $atts[$name];
                } else {
                    $result[$name] = $default;
                }
            }
            return $result;
        }
    }
    if (!function_exists('get_post_meta')) {
        function get_post_meta($post_id, $key, $single = false) {
            global $mock_post_meta;
            return isset($mock_post_meta[$post_id][$key]) ? $mock_post_meta[$post_id][$key] : ($single ? '' : []);
        }
    }
    if (!function_exists('update_post_meta')) {
        function update_post_meta($post_id, $key, $value) {
            global $mock_post_meta;
            $mock_post_meta[$post_id][$key] = $value;
            return true;
        }
    }
    if (!function_exists('get_post_type')) {
        function get_post_type($post = null) {
            return 'ipze_poll';
        }
    }
    if (!function_exists('sanitize_text_field')) {
        function sanitize_text_field($str) {
            if ($str === null || $str === '') {
                return '';
            }
            return strip_tags((string)$str);
        }
    }
    if (!function_exists('esc_attr')) {
        function esc_attr($text) {
            return htmlspecialchars($text ?? '', ENT_QUOTES);
        }
    }
    if (!function_exists('esc_html')) {
        function esc_html($text) {
            return htmlspecialchars($text ?? '', ENT_QUOTES);
        }
    }
    if (!function_exists('wp_verify_nonce')) {
        function wp_verify_nonce($nonce, $action) {
            return true;
        }
    }
    if (!function_exists('current_user_can')) {
        function current_user_can($capability) {
            return true;
        }
    }
    if (!function_exists('plugin_dir_path')) {
        function plugin_dir_path($file) {
            return dirname(dirname(dirname($file))) . '/';
        }
    }
    if (!function_exists('get_post')) {
        function get_post($id) {
            $post = new stdClass();
            $post->ID = $id;
            $post->post_type = 'ipze_poll';
            $post->post_status = 'publish';
            $post->post_title = 'Тестове опитування';
            $post->post_content = 'Опис опитування';
            return $post;
        }
    }
    if (!function_exists('wpautop')) {
        function wpautop($text) {
            return '<p>' . $text . '</p>';
        }
    }
    if (!defined('ABSPATH')) {
        define('ABSPATH', dirname(__FILE__) . '/');
    }
    if (!defined('DOING_AUTOSAVE')) {
        define('DOING_AUTOSAVE', false);
    }
}

// Завантажуємо класи плагіна
require_once dirname(dirname(__DIR__)) . '/includes/class-poll-metabox.php';
require_once dirname(dirname(__DIR__)) . '/includes/class-poll-ajax.php';
require_once dirname(dirname(__DIR__)) . '/includes/class-poll-shortcode.php';

echo "Bootstrap завантажено успішно!\n";