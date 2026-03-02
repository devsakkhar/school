from django.contrib import admin
from .models import SchoolSettings, Student, StudentClass, StudentSection

admin.site.register(SchoolSettings)
admin.site.register(Student)
admin.site.register(StudentClass)
admin.site.register(StudentSection)
