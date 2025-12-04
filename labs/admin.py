from django.contrib import admin
from .models import Lab, Submission, Attempt, CyberPhysicalSystemSimulation


class LabAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'max_attempts', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['order']


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['lab', 'profile', 'status', 'best_mark', 'attempts_left', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['lab__title', 'profile__user__username']


class AttemptAdmin(admin.ModelAdmin):
    list_display = ['submission', 'attempt_number', 'mark', 'created_at']
    list_filter = ['created_at']
    search_fields = ['submission__lab__title']


class CyberPhysicalSystemSimulationAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'lab_type', 'state', 'current_value', 'target_value', 'success', 'final_score', 'created_at']
    list_filter = ['lab_type', 'state', 'success', 'created_at']
    search_fields = ['attempt__submission__lab__title']
    readonly_fields = ['simulation_data', 'id', 'created_at', 'updated_at']
    fieldsets = (
        ('Основна інформація', {
            'fields': ('attempt', 'lab_type', 'state', 'id')
        }),
        ('Параметри системи', {
            'fields': ('initial_value', 'target_value', 'current_value', 'error_threshold')
        }),
        ('PID Контролер', {
            'fields': ('kp', 'ki', 'kd')
        }),
        ('Часові параметри', {
            'fields': ('simulation_time', 'total_duration')
        }),
        ('Результати', {
            'fields': ('simulation_data', 'success', 'final_score')
        }),
        ('Часові мітки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(Lab, LabAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Attempt, AttemptAdmin)
admin.site.register(CyberPhysicalSystemSimulation, CyberPhysicalSystemSimulationAdmin)