from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Разрешение только для администраторов.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    request.user.user_role == 'Admin')


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Разрешение для менеджеров и администраторов.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    request.user.user_role in ['Manager', 'Admin'])


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешение для владельца объекта или администратора.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ администратору
        if request.user.user_role == 'Admin':
            return True

        # Проверяем, является ли пользователь владельцем объекта
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'user_id'):
            return obj.user_id == request.user.user_id

        return False


class ProductPermission(permissions.BasePermission):
    """
    Разрешения для товаров:
    - Все аутентифицированные пользователи могут просматривать
    - Только администраторы могут создавать/редактировать/удалять
    """

    def has_permission(self, request, view):
        # Разрешаем GET, HEAD, OPTIONS для всех аутентифицированных
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Для остальных методов (POST, PUT, PATCH, DELETE) - только админы
        return bool(request.user and request.user.is_authenticated and
                    request.user.user_role == 'Admin')


class OrderPermission(permissions.BasePermission):
    """
    Разрешения для заказов:
    - User: может создавать и просматривать свои заказы
    - Manager: может просматривать все заказы и менять статус
    - Admin: полный доступ
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            # Создание заказа доступно всем аутентифицированным пользователям
            return request.user and request.user.is_authenticated

        # Для просмотра списка заказов
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Администратор имеет полный доступ
        if request.user.user_role == 'Admin':
            return True

        # Менеджер может просматривать и изменять статус заказов
        if request.user.user_role == 'Manager':
            return True

        # Пользователь может просматривать только свои заказы
        return obj.user == request.user


class CategoryPermission(permissions.BasePermission):
    """
    Разрешения для категорий:
    - Все аутентифицированные пользователи могут просматривать
    - Только администраторы могут создавать/редактировать/удалять
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True  # Разрешаем просмотр даже неавторизованным

        return bool(request.user and request.user.is_authenticated and
                    request.user.user_role == 'Admin')


class UserPermission(permissions.BasePermission):
    """
    Разрешения для пользователей:
    - Каждый может регистрироваться (POST без аутентификации)
    - Аутентифицированный пользователь может просматривать свой профиль
    - Администратор имеет полный доступ
    """

    def has_permission(self, request, view):
        # Разрешаем регистрацию без аутентификации
        if view.action == 'create':
            return True

        # Для других действий требуется аутентификация
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Администратор имеет полный доступ
        if request.user.user_role == 'Admin':
            return True

        # Пользователь может просматривать и редактировать только свой профиль
        return obj == request.user