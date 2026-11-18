from django.db import models
import uuid
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.core.validators import RegexValidator

from django.conf import settings


class MainUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        if not username:
            raise ValueError("User must have a username.")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            username=username,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MainUser(AbstractBaseUser):
    class Role(models.TextChoices):
        OWNER = "OWERNER", "owner"
        RETAILER = "RETAILER", "Retailer"


    id = models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?[1-9]\d{9,14}$",
                message="Enter a valid phone number"
            )
        ]
    )
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20,
    choices=Role.choices,
    default=Role.RETAILER)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MainUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class RetailerProfile(models.Model):

    class Approval(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="retailer")
    shop_name = models.CharField(max_length=200)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True, unique=True, validators=[
        RegexValidator(
            regex=r"\+?[1-9]\d{9,14}$",
            message="Enter a valid mobile number"
        )
    ])
    business_email = models.EmailField()
    shop_logo = models.ImageField(upload_to="retailer/logo", blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True)
    approval_status = models.CharField(max_length=20, choices=Approval.choices, default=Approval.PENDING)
    credit_enabled = models.BooleanField(default=False)
    credit_limit = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.shop_name


class RetailerStore(models.Model):
    id = models.UUIDField(editable=False, default=uuid.uuid4, primary_key=True)
    retailer = models.ForeignKey(RetailerProfile, on_delete=models.CASCADE, related_name="retail_store")
    store_code = models.CharField(max_length=6)
    contact_person_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True, validators=[
        RegexValidator(
            regex=r"\+?[1-9]\d{9,14}$",
            message="Enter a valid mobile number"
        )
    ])
    address_1 = models.CharField(max_length=40)
    address_2 = models.CharField(max_length=100)
    landmark = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    district = models.CharField(max_length=20)
    pincode = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)


    def __str__(self):
        return self.contact_person_name


