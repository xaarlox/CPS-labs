from django.contrib import admin
from .models import Lab, Submission, Attempt


admin.site.register(Lab)
admin.site.register(Submission)
admin.site.register(Attempt)