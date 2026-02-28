from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import MinValueValidator


class UserManager(BaseUserManager):
    def create_user(self, user_mail, password=None, **extra_fields):
        if not user_mail:
            raise ValueError('Email обязателен')
        user_mail = self.normalize_email(user_mail)
        user = self.model(user_mail=user_mail, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_mail, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_role', 'Admin')
        return self.create_user(user_mail, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_ROLES = [
        ('User', 'Пользователь'),
        ('Manager', 'Менеджер'),
        ('Admin', 'Администратор'),
    ]

    user_id = models.AutoField(primary_key=True)
    user_mail = models.EmailField(unique=True, max_length=100)
    user_password_hash = models.CharField(max_length=128)  # Django хранит хэши как строки
    user_surname = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    user_patronymic = models.CharField(max_length=100, blank=True, null=True)
    user_role = models.CharField(max_length=10, choices=USER_ROLES, default='User')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'user_mail'
    REQUIRED_FIELDS = ['user_surname', 'user_name', 'user_phone']

    def __str__(self):
        return f"{self.user_surname} {self.user_name}"

    class Meta:
        db_table = 'users'


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                        related_name='children')
    category_title = models.CharField(max_length=60)
    category_description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"
        db_table = 'categories'

    def __str__(self):
        return self.category_title


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_title = models.TextField()
    product_description = models.TextField(blank=True, null=True)
    product_price = models.DecimalField(max_digits=12, decimal_places=2)
    product_quantity_in_stock = models.IntegerField()
    product_image_url = models.URLField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    product_brand_title = models.CharField(max_length=50, blank=True, null=True)
    product_date_of_create = models.DateTimeField(default=timezone.now)
    product_is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.product_title

    class Meta:
        db_table = 'products'


class Basket(models.Model):
    basket_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='basket',
        db_column='user_id'
    )

    class Meta:
        db_table = 'basket'

    def __str__(self):
        return f"Корзина #{self.basket_id} - {self.user}"

    @property
    def total_price(self):
        return sum(
            pos.product_price * pos.product_quantity
            for pos in self.positions.all()
        )

    @property
    def total_items(self):
        return sum(pos.product_quantity for pos in self.positions.all())


class BasketPosition(models.Model):
    basket_position_id = models.AutoField(primary_key=True)
    basket = models.ForeignKey(
        Basket,
        on_delete=models.CASCADE,
        related_name='positions',
        db_column='basket_id'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        db_column='product_id'
    )
    product_quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )

    class Meta:
        db_table = 'basket_position'
        unique_together = [['basket', 'product']]

    def __str__(self):
        return f"{self.product.product_title} x{self.product_quantity}"

    @property
    def product_price(self):
        return self.product.product_price


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('В обработке', 'В обработке'),
        ('Собирается', 'Собирается'),
        ('Собран', 'Собран'),
        ('В пути', 'В пути'),
        ('Доставлен', 'Доставлен'),
        ('Отменён', 'Отменён'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('Онлайн', 'Онлайн'),
        ('Наличными', 'Наличными'),
    ]

    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
        db_column='user_id'
    )
    date_of_create = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='В обработке'
    )
    delivery_address = models.TextField()
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    user_comment = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'order'
        ordering = ['-date_of_create']

    def __str__(self):
        return f"Заказ #{self.order_id} - {self.order_status}"

    def cancel(self):
        """Отмена заказа с возвратом товаров на склад"""
        if self.order_status != 'В обработке':
            raise ValueError("Можно отменить только заказ 'В обработке'")

        # Возврат товаров на склад
        for position in self.positions.all():
            product = position.product
            product.product_quantity_in_stock += position.product_quantity
            product.save()

        self.order_status = 'Отменён'
        self.save()


class OrderPosition(models.Model):
    order_position_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='positions',
        db_column='order_id'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        db_column='product_id'
    )
    product_quantity = models.IntegerField(default=1)
    product_price_in_moment = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'order_position'

    def __str__(self):
        return f"{self.product.product_title if self.product else 'Удалённый товар'} x{self.product_quantity}"