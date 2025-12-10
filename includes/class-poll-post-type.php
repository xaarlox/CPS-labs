<?php
if ( ! defined( 'ABSPATH' ) ) exit;

class IPZE_Poll_Post_Type {

    public function __construct() {
        add_action('init', [$this, 'register_post_type']);
    }

    public function register_post_type() {
        $labels = [
            'name'               => 'Опитування',
            'singular_name'      => 'Опитування',
            'menu_name'          => 'Опитування',
            'add_new'            => 'Додати нове',
            'add_new_item'       => 'Додати нове опитування',
            'edit_item'          => 'Редагувати опитування',
            'new_item'           => 'Нове опитування',
            'view_item'          => 'Переглянути опитування',
            'search_items'       => 'Пошук опитувань',
            'not_found'          => 'Нічого не знайдено',
            'not_found_in_trash' => 'В кошику немає опитувань',
        ];

        $args = [
            'labels' => $labels,
            'public' => true,
            'show_ui' => true,
            'show_in_menu' => true,
            'menu_icon' => 'dashicons-chart-bar',
            'menu_position' => 25,
            'has_archive' => false,
            'supports' => ['title', 'editor'],
            'rewrite' => ['slug' => 'poll'],
        ];

        register_post_type('ipze_poll', $args);
    }
}

