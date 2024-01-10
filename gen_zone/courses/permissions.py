from rest_framework.permissions import BasePermission
from .models import Course

class IsOwnerOrReadOnly(BasePermission):
    """
    Пользователь может редактировать только свои объекты.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        if hasattr(obj, 'course'):
            return obj.course.owner == request.user

        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        if hasattr(obj, 'module') and hasattr(obj.module, 'course'):
            return obj.module.course.owner == request.user
        
        if hasattr(obj, 'lesson') and hasattr(obj.lesson, 'module'):
            return obj.lesson.module.course.owner == request.user
        return False
    
class HasCourse(BasePermission):
    """
    Пользователь может взаимодействовать с курсом только если он у него есть.
    """
    def has_object_permission(self, request, view, obj):

        if hasattr(obj, 'course'):
            return obj.course in request.user.courses.all()

        if isinstance(obj, Course):
            return obj in request.user.courses.all()

        return False


    