from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Lab, Submission, Attempt, CyberPhysicalSystemSimulation
from django.http import JsonResponse
import json
import math


def home(request):
    return render(request, 'home.html')


@login_required(login_url='login')
def labs(request):
    labs_qs = Lab.objects.all()

    lab_items = []
    for lab in labs_qs:
        # Для текущего пользователя ищем submission, если есть
        submission = None
        try:
            submission = Submission.objects.filter(lab=lab, profile=request.user.profile).first()
        except Exception:
            submission = None

        attempts_left = submission.attempts_left if submission and submission.attempts_left is not None else lab.max_attempts
        best_mark = submission.best_mark if submission and submission.best_mark is not None else None
        status = submission.status if submission else 'new'

        lab_items.append({
            'lab': lab,
            'submission': submission,
            'attempts_left': attempts_left,
            'best_mark': best_mark,
            'status': status,
        })

    context = {'lab_items': lab_items}
    return render(request, 'labs/labs.html', context)


@login_required(login_url='login')
def lab(request, pk):
    labObj = Lab.objects.get(id=pk)
    return render(request, 'labs/lab.html', {'lab': labObj})


@login_required(login_url='login')
def cps_simulation(request, pk):
    """
    Вьюха для лабораторної роботи з фізики
    Вибирає шаблон залежно від типу симуляції
    """
    lab = get_object_or_404(Lab, id=pk)
    
    # Отримуємо або створюємо submission
    submission, created = Submission.objects.get_or_create(
        lab=lab,
        profile=request.user.profile,
        defaults={'attempts_left': lab.max_attempts}
    )
    
    context = {
        'lab': lab,
        'submission': submission,
    }
    
    # Вибираємо шаблон залежно від назви лаби
    title_lower = lab.title.lower()
    
    if 'балістик' in title_lower or 'баллистик' in title_lower:
        template = 'labs/ballistics_simulation.html'
    elif 'термод' in title_lower or 'термодинам' in title_lower:
        template = 'labs/Termodynamika.html'
    elif 'оптик' in title_lower or 'світло' in title_lower or 'light' in title_lower:
        template = 'labs/light.html'
    elif 'маятник' in title_lower:
        template = 'labs/pendulum_simulation.html'
    elif 'спутник' in title_lower:
        template = 'labs/satellite_simulation.html'
    elif 'електр' in title_lower or 'струм' in title_lower or 'електрика' in title_lower or 'електрич' in title_lower:
        template = 'labs/electronics_simulation.html'
    elif 'електромагнітне' in title_lower or 'электромагнитное' in title_lower:
        template = 'labs/electromagnetic_simulation.html'
    elif 'хвилі' in title_lower or 'волны' in title_lower:
        template = 'labs/wave_simulation.html'
    else:
        template = 'labs/cps_simulation.html'
    
    return render(request, template, context)


def simulate_step(request):
    """
    API endpoint для виконання одного кроку симуляції
    Параметри: current_value, target_value, kp, ki, kd, prev_error, prev_integral, lab_type, step
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=400)
    
    try:
        data = json.loads(request.body)
        
        current_value = float(data.get('current_value', 0))
        target_value = float(data.get('target_value', 100))
        kp = float(data.get('kp', 0.5))
        ki = float(data.get('ki', 0.1))
        kd = float(data.get('kd', 0.2))
        prev_error = float(data.get('prev_error', 0))
        prev_integral = float(data.get('prev_integral', 0))
        dt = float(data.get('dt', 0.1))
        lab_type = data.get('lab_type', 'water_tank')
        step = int(data.get('step', 0))
        
        # Обчислення помилки
        error = target_value - current_value
        
        # PID контролер
        integral = prev_integral + error * dt
        derivative = (error - prev_error) / dt if dt > 0 else 0
        
        # Обчислення керуючого сигналу
        control_signal = kp * error + ki * integral + kd * derivative
        
        # Обмеження control_signal
        control_signal = max(-100, min(100, control_signal))
        
        # Різні моделі систем для різних типів лаб
        if lab_type == 'water_tank':
            # Резервуар: повільна система з великою інерцією
            tau = 8.0
            damping = 0.3
            new_value = current_value + (control_signal / 100.0) * (target_value - current_value) * (dt / tau)
            # Нелінійність: чим вище рівень, тим більше відповір
            if current_value > 80:
                new_value *= 0.7
            noise = (hash(str(current_value) + str(step)) % 100 - 50) * 0.015
            
        elif lab_type == 'temperature':
            # Температура: дуже повільна система, но чутлива до коливань
            tau = 12.0
            new_value = current_value + (control_signal / 100.0) * (target_value - current_value) * (dt / tau)
            # Температурна інерція більша
            if step % 5 == 0:  # Періодичні скачки
                new_value += (target_value - current_value) * 0.05
            noise = (hash(str(current_value) + str(step)) % 100 - 50) * 0.008
            
        elif lab_type == 'speed_control':
            # Швидкість: швидка система, але з затримкою
            tau = 3.0
            new_value = current_value + (control_signal / 100.0) * (target_value - current_value) * (dt / tau)
            # Затримка на старті
            if current_value < 20 and control_signal > 0:
                new_value *= 1.2
            # Фрикція на високих швидкостях
            if current_value > 100:
                new_value *= 0.95
            noise = (hash(str(current_value) + str(step)) % 100 - 50) * 0.01
            
        elif lab_type == 'pressure':
            # Тиск: нестійка система з резонансом
            tau = 4.0
            # Нелінійна відповідь при високому тиску
            response_factor = dt / tau
            if current_value > 80:
                response_factor *= 2.0  # Експоненціальна реакція
            new_value = current_value + (control_signal / 100.0) * (target_value - current_value) * response_factor
            noise = (hash(str(current_value) + str(step)) % 100 - 50) * 0.02
        else:
            tau = 5.0
            new_value = current_value + (control_signal / 100.0) * (target_value - current_value) * (dt / tau)
            noise = (hash(str(current_value) + str(step)) % 100 - 50) * 0.01
        
        new_value += noise
        
        # Обмеження значення
        new_value = max(0, min(150, new_value))
        
        return JsonResponse({
            'success': True,
            'new_value': round(new_value, 2),
            'error': round(error, 2),
            'control_signal': round(control_signal, 2),
            'integral': round(integral, 2),
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def calculate_score(request):
    """
    API endpoint для розрахунку оцінки на основі даних симуляції
    Різні критерії для різних типів систем
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=400)
    
    try:
        data = json.loads(request.body)
        simulation_data = data.get('simulation_data', [])
        target_value = float(data.get('target_value', 100))
        lab_type = data.get('lab_type', 'water_tank')
        
        if not simulation_data:
            return JsonResponse({'score': 0, 'feedback': 'Немає даних симуляції'})
        
        # Розраховуємо метрики якості
        errors = [abs(point['value'] - target_value) for point in simulation_data]
        total_error = sum(errors)
        max_error = max(errors) if errors else 0
        final_error = errors[-1] if errors else 100
        mean_error = total_error / len(errors) if errors else 0
        
        # Розрахунок перелівання
        max_overshoot = max([point['value'] - target_value for point in simulation_data if point['value'] > target_value]) if simulation_data else 0
        max_undershoot = min([target_value - point['value'] for point in simulation_data if point['value'] < target_value]) if simulation_data else 0
        
        # Розрахунок часу встановлення (коли помилка < 5%)
        settling_time = len(simulation_data)
        for i, point in enumerate(simulation_data):
            if abs(point['value'] - target_value) < target_value * 0.05:
                settling_time = i
                break
        
        base_score = 100
        
        # Різні критерії для різних типів систем
        if lab_type == 'water_tank':
            # Для резервуара: головне - точність і гладкість
            if final_error < 1:
                final_penalty = 0
            elif final_error < 3:
                final_penalty = 5
            elif final_error < 8:
                final_penalty = 15
            else:
                final_penalty = 35
            
            mean_penalty = min(25, mean_error * 1.5)
            overshoot_penalty = min(15, max_overshoot * 0.8)
            settling_bonus = max(0, min(10, 200 / (settling_time + 1)))
            
        elif lab_type == 'temperature':
            # Для температури: головне - стабільність і відсутність коливань
            if final_error < 0.5:
                final_penalty = 0
            elif final_error < 2:
                final_penalty = 8
            elif final_error < 5:
                final_penalty = 18
            else:
                final_penalty = 40
            
            mean_penalty = min(30, mean_error * 2)
            # Коливання дуже штрафуються
            oscillation_penalty = max_overshoot * 1.5 if max_overshoot > 2 else 0
            settling_bonus = max(0, min(15, 500 / (settling_time + 1)))
            
        elif lab_type == 'speed_control':
            # Для швидкості: головне - швидкість реакції
            if final_error < 2:
                final_penalty = 0
            elif final_error < 5:
                final_penalty = 10
            elif final_error < 12:
                final_penalty = 20
            else:
                final_penalty = 40
            
            mean_penalty = min(20, mean_error * 1.2)
            overshoot_penalty = min(10, max_overshoot * 0.5)
            settling_bonus = max(0, min(20, 150 / (settling_time + 1)))
            
        elif lab_type == 'pressure':
            # Для тиску: головне - стійкість та відсутність нестійкості
            if final_error < 3:
                final_penalty = 0
            elif final_error < 7:
                final_penalty = 12
            elif final_error < 15:
                final_penalty = 25
            else:
                final_penalty = 45
            
            mean_penalty = min(28, mean_error * 1.8)
            # Мокно штрафується за нестійкість
            instability_penalty = max_overshoot * 2 if max_overshoot > 15 else max_overshoot * 1.2
            settling_bonus = max(0, min(12, 300 / (settling_time + 1)))
        else:
            final_penalty = 30
            mean_penalty = 20
            overshoot_penalty = 15
            settling_bonus = 5
        
        score = base_score - final_penalty - mean_penalty - overshoot_penalty + settling_bonus
        score = max(0, min(100, score))
        
        feedback = f"Кінцева помилка: {final_error:.2f} | Середня: {mean_error:.2f} | Перелів: {max_overshoot:.2f}"
        
        return JsonResponse({
            'success': True,
            'score': round(score, 2),
            'feedback': feedback,
            'details': {
                'final_error': round(final_error, 2),
                'mean_error': round(mean_error, 2),
                'max_error': round(max_error, 2),
                'max_overshoot': round(max_overshoot, 2),
                'settling_time': settling_time,
            }
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required(login_url='login')
def submit_ballistics_result(request):
    """
    API endpoint для збереження результату балістичного пострілу
    Параметри: lab_id, score, error_distance, angle, velocity, distance
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=400)
    
    try:
        data = json.loads(request.body)
        lab_id = data.get('lab_id')
        score = float(data.get('score', 0))
        
        # Отримуємо лабу та submission
        lab = Lab.objects.get(id=lab_id)
        submission, created = Submission.objects.get_or_create(
            lab=lab,
            profile=request.user.profile,
            defaults={'attempts_left': lab.max_attempts}
        )
        
        # Перевіряємо, чи залишилось спроб
        if submission.attempts_left <= 0:
            return JsonResponse({'error': 'No attempts left'}, status=400)
        
        # Створюємо спробу
        attempt_number = submission.attempts.count() + 1
        attempt = Attempt.objects.create(
            submission=submission,
            mark=score,
            attempt_number=attempt_number,
            answers={
                'angle': data.get('angle'),
                'velocity': data.get('velocity'),
                'error_distance': data.get('error_distance'),
                'distance': data.get('distance'),
            }
        )
        
        # Оновлюємо submission
        submission.attempts_left -= 1
        if score > (submission.best_mark or 0):
            submission.best_mark = score
        submission.status = 'submitted'
        submission.save()
        
        return JsonResponse({
            'success': True,
            'attempt_id': str(attempt.id),
            'attempts_left': submission.attempts_left,
            'best_mark': submission.best_mark,
        })
    
    except Lab.DoesNotExist:
        return JsonResponse({'error': 'Lab not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required(login_url='login')
def submit_cps_result(request):
    """
    Generic API endpoint для збереження результату для CPS/термодинамічних лаб
    Параметри: lab_id, score, answers (optional)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=400)

    try:
        data = json.loads(request.body)
        lab_id = data.get('lab_id')
        score = float(data.get('score', 0))

        # Отримуємо лабу та submission
        lab = Lab.objects.get(id=lab_id)
        submission, created = Submission.objects.get_or_create(
            lab=lab,
            profile=request.user.profile,
            defaults={'attempts_left': lab.max_attempts}
        )

        # Перевіряємо, чи залишилось спроб
        if submission.attempts_left <= 0:
            return JsonResponse({'error': 'No attempts left'}, status=400)

        # Створюємо спробу
        attempt_number = submission.attempts.count() + 1
        attempt = Attempt.objects.create(
            submission=submission,
            mark=score,
            attempt_number=attempt_number,
            answers=data.get('answers', None)
        )

        # Оновлюємо submission
        submission.attempts_left -= 1
        if score > (submission.best_mark or 0):
            submission.best_mark = score
        submission.status = 'submitted'
        submission.save()

        return JsonResponse({
            'success': True,
            'attempt_id': str(attempt.id),
            'attempts_left': submission.attempts_left,
            'best_mark': submission.best_mark,
        })

    except Lab.DoesNotExist:
        return JsonResponse({'error': 'Lab not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
