import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxLengthValidator,
    validate_integer,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractBase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                   related_name="%(class)s_created_by", null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING,
                                   related_name="%(class)s_updated_by", null=True, blank=True)

    class Meta:
        abstract = True


class State(AbstractBase):
    name = models.CharField(max_length=100, db_index=True)
    alias = models.SlugField(unique=True, )
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'state'
        verbose_name_plural = "States"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(State, self).save(*args, **kwargs)


class Address(AbstractBase):
    address_line1 = models.CharField("Address line 1", max_length=512)
    address_line2 = models.CharField("Address line 2", max_length=512, default="", blank=True)
    city = models.CharField("City", max_length=256)
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING)
    zip_code = models.CharField("ZIP / Postal code", max_length=12, db_index=True)
    landmark = models.CharField(max_length=100)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)

    class Meta:
        db_table = 'address'
        verbose_name_plural = 'Addresses'
        ordering = ('state', 'city', 'zip_code')

    def get_full_address(self):
        return "%s, %s, %s, %s %s" % (
            self.address_line1,
            self.address_line2,
            self.state.name,
            self.city,
            self.zip_code,

        )

    def __str__(self):
        return self.get_full_address()


# Create your models here.
class User(AbstractUser):
    MALE = 1
    FEMALE = 2
    GENDER_CHOICES = ((MALE, "Male"), (FEMALE, "Female"))
    CUSTOMER = 1
    DELIVERY_BOY = 2
    RESTAURANT_OWNER = 3
    USER_TYPE_CHOICES = (
        (CUSTOMER, "Customer"),
        (DELIVERY_BOY, "Delivery Boy"),
        (RESTAURANT_OWNER, 'Restaurant Owner')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.SmallIntegerField(choices=USER_TYPE_CHOICES, default=CUSTOMER)
    mobile = models.CharField(
        max_length=15, validators=[MaxLengthValidator(15), validate_integer]
    )
    date_of_birth = models.DateField(_("DOB"), null=True, blank=True)
    gender = models.SmallIntegerField(choices=GENDER_CHOICES, null=True, blank=True)
    city = models.CharField(
        null=True, blank=True, max_length=255
    )
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user'


class Restaurant(AbstractBase):
    name = models.CharField(max_length=100)
    website = models.URLField()
    description = models.TextField()
    city = models.CharField(
        null=True, blank=True, max_length=255
    )
    address = models.ForeignKey(Address, on_delete=models.CASCADE)

    class Meta:
        db_table = 'restaurant'


class Menu(AbstractBase):
    name = models.CharField(max_length=100)
    type = models.SmallIntegerField()
    meal_type = models.SmallIntegerField()
    description = models.TextField()
    media = models.FileField()
    banner = models.ImageField()
    price = models.FloatField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'menu'


class Bill(AbstractBase):
    total_cost = models.FloatField()
    coupon_code = models.CharField(max_length=20)
    tax = models.FloatField()
    discount = models.FloatField()

    class Meta:
        db_table = 'bill'


class Cart(AbstractBase):
    menu = models.ForeignKey(Menu, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'cart'


class Order(AbstractBase):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    bill = models.ForeignKey(Bill, on_delete=models.DO_NOTHING)
    status = models.SmallIntegerField()

    class Meta:
        db_table = 'order'


class Delivery(AbstractBase):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    delivery_boy = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="delivered_by")
    user_address = models.ForeignKey(Address, on_delete=models.DO_NOTHING)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.DO_NOTHING)
    bill = models.ForeignKey(Bill, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'delivery'


class Payment(AbstractBase):
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    address = models.ForeignKey(Address, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    payment_status = models.SmallIntegerField()

    class Meta:
        db_table = 'payment'


class Notification(AbstractBase):
    type = models.SmallIntegerField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'notification'


class Rating(AbstractBase):
    APP = 1
    ORDER = 2
    DELIVERY = 3
    DELIVERY_BOY = 4
    RESTAURANT = 5
    MENU = 6

    RATING_TYPES = (
        (APP, 'App'),
        (ORDER, 'Order'),
        (DELIVERY, 'Delivery'),
        (DELIVERY_BOY, 'Delivery Boy'),
        (RESTAURANT, 'Restaurant'),
        (MENU, 'menu'),
    )
    created_by = None
    rating = models.SmallIntegerField(choices=RATING_TYPES)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    type = models.SmallIntegerField()
    menu = models.ForeignKey(Menu, on_delete=models.DO_NOTHING, null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.DO_NOTHING, null=True, blank=True)
    delivery_boy = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='delivery_boy_ratings')
    
    class Meta:
        db_table = 'rating'
