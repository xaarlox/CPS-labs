<?php
if (!defined('ABSPATH')) exit;

class IPZE_Poll_Metabox {

    public function __construct() {
        add_action('add_meta_boxes', [$this, 'add_metabox']);
        add_action('save_post', [$this, 'save']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_assets']);
    }

    public function enqueue_assets($hook) {
        global $post;
        if ($hook !== 'post.php' && $hook !== 'post-new.php') return;
        if (!$post || $post->post_type !== 'ipze_poll') return;
        
        wp_enqueue_style('ipze-poll-admin', plugin_dir_url(__FILE__) . '../assets/css/admin-style.css', [], '1.0');
        wp_enqueue_script('ipze-poll-admin', plugin_dir_url(__FILE__) . '../assets/js/admin-poll.js', ['jquery', 'jquery-ui-sortable'], '1.0', true);
    }

    public function add_metabox() {
        add_meta_box(
            'ipze_poll_metabox',
            'Питання опитування',
            [$this, 'render'],
            'ipze_poll',
            'normal',
            'high'
        );
    }

    public function render($post) {
        $questions = get_post_meta($post->ID, '_ipze_questions', true);
        if (!is_array($questions)) $questions = [];

        wp_nonce_field('ipze_poll_save', 'ipze_poll_nonce');
        ?>
        <div id="ipze-questions-wrapper">
            <?php if (empty($questions)): ?>
                <p class="ipze-empty-state">Ще немає питань. Натисніть кнопку нижче, щоб додати перше питання.</p>
            <?php else: ?>
                <?php foreach ($questions as $index => $q): ?>
                    <div class="ipze-question-block" data-index="<?php echo $index; ?>">
                        <div class="ipze-question-header">
                            <span class="ipze-drag-handle">&#8597;</span>
                            <span class="ipze-question-number">Питання <?php echo $index + 1; ?></span>
                            <span class="ipze-question-preview"><?php echo esc_html($q['question']); ?></span>
                            <span class="ipze-question-type-badge"><?php 
                                echo $q['type'] === 'single' ? 'Одна відповідь' : 
                                    ($q['type'] === 'multiple' ? 'Множинний вибір' : 'Текстова відповідь'); 
                            ?></span>
                            <button class="ipze-toggle-edit button" type="button">Редагувати</button>
                        </div>
                        <div class="ipze-question-body">
                            <div class="ipze-form-group">
                                <label><strong>Текст питання:</strong></label>
                                <input type="text" name="ipze_questions[<?php echo $index; ?>][question]" 
                                       value="<?php echo esc_attr($q['question']); ?>" 
                                       class="ipze-input-full" 
                                       placeholder="Введіть ваше питання...">
                            </div>
                            
                            <div class="ipze-form-group">
                                <label><strong>Тип відповіді:</strong></label>
                                <select name="ipze_questions[<?php echo $index; ?>][type]" class="ipze-question-type-select">
                                    <option value="single" <?php selected($q['type'],'single'); ?>>Одна відповідь</option>
                                    <option value="multiple" <?php selected($q['type'],'multiple'); ?>>Кілька відповідей</option>
                                    <option value="text" <?php selected($q['type'],'text'); ?>>Текстова відповідь</option>
                                </select>
                            </div>

                            <div class="ipze-options-box" style="<?php echo $q['type'] === 'text' ? 'display:none;' : ''; ?>">
                                <label><strong>Варіанти відповідей:</strong></label>
                                <div class="ipze-options-list">
                                    <?php 
                                    $opts = isset($q['options']) && is_array($q['options']) ? $q['options'] : [''];
                                    foreach ($opts as $opt_index => $opt): ?>
                                        <div class="ipze-option-item">
                                            <span class="ipze-option-number"><?php echo $opt_index + 1; ?>.</span>
                                            <input type="text" 
                                                   name="ipze_questions[<?php echo $index; ?>][options][]" 
                                                   value="<?php echo esc_attr($opt); ?>" 
                                                   placeholder="Варіант відповіді...">
                                            <button class="ipze-remove-option button" type="button" title="Видалити варіант">Видалити</button>
                                        </div>
                                    <?php endforeach; ?>
                                </div>
                                <button class="ipze-add-option button" type="button">Додати варіант</button>
                            </div>

                            <div class="ipze-question-actions">
                                <button class="ipze-remove-question button" type="button">Видалити питання</button>
                                <button class="ipze-toggle-edit button button-primary" type="button">Зберегти</button>
                            </div>
                        </div>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </div>
        <button type="button" id="ipze-add-question" class="button button-primary button-large">Додати нове питання</button>
        
        <!-- Шаблон для нового питання -->
        <script type="text/template" id="ipze-question-template">
            <div class="ipze-question-block" data-index="__INDEX__">
                <div class="ipze-question-header">
                    <span class="ipze-drag-handle">&#8597;</span>
                    <span class="ipze-question-number">Питання __NUMBER__</span>
                    <span class="ipze-question-preview">Нове питання</span>
                    <span class="ipze-question-type-badge">Одна відповідь</span>
                    <button class="ipze-toggle-edit button" type="button">Редагувати</button>
                </div>
                <div class="ipze-question-body" style="display:block;">
                    <div class="ipze-form-group">
                        <label><strong>Текст питання:</strong></label>
                        <input type="text" name="ipze_questions[__INDEX__][question]" class="ipze-input-full" placeholder="Введіть ваше питання...">
                    </div>
                    <div class="ipze-form-group">
                        <label><strong>Тип відповіді:</strong></label>
                        <select name="ipze_questions[__INDEX__][type]" class="ipze-question-type-select">
                            <option value="single">Одна відповідь</option>
                            <option value="multiple">Кілька відповідей</option>
                            <option value="text">Текстова відповідь</option>
                        </select>
                    </div>
                    <div class="ipze-options-box">
                        <label><strong>Варіанти відповідей:</strong></label>
                        <div class="ipze-options-list">
                            <div class="ipze-option-item">
                                <span class="ipze-option-number">1.</span>
                                <input type="text" name="ipze_questions[__INDEX__][options][]" placeholder="Варіант відповіді...">
                                <button class="ipze-remove-option button" type="button" title="Видалити варіант">Видалити</button>
                            </div>
                        </div>
                        <button class="ipze-add-option button" type="button">Додати варіант</button>
                    </div>
                    <div class="ipze-question-actions">
                        <button class="ipze-remove-question button" type="button">Видалити питання</button>
                        <button class="ipze-toggle-edit button button-primary" type="button">Зберегти</button>
                    </div>
                </div>
            </div>
        </script>
        <?php
    }

    public function save($post_id) {
        if (!isset($_POST['ipze_poll_nonce']) || !wp_verify_nonce($_POST['ipze_poll_nonce'], 'ipze_poll_save')) return;
        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;
        if (!current_user_can('edit_post', $post_id)) return;
        if (get_post_type($post_id) !== 'ipze_poll') return;

        $questions = isset($_POST['ipze_questions']) ? $_POST['ipze_questions'] : [];
        
        $sanitized_questions = [];
        foreach ($questions as $q) {
            $sanitized = [
                'question' => sanitize_text_field($q['question'] ?? ''),
                'type' => sanitize_text_field($q['type'] ?? 'single'),
                'options' => []
            ];
            
            if (isset($q['options']) && is_array($q['options'])) {
                $sanitized['options'] = array_values(array_filter(array_map('sanitize_text_field', $q['options'])));
            }
            
            if (!empty($sanitized['question'])) {
                // Валідація: для не-текстових питань повинен бути хоча б один варіант
                if ($sanitized['type'] !== 'text' && empty($sanitized['options'])) {
                    // Пропускаємо питання без варіантів
                    continue;
                }
                $sanitized_questions[] = $sanitized;
            }
        }
        
        // Валідація: опитування повинно мати хоча б одне питання
        if (empty($sanitized_questions)) {
            add_action('admin_notices', function() {
                echo '<div class="notice notice-error"><p><strong>Помилка:</strong> Опитування повинно містити хоча б одне питання з варіантами відповідей!</p></div>';
            });
            return;
        }
        
        update_post_meta($post_id, '_ipze_questions', $sanitized_questions);
    }
}