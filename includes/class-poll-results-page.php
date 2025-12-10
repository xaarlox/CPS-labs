<?php
if (!defined('ABSPATH')) exit;

class IPZE_Poll_Results_Page {

    public function __construct() {
        add_action('admin_menu', [$this, 'add_results_page']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_scripts']);
    }

    public function add_results_page() {
        add_submenu_page(
            'edit.php?post_type=ipze_poll',
            'Результати опитувань',
            'Результати',
            'manage_options',
            'ipze-poll-results',
            [$this, 'render_results_page']
        );
    }

    public function enqueue_scripts($hook) {
        if ($hook !== 'ipze_poll_page_ipze-poll-results') return;
        
        wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js', [], '4.4.0', true);
        wp_enqueue_style('ipze-results-style', plugin_dir_url(__FILE__) . '../assets/css/results-page.css', [], '1.0');
    }

    public function render_results_page() {
        // Отримуємо всі опубліковані опитування
        $polls = get_posts([
            'post_type' => 'ipze_poll',
            'post_status' => 'publish',
            'numberposts' => -1,
            'orderby' => 'date',
            'order' => 'DESC'
        ]);

        $selected_poll_id = isset($_GET['poll_id']) ? intval($_GET['poll_id']) : 0;
        
        ?>
        <div class="wrap ipze-results-wrap">
            <h1>Результати опитувань</h1>

            <?php if (empty($polls)): ?>
                <div class="notice notice-info">
                    <p>Немає опублікованих опитувань. Створіть опитування щоб побачити результати.</p>
                </div>
            <?php else: ?>
                
                <div class="ipze-poll-selector">
                    <label for="poll-select">Оберіть опитування:</label>
                    <select id="poll-select" onchange="window.location.href='?post_type=ipze_poll&page=ipze-poll-results&poll_id=' + this.value">
                        <option value="">-- Оберіть опитування --</option>
                        <?php foreach ($polls as $poll): ?>
                            <option value="<?php echo $poll->ID; ?>" <?php selected($selected_poll_id, $poll->ID); ?>>
                                <?php echo esc_html($poll->post_title); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>

                <?php if ($selected_poll_id): ?>
                    <?php $this->display_poll_results($selected_poll_id); ?>
                <?php else: ?>
                    <div class="notice notice-warning">
                        <p>Оберіть опитування зі списку вище.</p>
                    </div>
                <?php endif; ?>

            <?php endif; ?>
        </div>
        <?php
    }

    private function display_poll_results($poll_id) {
        $poll = get_post($poll_id);
        if (!$poll) return;

        $questions = get_post_meta($poll_id, '_ipze_questions', true);
        $results = get_post_meta($poll_id, '_ipze_poll_results', true);

        ?>
        <div class="ipze-results-container">
            <h2><?php echo esc_html($poll->post_title); ?></h2>
            
            <?php if (!$results || !is_array($results) || empty($results)): ?>
                <div class="notice notice-info">
                    <p>Результатів ще немає. Статистика з'явиться після того, як хтось пройде опитування.</p>
                </div>
            <?php else: ?>
                
                <div class="ipze-summary">
                    <div class="ipze-summary-card">
                        <div class="ipze-summary-number"><?php echo count($results); ?></div>
                        <div class="ipze-summary-label">Всього відповідей</div>
                    </div>
                    <div class="ipze-summary-card">
                        <div class="ipze-summary-number"><?php echo count($questions); ?></div>
                        <div class="ipze-summary-label">Питань в опитуванні</div>
                    </div>
                </div>

                <?php if (!$questions || !is_array($questions)): ?>
                    <p>Питання не знайдені.</p>
                <?php else: ?>
                    
                    <?php foreach ($questions as $q_index => $question): ?>
                        <?php
                        $q_text = isset($question['question']) ? $question['question'] : '';
                        $q_type = isset($question['type']) ? $question['type'] : 'text';
                        $q_options = isset($question['options']) && is_array($question['options']) ? $question['options'] : [];
                        ?>

                        <div class="ipze-question-results">
                            <h3>Питання <?php echo $q_index + 1; ?>: <?php echo esc_html($q_text); ?></h3>
                            <div class="ipze-question-type-label">
                                <?php 
                                if ($q_type === 'text') {
                                    echo 'Тип: Текстова відповідь';
                                } elseif ($q_type === 'multiple') {
                                    echo 'Тип: Множинний вибір';
                                } else {
                                    echo 'Тип: Одна відповідь';
                                }
                                ?>
                            </div>

                            <?php if ($q_type === 'text'): ?>
                                <!-- Текстові відповіді -->
                                <div class="ipze-text-responses">
                                    <p class="ipze-response-count">Всього відповідей: <strong><?php 
                                        $text_count = 0;
                                        foreach ($results as $res) {
                                            if (isset($res['question_' . $q_index]) && !empty($res['question_' . $q_index])) {
                                                $text_count++;
                                            }
                                        }
                                        echo $text_count;
                                    ?></strong></p>
                                    
                                    <?php if ($text_count > 0): ?>
                                        <table class="wp-list-table widefat fixed striped">
                                            <thead>
                                                <tr>
                                                    <th style="width: 60px;">#</th>
                                                    <th>Відповідь</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <?php 
                                                $answer_num = 1;
                                                foreach ($results as $res): 
                                                    $ans = isset($res['question_' . $q_index]) ? $res['question_' . $q_index] : '';
                                                    if ($ans && trim($ans) !== ''):
                                                ?>
                                                    <tr>
                                                        <td><strong><?php echo $answer_num; ?></strong></td>
                                                        <td><?php echo nl2br(esc_html($ans)); ?></td>
                                                    </tr>
                                                <?php 
                                                    $answer_num++;
                                                    endif;
                                                endforeach; 
                                                ?>
                                            </tbody>
                                        </table>
                                    <?php else: ?>
                                        <p class="ipze-no-data">Немає відповідей на це питання.</p>
                                    <?php endif; ?>
                                </div>

                            <?php else: ?>
                                <!-- Діаграма для single/multiple -->
                                <?php
                                $counts = [];
                                foreach ($q_options as $opt) {
                                    $counts[$opt] = 0;
                                }

                                $total_answers = 0;
                                foreach ($results as $res) {
                                    $ans = isset($res['question_' . $q_index]) ? $res['question_' . $q_index] : [];
                                    if (!is_array($ans)) $ans = [$ans];
                                    
                                    foreach ($ans as $a) {
                                        if (isset($counts[$a])) {
                                            $counts[$a]++;
                                            $total_answers++;
                                        }
                                    }
                                }

                                $chart_id = 'chart_' . $poll_id . '_' . $q_index;
                                ?>

                                <p class="ipze-response-count">
                                    Всього голосів: <strong><?php echo $total_answers; ?></strong>
                                    <?php if ($q_type === 'multiple'): ?>
                                        (користувачі могли обрати кілька варіантів)
                                    <?php endif; ?>
                                </p>

                                <?php if ($total_answers > 0): ?>
                                <div class="ipze-chart-wrapper">
                                    <canvas id="<?php echo $chart_id; ?>" width="400" height="200"></canvas>
                                </div>
                                <?php else: ?>
                                <p class="ipze-no-data">Немає голосів для цього питання.</p>
                                <?php endif; ?>

                                <table class="wp-list-table widefat fixed striped ipze-stats-table">
                                    <thead>
                                        <tr>
                                            <th>Варіант відповіді</th>
                                            <th style="width: 100px; text-align: center;">Голосів</th>
                                            <th style="width: 250px;">Відсоток від загальної кількості</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php 
                                        $total_responses = count($results);
                                        foreach ($counts as $opt => $cnt): 
                                            $percentage = $total_responses > 0 ? round(($cnt / $total_responses) * 100, 1) : 0;
                                        ?>
                                            <tr>
                                                <td><strong><?php echo esc_html($opt); ?></strong></td>
                                                <td style="text-align: center; font-weight: bold; font-size: 16px;"><?php echo intval($cnt); ?></td>
                                                <td>
                                                    <div class="ipze-progress-bar-wrapper">
                                                        <div class="ipze-progress-bar-fill" style="width: <?php echo $percentage; ?>%;">
                                                            <span class="ipze-progress-text"><?php echo $percentage; ?>%</span>
                                                        </div>
                                                    </div>
                                                </td>
                                            </tr>
                                        <?php endforeach; ?>
                                    </tbody>
                                </table>

                                <script>
                                (function waitForChartAndInit(){
                                    if (typeof Chart === 'undefined') {
                                        setTimeout(waitForChartAndInit, 50);
                                        return;
                                    }

                                    const ctx = document.getElementById('<?php echo $chart_id; ?>');
                                    if (!ctx) return;

                                    new Chart(ctx, {
                                        type: 'pie',
                                        data: {
                                            labels: <?php echo json_encode(array_keys($counts)); ?>,
                                            datasets: [{
                                                label: 'Кількість голосів',
                                                data: <?php echo json_encode(array_values($counts)); ?>,
                                                    backgroundColor: <?php echo json_encode(array_slice(["#E53935","#43A047","#1E88E5","#00ACC1","#FB8C00","#8E24AA","#7CB342","#546E7A"], 0, count($counts))); ?>,
                                                borderColor: '#ffffff',
                                                borderWidth: 1
                                            }]
                                        },
                                        options: {
                                            responsive: true,
                                            maintainAspectRatio: true,
                                            plugins: {
                                                legend: {
                                                    display: true,
                                                    position: 'right'
                                                },
                                                title: {
                                                    display: true,
                                                    text: 'Розподіл відповідей',
                                                    font: {
                                                        size: 14,
                                                        weight: 'bold'
                                                    },
                                                    color: '#1d2327'
                                                }
                                            }
                                        }
                                    });
                                })();
                                </script>

                            <?php endif; ?>
                        </div>

                    <?php endforeach; ?>

                <?php endif; ?>

            <?php endif; ?>
        </div>
        <?php
    }
}