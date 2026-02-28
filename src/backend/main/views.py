import math

from django.http import Http404
from rest_framework import viewsets, permissions
from django.db.models import Q
from django.db import transaction, models
from django.core.paginator import Paginator
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import IsAdmin
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.viewsets import ViewSet

from .models import CustomUser, Product, Category, Basket, BasketPosition, Order, OrderPosition
from .serializers import (
    UserSerializer, LoginSerializer, RegisterSerializer,
    CategorySerializer, ProductSerializer,
    BasketSerializer, BasketPositionSerializer,
    OrderSerializer, OrderCreateSerializer,
    AdminOrderSerializer, OrderStatusUpdateSerializer
)


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
    filterset_fields = ['category']

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
        sort_by_id = self.request.query_params.get('sortById')

        if is_all:
            queryset = Product.objects.all()
        else:
            queryset = Product.objects.filter(product_is_active=True)

        if sort_by_id:
            queryset = queryset.order_by('-product_id')

        # Поиск
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(product_title__icontains=search) |
                Q(product_description__icontains=search) |
                Q(product_brand_title__icontains=search)
            )

        # Цена
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

        # Бренд
        brand = self.request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(product_brand_title=brand)

        # Наличие
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

        print(f"Method: {self.request.method}, QuerySet count: {queryset.count()}")
        return queryset

    def get_object(self):
        # Возвращаем полный queryset не для list метода
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            queryset = Product.objects.all()
        else:
            queryset = self.get_queryset()

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = queryset.filter(**filter_kwargs).first()

        if obj is None:
            raise NotFound(detail='Товар не найден')

        self.check_object_permissions(self.request, obj)
        return obj

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


class BasketViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_or_create_basket(self, user):
        basket, created = Basket.objects.get_or_create(user=user)
        return basket

    def list(self, request):
        """Получить корзину текущего пользователя"""
        basket = self.get_or_create_basket(request.user)
        serializer = BasketSerializer(basket)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Добавить товар в корзину"""
        basket = self.get_or_create_basket(request.user)

        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(product_id=product_id, product_is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Товар не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверка наличия на складе
        if product.product_quantity_in_stock < quantity:
            return Response(
                {
                    'error': 'Недостаточно товара на складе',
                    'available': product.product_quantity_in_stock
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Обновление или создание позиции
        position, created = BasketPosition.objects.get_or_create(
            basket=basket,
            product=product,
            defaults={'product_quantity': quantity}
        )

        if not created:
            # Проверка суммарного количества
            new_quantity = position.product_quantity + quantity
            if new_quantity > product.product_quantity_in_stock:
                return Response(
                    {
                        'error': 'Превышено доступное количество',
                        'available': product.product_quantity_in_stock,
                        'in_basket': position.product_quantity
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            position.product_quantity = new_quantity
            position.save()

        serializer = BasketSerializer(basket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        """Изменить количество товара в корзине"""
        basket = self.get_or_create_basket(request.user)

        position_id = request.data.get('position_id')
        new_quantity = request.data.get('quantity')

        try:
            position = basket.positions.get(basket_position_id=position_id)
        except BasketPosition.DoesNotExist:
            return Response(
                {'error': 'Позиция не найдена в корзине'},
                status=status.HTTP_404_NOT_FOUND
            )

        if new_quantity < 1:
            position.delete()
        else:
            # Проверка наличия на складе
            if new_quantity > position.product.product_quantity_in_stock:
                return Response(
                    {
                        'error': 'Недостаточно товара на складе',
                        'available': position.product.product_quantity_in_stock
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            position.product_quantity = new_quantity
            position.save()

        serializer = BasketSerializer(basket)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Удалить товар из корзины"""
        basket = self.get_or_create_basket(request.user)

        position_id = request.data.get('position_id')

        try:
            position = basket.positions.get(basket_position_id=position_id)
            position.delete()
        except BasketPosition.DoesNotExist:
            return Response(
                {'error': 'Позиция не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BasketSerializer(basket)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Очистить корзину"""
        basket = self.get_or_create_basket(request.user)
        basket.positions.all().delete()

        serializer = BasketSerializer(basket)
        return Response(serializer.data)


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Список заказов пользователя с пагинацией"""
        orders = Order.objects.filter(user=request.user)

        # Пагинация
        page = request.query_params.get('page', 1)
        per_page = request.query_params.get('per_page', 10)

        paginator = Paginator(orders, per_page)
        page_obj = paginator.get_page(page)

        serializer = OrderSerializer(page_obj.object_list, many=True)

        return Response({
            'results': serializer.data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        })

    def retrieve(self, request, pk=None):
        """Получить детали заказа"""
        try:
            order = Order.objects.get(order_id=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Заказ не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request):
        """Оформить заказ из корзины"""
        # Проверка данных
        create_serializer = OrderCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        create_serializer.is_valid(raise_exception=True)

        user = request.user

        try:
            basket = user.basket
        except Basket.DoesNotExist:
            return Response(
                {'error': 'Корзина не найдена'},
                status=status.HTTP_400_BAD_REQUEST
            )

        positions = basket.positions.all()
        if not positions.exists():
            return Response(
                {'error': 'Корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Финальная проверка остатков и расчет цены
        total_price = 0
        for pos in positions:
            product = pos.product
            if pos.product_quantity > product.product_quantity_in_stock:
                return Response(
                    {
                        'error': f'Недостаточно товара "{product.product_title}"',
                        'available': product.product_quantity_in_stock
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            total_price += pos.product_price * pos.product_quantity

        # Создание заказа
        order = Order.objects.create(
            user=user,
            delivery_address=create_serializer.validated_data['delivery_address'],
            payment_method=create_serializer.validated_data['payment_method'],
            user_comment=create_serializer.validated_data.get('user_comment', ''),
            price=total_price
        )

        # Создание позиций заказа и списание со склада
        for pos in positions:
            OrderPosition.objects.create(
                order=order,
                product=pos.product,
                product_quantity=pos.product_quantity,
                product_price_in_moment=pos.product_price
            )

            # Списание со склада
            product = pos.product
            product.product_quantity_in_stock -= pos.product_quantity
            product.save()

        # Очистка корзины
        positions.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отмена заказа"""
        try:
            order = Order.objects.get(order_id=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Заказ не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            order.cancel()
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AdminOrderViewSet(viewsets.ViewSet):
    """Управление заказами для администраторов"""
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = Order.objects.all().select_related('user').prefetch_related(
            'positions', 'positions__product'
        )

        # Фильтрация по статусу
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(order_status=status_filter)

        # Фильтрация по пользователю
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Поиск по ID заказа или email пользователя
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(order_id__icontains=search) |
                models.Q(user__user_mail__icontains=search) |
                models.Q(user__user_surname__icontains=search)
            )

        return queryset.order_by('-date_of_create')

    def list(self, request):
        """Список всех заказов с пагинацией и фильтрацией"""
        queryset = self.get_queryset()

        # Пагинация
        page = request.query_params.get('page', 1)
        per_page = request.query_params.get('per_page', 20)

        paginator = Paginator(queryset, per_page)
        page_obj = paginator.get_page(page)

        serializer = AdminOrderSerializer(page_obj.object_list, many=True)

        # Статистика для дашборда
        stats = {
            'total': Order.objects.count(),
            'in_progress': Order.objects.filter(
                order_status__in=['В обработке', 'Собирается', 'Собран', 'В пути']).count(),
            'delivered': Order.objects.filter(order_status='Доставлен').count(),
            'cancelled': Order.objects.filter(order_status='Отменён').count()
        }

        return Response({
            'results': serializer.data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'stats': stats
        })

    def retrieve(self, request, pk=None):
        """Детали заказа"""
        try:
            order = Order.objects.select_related('user').prefetch_related(
                'positions', 'positions__product'
            ).get(order_id=pk)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Заказ не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AdminOrderSerializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Изменение статуса заказа"""
        try:
            order = Order.objects.get(order_id=pk)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Заказ не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderStatusUpdateSerializer(
            order,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        old_status = order.order_status
        new_status = serializer.validated_data['order_status']

        # Если отмена - возвращаем товары на склад
        if new_status == 'Отменён' and old_status != 'Отменён':
            try:
                order.cancel()
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            order.order_status = new_status
            order.save()

        return Response(AdminOrderSerializer(order).data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Последние 10 заказов для дашборда"""
        orders = Order.objects.select_related('user').order_by('-date_of_create')[:10]
        serializer = AdminOrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика заказов"""
        from django.db.models import Sum, Count, Avg
        from django.utils import timezone
        from datetime import timedelta

        # За последние 30 дней
        thirty_days_ago = timezone.now() - timedelta(days=30)

        stats = {
            'total_orders': Order.objects.count(),
            'total_revenue': Order.objects.filter(
                order_status__in=['Доставлен', 'В пути', 'Собран', 'Собирается']
            ).aggregate(total=Sum('price'))['total'] or 0,
            'recent_orders': Order.objects.filter(date_of_create__gte=thirty_days_ago).count(),
            'recent_revenue': Order.objects.filter(
                date_of_create__gte=thirty_days_ago,
                order_status__in=['Доставлен', 'В пути', 'Собран', 'Собирается']
            ).aggregate(total=Sum('price'))['total'] or 0,
            'avg_order_value': Order.objects.filter(
                order_status__in=['Доставлен', 'В пути', 'Собран', 'Собирается']
            ).aggregate(avg=Avg('price'))['avg'] or 0,
            'by_status': {
                status: Order.objects.filter(order_status=status).count()
                for status, _ in Order.ORDER_STATUS_CHOICES
            }
        }

        return Response(stats)