<?php
/*
Plugin Name: IPZE Poll
Description: Базовий модуль опитувань для сайту кафедри ІПЗЕ.
Version: 1.0
Author: Anfisa
*/

if ( ! defined( 'ABSPATH' ) ) exit;

require_once plugin_dir_path(__FILE__) . 'includes/class-poll-post-type.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-poll-metabox.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-poll-shortcode.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-poll-shortcode-metabox.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-poll-ajax.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-poll-results-page.php';
require_once plugin_dir_path(__FILE__) . 'includes/class-poll-duplicator.php';

class IPZE_Poll {

    public function __construct() {
        // Реєстрація CPT
        new IPZE_Poll_Post_Type();

        // Метабокс для питань
        new IPZE_Poll_Metabox();

        // Шорткод [ipze_poll id="123"]
        new IPZE_Poll_Shortcode();

        // Метабокс для шорткода у адмінці
        new IPZE_Poll_Shortcode_Metabox();

        // AJAX
        new IPZE_Poll_Ajax();

        // Окрема сторінка результатів
        new IPZE_Poll_Results_Page();

        // Дублювання опитувань
        new IPZE_Poll_Duplicator();

        // Підключення стилів/скриптів
        add_action('wp_enqueue_scripts', [$this, 'enqueue_assets']);
    }

    public function enqueue_assets() {
        wp_enqueue_style(
            'ipze-poll-style',
            plugin_dir_url(__FILE__) . 'assets/css/style.css'
        );

        wp_enqueue_script(
            'ipze-poll-js',
            plugin_dir_url(__FILE__) . 'assets/js/poll.js',
            ['jquery'],
            false,
            true
        );

        wp_localize_script('ipze-poll-js', 'ipze_poll_ajax', [
            'url' => admin_url('admin-ajax.php'),
        ]);
    }
}


add_action('plugins_loaded', function() {
    new IPZE_Poll();
});