<?php
if (!defined('ABSPATH')) exit;

class IPZE_Poll_Shortcode_Metabox {

    public function __construct() {
        add_action('add_meta_boxes', [$this, 'add_shortcode_box']);
    }

    public function add_shortcode_box() {
        add_meta_box(
            'ipze_poll_shortcode_box',
            'Шорткод опитування',
            [$this, 'render_box'],
            'ipze_poll',
            'side',
            'high'
        );
    }

    public function render_box($post) {
        $shortcode = '[ipze_poll id="' . $post->ID . '"]';
        ?>
        <p>Скопіюйте шорткод для вставки в сторінку або пост:</p>
        <input type="text" value="<?php echo esc_attr($shortcode); ?>" readonly style="width:100%; padding:5px;">
        <p><strong>ID:</strong> <?php echo $post->ID; ?></p>
        <?php
    }
}
