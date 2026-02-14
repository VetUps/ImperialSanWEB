from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator

from .models import CustomUser, Category, Product


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
    class Meta:
        model = Category
        fields = ['category_id', 'category_title', 'category_description', 'parent_category_id']


class ProductSerializer(serializers.ModelSerializer):
    category_title = serializers.ReadOnlyField(source='category.category_title')

    class Meta:
        model = Product
        fields = ['product_id', 'product_title', 'product_description',
                  'product_price', 'product_quantity_in_stock',
                  'product_image_url', 'category', 'category_title',
                  'product_brand_title', 'product_date_of_create',
                  'product_is_active']