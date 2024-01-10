from django.contrib import admin
from .models import Course, Module, Lesson, Step, Content
from django.utils.html import format_html

class ContentInline(admin.StackedInline):
    model = Content
    extra = 1

class StepInline(admin.StackedInline):
    model = Step
    inlines = [ContentInline]
    extra = 1

class LessonInline(admin.StackedInline):
    model = Lesson
    inlines = [StepInline]
    extra = 1

class ModuleInline(admin.StackedInline):
    model = Module
    inlines = [LessonInline]
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [ModuleInline]
    readonly_fields = ('image_tag',)
    list_display = ('title', 'description', 'owner', 'rating', 'price', 'image_tag')
    search_fields = ('title', 'owner__username')
    list_filter = ('owner',)

    def image_tag(self, obj):
        return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.preview.url)
    
    image_tag.short_description = 'Image'

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('course', 'module_num', 'module_title', 'module_description')
    list_filter = ('course',)
    search_fields = ('module_title',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    inlines = [StepInline]
    list_display = ('module', 'lesson_num', 'lesson_title', 'lesson_description')
    list_filter = ('module__course', 'module')
    search_fields = ('lesson_title',)

@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    inlines = [ContentInline]
    list_display = ('lesson', 'step_num')
    list_filter = ('lesson__module__course', 'lesson__module', 'lesson')
    search_fields = ('step_num',)

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    pass
