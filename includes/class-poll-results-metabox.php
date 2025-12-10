<?php
if (!defined('ABSPATH')) exit;

class IPZE_Poll_Results_Metabox {

    public function __construct() {
        add_action('add_meta_boxes', [$this, 'add_results_metabox']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue_chart_scripts']);
    }

    public function enqueue_chart_scripts($hook) {
        global $post;
        if ($hook !== 'post.php' || !$post || $post->post_type !== 'ipze_poll') return;
        
        wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js', [], '4.4.0', true);
    }

    public function add_results_metabox() {
        add_meta_box(
            'ipze_poll_results',
            '📊 Результати опитування',
            [$this, 'render_results'],
            'ipze_poll',
            'normal',
            'default'
        );
    }

    public function render_results($post) {
        $questions = get_post_meta($post->ID, '_ipze_questions', true);
        $results = get_post_meta($post->ID, '_ipze_poll_results', true);

        if (!$results || !is_array($results) || empty($results)) {
            echo '<div style="text-align:center; padding:40px; background:#f9f9f9; border-radius:8px;">';
            echo '<p style="font-size:18px; color:#666;">📭 Результатів ще немає.</p>';
            echo '<p style="color:#999;">Статистика з\'явиться після того, як хтось пройде опитування.</p>';
            echo '</div>';
            return;
        }

        $total_responses = count($results);
        
        echo '<div class="ipze-summary-stats">';
        echo '👥 Всього учасників: <strong>' . $total_responses . '</strong>';
        echo '</div>';

        if (!$questions || !is_array($questions)) {
            echo '<p>Питання не знайдені.</p>';
            return;
        }

        foreach ($questions as $q_index => $question) {
            $q_text = isset($question['question']) ? $question['question'] : '';
            $q_type = isset($question['type']) ? $question['type'] : 'text';
            $q_options = isset($question['options']) && is_array($question['options']) ? $question['options'] : [];

            echo '<div class="ipze-results-section">';
            echo '<h4>Питання ' . ($q_index + 1) . ': ' . esc_html($q_text) . '</h4>';

            if ($q_type === 'text') {
                // Текстові відповіді
                echo '<div class="ipze-text-answers">';
                echo '<ul style="list-style:none; padding:0; margin:0;">';
                $answer_num = 1;
                foreach ($results as $res) {
                    $ans = isset($res['question_' . $q_index]) ? $res['question_' . $q_index] : '';
                    if ($ans) {
                        echo '<li><strong>Відповідь ' . $answer_num . ':</strong> ' . esc_html($ans) . '</li>';
                        $answer_num++;
                    }
                }
                echo '</ul>';
                echo '</div>';
            } else {
                // Діаграма для single/multiple
                $counts = [];
                foreach ($q_options as $opt) {
                    $counts[$opt] = 0;
                }

                foreach ($results as $res) {
                    $ans = isset($res['question_' . $q_index]) ? $res['question_' . $q_index] : [];
                    if (!is_array($ans)) $ans = [$ans];
                    
                    foreach ($ans as $a) {
                        if (isset($counts[$a])) {
                            $counts[$a]++;
                        }
                    }
                }

                $chart_id = 'chart_' . $post->ID . '_' . $q_index;

                $labels = array_keys($counts);
                $data = array_values($counts);
                $sum_data = array_sum($data);
                $colors = $this->generate_colors(count($labels));

                if ($sum_data > 0) {
                    echo '<div class="ipze-chart-container">';
                    echo '<canvas id="' . $chart_id . '" width="400" height="200"></canvas>';
                    echo '</div>';
                } else {
                    echo '<p style="color:#666;">Немає голосів для цього питання.</p>';
                }

                ?>
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
                            labels: <?php echo json_encode($labels); ?>,
                            datasets: [{
                                label: 'Кількість відповідей',
                                data: <?php echo json_encode($data); ?>,
                                backgroundColor: <?php echo json_encode($colors); ?>,
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
                                    text: 'Статистика відповідей',
                                    font: {
                                        size: 16,
                                        weight: 'bold'
                                    },
                                    color: '#2F2156'
                                }
                            }
                        }
                    });
                })();
                </script>
                <?php

                // Таблиця з даними
                echo '<table style="width:100%; margin-top:15px; border-collapse:collapse;">';
                echo '<thead><tr style="background:#2F2156; color:white;">';
                echo '<th style="padding:10px; text-align:left; border:1px solid #ddd;">Варіант</th>';
                echo '<th style="padding:10px; text-align:center; border:1px solid #ddd;">Голосів</th>';
                echo '<th style="padding:10px; text-align:center; border:1px solid #ddd;">Відсоток</th>';
                echo '</tr></thead><tbody>';
                
                foreach ($counts as $opt => $cnt) {
                    $percentage = $total_responses > 0 ? round(($cnt / $total_responses) * 100, 1) : 0;
                    echo '<tr>';
                    echo '<td style="padding:10px; border:1px solid #ddd;">' . esc_html($opt) . '</td>';
                    echo '<td style="padding:10px; text-align:center; border:1px solid #ddd; font-weight:bold;">' . intval($cnt) . '</td>';
                    echo '<td style="padding:10px; text-align:center; border:1px solid #ddd;">';
                    echo '<div style="background:#f0f0f0; border-radius:10px; overflow:hidden; height:25px; position:relative;">';
                    echo '<div style="background:#FFD700; width:' . $percentage . '%; height:100%; transition:width 0.3s;"></div>';
                    echo '<span style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-weight:bold; color:#2F2156;">' . $percentage . '%</span>';
                    echo '</div>';
                    echo '</td>';
                    echo '</tr>';
                }
                
                echo '</tbody></table>';
            }

            echo '</div>'; // .ipze-results-section
        }
    }

    private function generate_colors($count) {
        $base_colors = [
            '#E53935', // red
            '#43A047', // green
            '#1E88E5', // blue
            '#00ACC1', // teal
            '#FB8C00', // orange
            '#8E24AA', // purple
            '#7CB342', // lime/green
            '#546E7A', // slate
        ];
        
        $colors = [];
        for ($i = 0; $i < $count; $i++) {
            $colors[] = $base_colors[$i % count($base_colors)];
        }
        
        return $colors;
    }
}