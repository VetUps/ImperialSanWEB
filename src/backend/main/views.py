import math

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import CustomUser, Product, Category
from .serializers import (UserSerializer, RegisterSerializer,
                          LoginSerializer, ProductSerializer,
                          CategorySerializer)
from .permissions import IsAdmin, IsManagerOrAdmin
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.viewsets import ViewSet

from .serializers import LoginSerializer, RegisterSerializer


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'total_objects': self.page.paginator.count,
            'total_pages': math.ceil(self.page.paginator.count / self.page_size),
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category']  # Простая фильтрация по категории

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.product_is_active = False
            instance.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response(
                {"detail": 'Товар для удаления не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

    def get_queryset(self):
        """
        Возвращает отфильтрованный и отсортированный кверисет продуктов
        """
        is_all = self.request.query_params.get('is_all')

        if is_all:
            queryset = Product.objects.all()
        else:
            queryset = Product.objects.filter(product_is_active=True)

        # === 1. Поиск (search) ===
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(product_title__icontains=search) |
                Q(product_description__icontains=search) |
                Q(product_brand_title__icontains=search)
            )

        # === 2. Фильтрация по цене ===
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price:
            try:
                min_price_value = float(min_price)
                queryset = queryset.filter(product_price__gte=min_price_value)
            except ValueError:
                pass

        if max_price:
            try:
                max_price_value = float(max_price)
                queryset = queryset.filter(product_price__lte=max_price_value)
            except ValueError:
                pass

        # === 3. Фильтрация по бренду ===
        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(product_brand_title=brand)

        # === 4. Фильтрация по наличию ===
        availability = self.request.query_params.get('availability')
        if availability:
            if availability == 'in_stock':
                queryset = queryset.filter(product_quantity_in_stock__gt=10)
            elif availability == 'out_of_stock':
                queryset = queryset.filter(product_quantity_in_stock=0)
            elif availability == 'low_stock':
                queryset = queryset.filter(
                    product_quantity_in_stock__gt=0,
                    product_quantity_in_stock__lte=10
                )

        # === 5. Сортировка ===
        sort = self.request.query_params.get('sort')
        if sort:
            sort_mapping = {
                'price_asc': 'product_price',
                'price_desc': '-product_price',
                'title_asc': 'product_title',
                'title_desc': '-product_title',
                'newest': '-product_date_of_create',
            }
            order_by = sort_mapping.get(sort)
            if order_by:
                queryset = queryset.order_by(order_by)

        return queryset

    def get_permissions(self):
        """
        Возвращает права доступа в зависимости от действия
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return []


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class UserViewSet(ViewSet):
    @extend_schema(
        request=LoginSerializer,
        responses={200: OpenApiResponse(description="Токен получен")},
        description="Вход по email и паролю",
    )
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data
        token = AccessToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "token": str(token),
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        request=RegisterSerializer,
        responses={201: OpenApiResponse(description="Регистрация успешна")},
        description="Регистрация нового пользователя",
    )
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = AccessToken.for_user(user)

        return Response(
            {
                'message': "Пользователь успешно зарегистрирован.",
                'token': str(token),
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED,
        )
