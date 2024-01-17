from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Разрешение только для чтения для всех запросов
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешение доступа к изменению/удалению только владельцу объекта
        return obj.id == request.user.id