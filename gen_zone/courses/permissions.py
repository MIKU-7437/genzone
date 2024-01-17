from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Пользователь может редактировать только свои объекты.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
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
    Пользователь может взаимодействовать с курсом только если у него есть к нему доступ.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'course'):
            return obj.course in request.user.courses.all() or obj.course.owner == request.user

        if hasattr(obj, 'owner'):
            return obj in request.user.courses.all() or obj.owner == request.user

        if hasattr(obj, 'module') and hasattr(obj.module, 'course'):
            return obj.module.course in request.user.courses.all() or obj.module.course.owner == request.user

        if hasattr(obj, 'lesson') and hasattr(obj.lesson, 'module'):
            return obj.lesson.module.course == request.user.courses.all() or obj.lesson.module.course.owner == request.user
        return False


class CanEditCourse(BasePermission):
    """
    Пользователь может редактировать курс только если он владелец курса.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH']:
            return hasattr(obj, 'owner') and obj.owner == request.user
        return True
