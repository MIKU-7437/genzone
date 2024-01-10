from django.db import models
from users.models import User as UsersUser
from django.core.exceptions import ValidationError
from django.core.management.utils import get_random_secret_key


def course_preview_upload_path(instance, filename):
    return f'courses/{instance.title}_{get_random_secret_key()[:8]}/preview/{filename}'

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(UsersUser, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    preview = models.ImageField(upload_to=course_preview_upload_path, null=False, blank=False)
    price = models.IntegerField(default = 0)

    def __str__(self):
        return self.title
    
    def clean(self):
        if not self.preview:
            raise ValidationError({'preview': 'Это поле обязательно.'})

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    module_num = models.IntegerField()
    module_title = models.CharField(max_length=255)
    module_description = models.TextField()

    def __str__(self):
        return self.module_title
    
    class Meta:
        unique_together = ['course', 'module_num']

    

class Lesson(models.Model):
    module = models.ForeignKey(Module, related_name='lessons', on_delete=models.CASCADE)
    lesson_num = models.IntegerField()
    lesson_title = models.CharField(max_length=255)
    lesson_description = models.TextField()

    def __str__(self):
        return self.lesson_title
    
    class Meta:
        unique_together = ['module', 'lesson_num']
    
class Step(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='steps', on_delete=models.CASCADE)
    step_num = models.IntegerField()

    def __str__(self):
        return f'{self.lesson.lesson_title}.{self.step_num}'

    class Meta:
        unique_together = ['lesson', 'step_num']



def content_upload_path(instance, filename):
    return f'courses/{instance.step.lesson.module.course.title}_{instance.step.lesson.module.course.id}/{instance.step.lesson.module.module_title}/{instance.step.lesson.lesson_title}/{filename}'


class Content(models.Model):
    TEXT_TYPE = 'text'
    IMAGE_TYPE = 'image'
    VIDEO_TYPE = 'video'
    
    CONTENT_TYPES = [
        (TEXT_TYPE, 'Text'),
        (IMAGE_TYPE, 'Image'),
        (VIDEO_TYPE, 'Video'),
    ]
    
    step = models.ForeignKey(Step, related_name='contents', on_delete=models.CASCADE)
    content_num = models.IntegerField()
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=content_upload_path, blank=True, null=True)
    width = models.CharField(max_length=10, blank=True, null=True)
    height = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        unique_together = ['step', 'content_num']

    def __str__(self):
        return f'{self.step} - Content {self.content_num} ({self.get_content_type_display()})'

