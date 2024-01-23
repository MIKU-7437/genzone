from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        # Создание пользователя без указания имени пользователя
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Создание суперпользователя без указания имени пользователя
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    # Определение возможных ролей пользователя
    class Roles(models.IntegerChoices):
        STUDENT = 1
        TEACHER = 2
        ADMIN = 3

    # Дополнительные поля для пользователя
    email = models.EmailField(max_length=256, unique=True)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    username = models.CharField(max_length=256)
    role = models.IntegerField(choices=Roles.choices, default=Roles.STUDENT)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    #courses
    courses = models.ManyToManyField('courses.Course', related_name='users', blank=True)
    courses_owned = models.ManyToManyField('courses.Course', related_name='created_by_user', blank=True)
    courses_favorite = models.ManyToManyField('courses.Course', related_name='favorite_for_user', blank=True)
    courses_in_progress = models.ManyToManyField('courses.Course', related_name='in_progress_for_user', blank=True)
    # Фотография пользователя
    photo = models.ImageField(
        upload_to='customer_photos/',
        null=True,
        blank=True,
        default='customer_photos/default-profile-picture.jpg'
    )
    
    # Менеджер объектов для пользователей
    objects = CustomUserManager()

    # Использование электронной почты в качестве уникального идентификатора
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # Определение возможности вывода объекта в виде строки
    def __str__(self):
        return self.email