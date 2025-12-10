jQuery(document).ready(function($) {
    let questionIndex = $('#ipze-questions-wrapper .ipze-question-block').length;

    // Валідація перед збереженням
    $(document).on('click', '#publish, #save-post', function(e) {
        const $wrapper = $('#ipze-questions-wrapper');
        const questions = $wrapper.find('.ipze-question-block');
        
        // Перевіряємо, чи є хоча б одне питання
        if (questions.length === 0) {
            e.preventDefault();
            alert('Помилка: Опитування повинно містити хоча б одне питання!');
            $wrapper.focus();
            return false;
        }
        
        // Перевіряємо кожне питання
        let isValid = true;
        questions.each(function() {
            const $block = $(this);
            const type = $block.find('select[name*="[type]"]').val();
            const question = $block.find('input[name*="[question]"]').val().trim();
            const $optionsList = $block.find('.ipze-options-list');
            const filledOptions = $optionsList.find('input[type="text"]').filter(function() {
                return $(this).val().trim() !== '';
            }).length;
            
            // Якщо тип не текстовий, перевіряємо варіанти
            if (type !== 'text' && filledOptions === 0) {
                alert('Помилка: Питання "' + (question || 'Без назви') + '" повинно мати хоча б один варіант відповіді!');
                isValid = false;
                return false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            return false;
        }
    });

    // Додавання нового питання
    $('#ipze-add-question').on('click', function() {
        const template = $('#ipze-question-template').html();
        const newQuestion = template
            .replace(/__INDEX__/g, questionIndex)
            .replace(/__NUMBER__/g, questionIndex + 1);
        
        $('#ipze-questions-wrapper').append(newQuestion);
        $('.ipze-empty-state').remove();
        questionIndex++;
        updateQuestionNumbers();
    });

    // Перемикання редагування
    $(document).on('click', '.ipze-toggle-edit', function(e) {
        e.preventDefault();
        const $block = $(this).closest('.ipze-question-block');
        const $body = $block.find('.ipze-question-body');
        
        if ($body.is(':visible')) {
            // Зберігаємо та закриваємо
            const questionText = $block.find('input[name*="[question]"]').val();
            const questionType = $block.find('select[name*="[type]"]').val();
            
            $block.find('.ipze-question-preview').text(questionText || 'Нове питання');
            
            let typeBadge = '';
            if (questionType === 'single') typeBadge = 'Одна відповідь';
            else if (questionType === 'multiple') typeBadge = 'Множинний вибір';
            else typeBadge = 'Текстова відповідь';
            
            $block.find('.ipze-question-type-badge').text(typeBadge);
            $body.slideUp(300);
        } else {
            $body.slideDown(300);
        }
    });

    // Видалення питання
    $(document).on('click', '.ipze-remove-question', function(e) {
        e.preventDefault();
        if (confirm('Ви впевнені, що хочете видалити це питання?')) {
            $(this).closest('.ipze-question-block').slideUp(300, function() {
                $(this).remove();
                updateQuestionNumbers();
                
                if ($('#ipze-questions-wrapper .ipze-question-block').length === 0) {
                    $('#ipze-questions-wrapper').html('<p class="ipze-empty-state">Ще немає питань. Натисніть кнопку нижче, щоб додати перше питання.</p>');
                }
            });
        }
    });

    // Додавання варіанта
    $(document).on('click', '.ipze-add-option', function(e) {
        e.preventDefault();
        const $list = $(this).siblings('.ipze-options-list');
        const $block = $(this).closest('.ipze-question-block');
        const index = $block.data('index');
        const optionNumber = $list.find('.ipze-option-item').length + 1;
        
        const newOption = `
            <div class="ipze-option-item">
                <span class="ipze-option-number">${optionNumber}.</span>
                <input type="text" name="ipze_questions[${index}][options][]" placeholder="Варіант відповіді...">
                <button class="ipze-remove-option" type="button" title="Видалити варіант">Видалити</button>
            </div>
        `;
        
        $list.append(newOption);
    });

    // Видалення варіанта
    $(document).on('click', '.ipze-remove-option', function(e) {
        e.preventDefault();
        const $list = $(this).closest('.ipze-options-list');
        
        // Перевіряємо скільки непустих варіантів
        const filledOptions = $list.find('input[type="text"]').filter(function() {
            return $(this).val().trim() !== '';
        }).length;
        
        if (filledOptions > 1 || $list.find('.ipze-option-item').length > 1) {
            $(this).closest('.ipze-option-item').slideUp(200, function() {
                $(this).remove();
                updateOptionNumbers($list);
            });
        } else {
            alert('Повинен залишитися хоча б один варіант відповіді!');
        }
    });

    // Зміна типу питання
    $(document).on('change', '.ipze-question-type-select', function() {
        const type = $(this).val();
        const $optionsBox = $(this).closest('.ipze-question-body').find('.ipze-options-box');
        
        if (type === 'text') {
            $optionsBox.slideUp(200);
        } else {
            $optionsBox.slideDown(200);
        }
    });

    // Оновлення нумерації питань
    function updateQuestionNumbers() {
        $('#ipze-questions-wrapper .ipze-question-block').each(function(index) {
            $(this).find('.ipze-question-number').text('Питання ' + (index + 1));
            $(this).attr('data-index', index);
            
            // Оновлюємо атрибути name
            $(this).find('input[name*="[question]"]').attr('name', `ipze_questions[${index}][question]`);
            $(this).find('select[name*="[type]"]').attr('name', `ipze_questions[${index}][type]`);
            $(this).find('input[name*="[options]"]').each(function() {
                $(this).attr('name', `ipze_questions[${index}][options][]`);
            });
        });
    }

    // Оновлення нумерації варіантів
    function updateOptionNumbers($list) {
        $list.find('.ipze-option-item').each(function(index) {
            $(this).find('.ipze-option-number').text((index + 1) + '.');
        });
    }

    // Ініціалізація сортування
    if ($.fn.sortable) {
        $('#ipze-questions-wrapper').sortable({
            handle: '.ipze-drag-handle',
            placeholder: 'ui-sortable-placeholder',
            axis: 'y',
            update: function() {
                updateQuestionNumbers();
            }
        });
    }

    // Ініціалізація - закриваємо всі блоки при завантаженні
    $('.ipze-question-body').hide();
});