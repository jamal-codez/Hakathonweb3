from django.db import models
import random
# import logging
import secrets
# import jwt
import uuid
# from collections import Counter
# from decimal import Decimal
# import datetime
# from django.contrib.auth.models import Permission, Group
# from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, UserManager
# from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.core.mail import send_mass_mail, EmailMessage, get_connection, EmailMultiAlternatives
# from django.conf import settings
# from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.postgres.fields import ArrayField
# from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.hashers import make_password, check_password




# from .validators import phone_number_validator, full_name_validator, numeric_validator, acct_number_validator
# from .socket_service import WebsocketService



# Create your models here.

class BaseManager(UserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('full_name',"Admin "+str(secrets.token_urlsafe(8)))
        extra_fields.setdefault('phone_number',"0901234"+str(random.randint(1000,9999)))
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

# Models Section   

class MessageTypes(models.TextChoices):
    DOCUMENT = "document","Document"
    TEXT = "text", "Text"
    AUDIO = "audio","Audio"
    IMAGE = "image","Image"
    
class User(AbstractUser):
    """
    The model representing the User table in the database.
    Seen in the database as `core_user`.
    Represents all the possible users of the app. 
    Whether admins, contractors, superadmins or normal users
    """
    username = None
    first_name = None
    last_name = None
    full_name = models.CharField(
        _("Full Name"),
        max_length=200,
        )
    
    email = models.EmailField(
        _('Email'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    phone_number = models.CharField(
        _('Phone Number'),
        max_length=11,
        unique=True,
    )
    email_verified = models.BooleanField(default= False)
    # pin=models.CharField(max_length=128, default=make_password('0000'))
    photo = models.ImageField(null=True, blank=True, upload_to="photos")
    last_login = models.DateTimeField(_("last login"), default=timezone.now)
    objects = BaseManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        indexes = [
            models.Index(fields=["id","email"])
        ]

    def __str__(self) :
        return f"{self.email}"
    
    @property
    def has_pin(self):
        if check_password('0000', self.pin):
            return False
        else:
            return True
    


    # def set_pin(self, raw_pin):
    #     """
    #     Set the pin for the user. The pin will be encrypted.
    #     """
    #     self.pin = make_password(raw_pin)
    
    # def check_pin(self, raw_pin):
    #     """
    #     Check if the given pin matches the encrypted pin.
    #     """
    #     return check_password(raw_pin, self.pin)
    


class SolariGroup(models.Model):
    admin = models.ForeignKey(User, on_delete = models.CASCADE)    
    name = models.CharField(max_length = 200)
    description = models.CharField(max_length = 2000)
    picture = models.FileField(upload_to="group_picture", null=True, blank=True)
    members = models.ManyToManyField(User, related_name="solari_groups")
    date_created = models.DateTimeField(auto_now_add = True)

    class Meta:
        verbose_name_plural = "solari_groups"
        indexes = [
            models.Index(fields=["name"]), # indexes for faster querying
            models.Index(fields=["id"]),
        ]

    def __str__(self):
        return self.name


class SolariSubGroup(models.Model):
    group=models.ForeignKey(SolariGroup, on_delete = models.CASCADE)    
    admin = models.ForeignKey(User, on_delete = models.CASCADE)    
    name = models.CharField(max_length = 200)
    description = models.CharField(max_length = 2000)
    picture = models.FileField(upload_to="subgroup_picture", null=True, blank=True)
    members = models.ManyToManyField(User, related_name="solari_subgroups")
    date_created = models.DateTimeField(auto_now_add = True)


class SolariGroupChatSpace(models.Model):
    id = models.UUIDField(default = uuid.uuid4, primary_key = True, editable = False)
    group= models.OneToOneField(SolariGroup,on_delete = models.CASCADE)

    def __str__(self):
        return self.group.name
    
class SolariGroupMessage(models.Model):
    chatspace = models.ForeignKey(SolariGroupChatSpace, on_delete = models.CASCADE)
    sender = models.ForeignKey(User, on_delete = models.SET_NULL, null=True)
    type = models.CharField(max_length = 10,choices = MessageTypes.choices)
    content = models.TextField(blank = True, null = True)
    file = models.FileField(upload_to="upload", blank=True, null=True)
    created = models.DateTimeField(auto_now_add = True)
    class Meta:
        indexes = [
            models.Index(fields=['chatspace', 'created']),
        ]

    def __str__(self):
        return str(self.id)+self.content 
    


class SolariSubGroupChatSpace(models.Model):
    id = models.UUIDField(default = uuid.uuid4, primary_key = True, editable = False)
    sub_group= models.OneToOneField(SolariSubGroup,on_delete = models.CASCADE)

    def __str__(self):
        return self.group.name
    
class SolariSubGroupMessage(models.Model):
    chatspace = models.ForeignKey(SolariSubGroupChatSpace, on_delete = models.CASCADE)
    sender = models.ForeignKey(User, on_delete = models.SET_NULL, null=True)
    type = models.CharField(max_length = 10,choices = MessageTypes.choices)
    content = models.TextField(blank = True, null = True)
    file = models.FileField(upload_to="upload", blank=True, null=True)
    created = models.DateTimeField(auto_now_add = True)
    class Meta:
        indexes = [
            models.Index(fields=['chatspace', 'created']),
        ]

    def __str__(self):
        return str(self.id)+self.content 
    

class UserChatSpace(models.Model):
    id = models.UUIDField(default= uuid.uuid4, editable=False, primary_key = True)
    users = models.ManyToManyField(User)

    def __str__(self):
        return f"User Chat - {self.id}"
    
class UserMessage(models.Model):
    chatspace = models.ForeignKey(UserChatSpace, on_delete = models.CASCADE)
    sender = models.ForeignKey(User, on_delete = models.SET_NULL, null=True)
    type = models.CharField(max_length = 10,choices = MessageTypes.choices)
    content = models.TextField(blank = True, null = True)
    file = models.FileField(upload_to="upload", blank=True, null=True)
    created = models.DateTimeField(auto_now_add = True)
