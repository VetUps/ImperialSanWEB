from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from django.urls import get_resolver
from .views import (UserViewSet, ProductViewSet, CategoryViewSet,)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="user")
router.register(r'products', ProductViewSet, basename="product")
router.register(r'categories', CategoryViewSet)

urlpatterns = router.urls + [
    #path('logout/', LogoutView.as_view(), name='logout'),
]

resolver = get_resolver()
print("\n=== Все зарегистрированные маршруты ===")
for pattern, callback in resolver.reverse_dict.items():
    if isinstance(pattern, str):
        print(f"{pattern}: {callback}")
print("==================================\n")