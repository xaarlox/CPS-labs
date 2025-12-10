<?php
if (!defined('ABSPATH')) exit;
?>

<div class="ipze-poll-container" id="ipze-poll-<?php echo $poll_id; ?>">
        
        <!-- Титульна сторінка -->
        <div class="ipze-screen ipze-welcome-screen active">
            <div class="ipze-welcome-content">
                <h1 class="ipze-poll-title"><?php echo esc_html($post->post_title); ?></h1>
                
                <?php if ($post->post_content): ?>
                    <div class="ipze-poll-description">
                        <?php echo wp_kses_post(wpautop($post->post_content)); ?>
                    </div>
                <?php endif; ?>
                
                <div class="ipze-poll-info">
                    <div class="ipze-info-item">
                        <span>Питань: <strong><?php echo count($questions); ?></strong></span>
                    </div>
                    <div class="ipze-info-item">
                        <span>Приблизно: <strong><?php echo ceil(count($questions) * 0.5); ?> хв</strong></span>
                    </div>
                </div>
                
                <button type="button" class="ipze-start-btn" onclick="startPoll()">
                    Почати
                </button>
            </div>
        </div>

        <!-- Форма з питаннями -->
        <form method="post" action="" class="ipze-poll-form" id="ipze-poll-form-<?php echo $poll_id; ?>" style="display:none;">
            <input type="hidden" name="poll_id" value="<?php echo $poll_id; ?>">
            <input type="hidden" name="action" value="ipze_submit_poll">
            
            <!-- Прогрес бар -->
            <div class="ipze-progress-container">
                <div class="ipze-progress-bar">
                    <div class="ipze-progress-fill" id="progress-fill"></div>
                </div>
                <div class="ipze-progress-text">
                    Питання <span id="current-question">1</span> з <?php echo count($questions); ?>
                </div>
            </div>

            <?php foreach ($questions as $index => $question): ?>
                <div class="ipze-screen ipze-question-screen" data-question="<?php echo $index; ?>" style="display:none;">
                    <div class="ipze-question-content">
                        <div class="ipze-question-header">
                            <h3 class="ipze-question-text"><?php echo esc_html($question['question']); ?></h3>
                        </div>

                        <div class="ipze-options">
                            <?php if ($question['type'] === 'single'): ?>
                                <?php foreach ($question['options'] as $opt_index => $option): ?>
                                    <label class="ipze-option">
                                        <input 
                                            type="radio" 
                                            name="question_<?php echo $index; ?>" 
                                            value="<?php echo esc_attr($option); ?>" 
                                            required>
                                        <span class="ipze-option-text"><?php echo esc_html($option); ?></span>
                                        <span class="ipze-option-check">✓</span>
                                    </label>
                                <?php endforeach; ?>

                            <?php elseif ($question['type'] === 'multiple'): ?>
                                <?php foreach ($question['options'] as $opt_index => $option): ?>
                                    <label class="ipze-option ipze-option-checkbox">
                                        <input 
                                            type="checkbox" 
                                            name="question_<?php echo $index; ?>[]" 
                                            value="<?php echo esc_attr($option); ?>">
                                        <span class="ipze-option-text"><?php echo esc_html($option); ?></span>
                                        <span class="ipze-option-check">✓</span>
                                    </label>
                                <?php endforeach; ?>
                                <p class="ipze-hint">Можна обрати кілька варіантів</p>

                            <?php elseif ($question['type'] === 'text'): ?>
                                <textarea 
                                    name="question_<?php echo $index; ?>" 
                                    class="ipze-text-input" 
                                    rows="6" 
                                    placeholder="Введіть вашу відповідь тут..." 
                                    required></textarea>
                            <?php endif; ?>
                        </div>

                        <div class="ipze-navigation">
                            <?php if ($index > 0): ?>
                                <button type="button" class="ipze-nav-btn ipze-prev-btn" onclick="prevQuestion(<?php echo $index; ?>)">
                                    Назад
                                </button>
                            <?php endif; ?>
                            
                            <?php if ($index < count($questions) - 1): ?>
                                <button type="button" class="ipze-nav-btn ipze-next-btn" onclick="nextQuestion(<?php echo $index; ?>)">
                                    Далі
                                </button>
                            <?php else: ?>
                                <button type="submit" class="ipze-nav-btn ipze-submit-btn">
                                    Завершити
                                </button>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>
            <?php endforeach; ?>
        </form>
</div>

<script>
let currentQuestion = 0;
const totalQuestions = <?php echo count($questions); ?>;

function startPoll() {
    document.querySelector('.ipze-welcome-screen').style.display = 'none';
    document.querySelector('.ipze-poll-form').style.display = 'block';
    showQuestion(0);
    updateProgress();
}

function showQuestion(index) {
    document.querySelectorAll('.ipze-question-screen').forEach(screen => {
        screen.style.display = 'none';
    });
    
    const questionScreen = document.querySelector(`[data-question="${index}"]`);
    if (questionScreen) {
        questionScreen.style.display = 'block';
        questionScreen.style.animation = 'slideIn 0.4s ease';
        
        // Скрол вгору — вычисляем безопасную позицию, чтобы не прокрутить выше страницы
        const topPos = Math.max(questionScreen.getBoundingClientRect().top + window.pageYOffset - 100, 0);
        window.scrollTo({
            top: topPos,
            behavior: 'smooth'
        });
    }
    
    currentQuestion = index;
    updateProgress();
}

function nextQuestion(currentIndex) {
    const currentScreen = document.querySelector(`[data-question="${currentIndex}"]`);
    const radioInputs = currentScreen.querySelectorAll('input[type="radio"]');
    const checkboxInputs = currentScreen.querySelectorAll('input[type="checkbox"]');
    const textInput = currentScreen.querySelector('textarea');
    
    let isValid = true;
    
    // Перевірка radio
    if (radioInputs.length > 0) {
        const radioName = radioInputs[0].name;
        const checkedRadio = currentScreen.querySelector(`input[name="${radioName}"]:checked`);
        if (!checkedRadio) {
            isValid = false;
            alert('Будь ласка, оберіть варіант відповіді!');
        }
    }
    
    // Перевірка checkbox (хоча б один має бути обраний)
    if (checkboxInputs.length > 0) {
        const checkedCheckboxes = currentScreen.querySelectorAll('input[type="checkbox"]:checked');
        if (checkedCheckboxes.length === 0) {
            isValid = false;
            alert('Будь ласка, оберіть хоча б один варіант!');
        }
    }
    
    // Перевірка textarea
    if (textInput && !textInput.value.trim()) {
        isValid = false;
        alert('Будь ласка, введіть відповідь!');
    }
    
    if (isValid) {
        showQuestion(currentIndex + 1);
    }
}

function prevQuestion(currentIndex) {
    showQuestion(currentIndex - 1);
}

function updateProgress() {
    const progress = ((currentQuestion + 1) / totalQuestions) * 100;
    const progressFill = document.getElementById('progress-fill');
    const currentQuestionSpan = document.getElementById('current-question');
    
    if (progressFill) {
        progressFill.style.width = progress + '%';
    }
    
    if (currentQuestionSpan) {
        currentQuestionSpan.textContent = currentQuestion + 1;
    }
}

// Обробка кліків на варіанти
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.ipze-option').forEach(option => {
        option.addEventListener('click', function(e) {
            // Якщо клікнули безпосередньо на input - пропускаємо
            if (e.target.tagName === 'INPUT') {
                return;
            }
            
            e.preventDefault();
            e.stopPropagation();
            
            const input = this.querySelector('input');
            if (!input) return;
            
            if (input.type === 'radio') {
                input.checked = true;
                // Оновлюємо всі radio в цій групі
                const name = input.name;
                document.querySelectorAll(`input[name="${name}"]`).forEach(r => {
                    const parent = r.closest('.ipze-option');
                    if (parent) {
                        parent.classList.toggle('checked', r.checked);
                    }
                });
            } else if (input.type === 'checkbox') {
                input.checked = !input.checked;
                this.classList.toggle('checked', input.checked);
            }
        });
    });

    // Валідація перед відправкою
    document.querySelector('.ipze-poll-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const lastQuestion = document.querySelector(`[data-question="${totalQuestions - 1}"]`);
        const radioInputs = lastQuestion.querySelectorAll('input[type="radio"]');
        const checkboxInputs = lastQuestion.querySelectorAll('input[type="checkbox"]');
        const textInput = lastQuestion.querySelector('textarea');
        
        let isValid = true;
        
        // Перевірка radio
        if (radioInputs.length > 0) {
            const radioName = radioInputs[0].name;
            const checkedRadio = lastQuestion.querySelector(`input[name="${radioName}"]:checked`);
            if (!checkedRadio) {
                isValid = false;
                alert('Будь ласка, оберіть варіант відповіді!');
            }
        }
        
        // Перевірка checkbox
        if (checkboxInputs.length > 0) {
            const checkedCheckboxes = lastQuestion.querySelectorAll('input[type="checkbox"]:checked');
            if (checkedCheckboxes.length === 0) {
                isValid = false;
                alert('Будь ласка, оберіть хоча б один варіант!');
            }
        }
        
        // Перевірка textarea
        if (textInput && !textInput.value.trim()) {
            isValid = false;
            alert('Будь ласка, введіть відповідь!');
        }
        
        if (!isValid) {
            return;
        }
        
        // Відправляємо форму через AJAX
        submitPollAjax(this);
    });
});

// Функція відправки через AJAX
function submitPollAjax(form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('.ipze-submit-btn');
    
    // Блокуємо кнопку
    submitBtn.disabled = true;
    submitBtn.textContent = 'Відправка...';
    
    fetch('<?php echo admin_url('admin-ajax.php'); ?>', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Ховаємо форму
            document.querySelector('.ipze-poll-form').style.display = 'none';
            
            // Показуємо повідомлення успіху
            const container = document.querySelector('.ipze-poll-container');
            container.innerHTML = `
                <div class="ipze-success-screen" style="display: block;">
                    <div class="ipze-success-icon">✓</div>
                    <h2>Дякуємо за участь!</h2>
                    <p>Ваші відповіді успішно збережено.</p>
                </div>
            `;
            
            // Прокручуємо до повідомлення
            container.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            alert('Помилка при відправці. Спробуйте ще раз.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Завершити';
        }
    })
    .catch(error => {
        alert('Помилка при відправці. Спробуйте ще раз.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Завершити';
    });
}
</script>

<style>
.ipze-option.selected-animation {
    transform: scale(1.02);
    box-shadow: 0 4px 15px rgba(47, 33, 86, 0.2);
}
</style>