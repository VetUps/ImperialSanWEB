from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator

from .models import CustomUser, Category, Product, Basket, BasketPosition, Order, OrderPosition


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['user_id', 'user_mail', 'user_surname', 'user_name',
                  'user_patronymic', 'user_role']
        read_only_fields = ['user_role']


class RegisterSerializer(serializers.ModelSerializer):
    user_mail = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=CustomUser.objects.all(), message="Эта почта уже занята!"
            )
        ],
    )
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = ['user_mail', 'password', 'user_surname', 'user_name', 'user_patronymic']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            user_mail=validated_data['user_mail'],
            password=validated_data['password'],
            user_surname=validated_data['user_surname'],
            user_name=validated_data['user_name'],
            user_patronymic=validated_data.get('user_patronymic', ''),
        )
        return user


class LoginSerializer(serializers.Serializer):
    user_mail = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['user_mail'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Неверные учетные данные")
        if not user.is_active:
            raise serializers.ValidationError("Учетная запись отключена")
        return user


class CategorySerializer(serializers.ModelSerializer):
    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['category_id', 'category_title', 'category_description', 'parent_category_id', 'full_path']

    def get_full_path(self, obj):
        path = []
        current = obj

        depth = 0
        while current and depth < 10:
            path.append(current.category_title)
            current = current.parent_category
            depth += 1

        return '/'.join(reversed(path))


class ProductSerializer(serializers.ModelSerializer):
    category_title = serializers.ReadOnlyField(source='category.category_title')

    class Meta:
        model = Product
        fields = ['product_id', 'product_title', 'product_description',
                  'product_price', 'product_quantity_in_stock',
                  'product_image_url', 'category', 'category_title',
                  'product_brand_title', 'product_date_of_create',
                  'product_is_active']

    def validate_product_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной")
        elif value > 100000000:
            raise serializers.ValidationError("Цена не может быть такой большой (не больше 100кк)")
        return value

    def validate_product_quantity_in_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Количество не может быть отрицательным")
        return value

    def validate_product_title(self, value):
        if not value or value.strip() == '':
            raise serializers.ValidationError("Название товара не может быть пустым")
        return value


class ProductBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_id', 'product_title', 'product_image_url', 'product_brand_title', 'product_price']


class BasketPositionSerializer(serializers.ModelSerializer):
    product = ProductBriefSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = BasketPosition
        fields = ['basket_position_id', 'product', 'product_id', 'product_quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.product_price * obj.product_quantity

    def validate_product_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество должно быть не менее 1")
        return value


class BasketSerializer(serializers.ModelSerializer):
    positions = BasketPositionSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Basket
        fields = ['basket_id', 'positions', 'total_price', 'total_items']


class OrderPositionSerializer(serializers.ModelSerializer):
    product = ProductBriefSerializer(read_only=True)

    class Meta:
        model = OrderPosition
        fields = ['order_position_id', 'product', 'product_quantity', 'product_price_in_moment']


class OrderSerializer(serializers.ModelSerializer):
    positions = OrderPositionSerializer(many=True, read_only=True)
    status_display = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'order_id', 'date_of_create', 'order_status', 'status_display',
            'delivery_address', 'payment_method', 'price', 'user_comment',
            'positions', 'can_cancel'
        ]
        read_only_fields = ['order_id', 'date_of_create', 'order_status', 'price']

    def get_status_display(self, obj):
        status_colors = {
            'В обработке': 'warning',
            'Собирается': 'info',
            'Собран': 'primary',
            'В пути': 'primary',
            'Доставлен': 'success',
            'Отменён': 'error',
        }
        return {
            'status': obj.order_status,
            'color': status_colors.get(obj.order_status, 'grey')
        }

    def get_can_cancel(self, obj):
        return obj.order_status == 'В обработке'


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['delivery_address', 'payment_method', 'user_comment']

    def validate(self, data):
        # Проверка наличия товаров в корзине
        user = self.context['request'].user
        try:
            basket = user.basket
            if not basket.positions.exists():
                raise serializers.ValidationError("Корзина пуста")
        except Basket.DoesNotExist:
            raise serializers.ValidationError("Корзина не найдена")

        # Проверка наличия на складе
        for position in basket.positions.all():
            if position.product_quantity > position.product.product_quantity_in_stock:
                raise serializers.ValidationError(
                    f"Недостаточно товара '{position.product.product_title}' на склаке. "
                    f"Доступно: {position.product.product_quantity_in_stock}"
                )

        return data


class AdminOrderSerializer(serializers.ModelSerializer):
    """Расширенный сериализатор для администраторов"""
    positions = OrderPositionSerializer(many=True, read_only=True)
    status_display = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'order_id', 'date_of_create', 'order_status', 'status_display',
            'delivery_address', 'payment_method', 'price', 'user_comment',
            'positions', 'can_cancel', 'user_info'
        ]

    def get_user_info(self, obj):
        print(obj.user)
        if obj.user:
            return {
                'user_id': obj.user.user_id,
                'full_name': f"{obj.user.user_surname} {obj.user.user_name}",
                'email': obj.user.user_mail,
                'phone': getattr(obj.user, 'user_phone', None)
            }
        return None

    def get_status_display(self, obj):
        status_colors = {
            'В обработке': 'warning',
            'Собирается': 'info',
            'Собран': 'primary',
            'В пути': 'primary',
            'Доставлен': 'success',
            'Отменён': 'error',
        }
        return {
            'status': obj.order_status,
            'color': status_colors.get(obj.order_status, 'grey')
        }

    def get_can_cancel(self, obj):
        return obj.order_status == 'В обработке'


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления статуса заказа"""

    class Meta:
        model = Order
        fields = ['order_status']

    def validate_order_status(self, value):
        valid_transitions = {
            'В обработке': ['Собирается', 'Отменён'],
            'Собирается': ['Собран', 'Отменён'],
            'Собран': ['В пути'],
            'В пути': ['Доставлен'],
            'Доставлен': [],
            'Отменён': []
        }

        current_status = self.instance.order_status if self.instance else None

        if current_status and value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Нельзя изменить статус '{current_status}' на '{value}'"
            )

        return value