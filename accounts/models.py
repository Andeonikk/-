from django.contrib.auth.models import AbstractUser
from django.db import models
import random
from datetime import timedelta
from django.utils import timezone
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    is_active = models.BooleanField(default=False)
    phone_number = models.CharField(
        max_length=15,
        blank=False,
        null=False,
        verbose_name="Номер телефона",
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Введите корректный номер (до 15 цифр, можно с +)"
            )
        ],
        error_messages={
            'blank': 'Пожалуйста, укажите номер телефона',
            'null': 'Номер телефона не может быть пустым'
        }
    )
    email = models.EmailField(unique=True, null=False)
    verification_code = models.CharField(max_length=6, null=True, blank=True)
    code_expires = models.DateTimeField(null=True, blank=True)

    def generate_verification_code(self):
        self.verification_code = str(random.randint(100000, 999999))
        self.code_expires = timezone.now() + timedelta(minutes=5)

    def is_code_valid(self, code):
        return (
            self.verification_code == code
            and self.code_expires > timezone.now()
        )

    def __str__(self):
        return self.username



class OrganizationData(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    name_organ = models.CharField(
        'Название организации',
        max_length=200,
        default='Не указано',
        blank=False,
        null=False
    )
    prav_form = models.CharField(
        'Правовая форма',
        max_length=3,
        choices=[
            ('ooo', 'ООО'),
            ('ip', 'ИП'),
        ],
        blank=False,
        default='ooo',
        null=False
    )
    inn = models.CharField(
        'ИНН',
        max_length=12,
        blank=False,
        null=False
    )
    kpp = models.CharField(
        'КПП',
        max_length=9,
        blank=True,
        null=True
    )
    ogrn = models.CharField(
        'ОГРН',
        max_length=15,
        default='000000000000000',
        blank=False,
        null=False
    )
    address = models.TextField(
        'Адрес',
        default='Не указан',
        blank=False,
        null=False
    )

    # Новые поля для банковских реквизитов
    bik = models.CharField(
        'БИК',
        max_length=9,
        help_text='Банковский идентификационный код (9 цифр)',
        blank=True,
        null=True
    )
    bank_name = models.CharField(
        'Наименование банка',
        max_length=100,
        help_text='Полное наименование банка',
        blank=True,
        null=True
    )
    correspondent_account = models.CharField(
        'Номер корсчёта',
        max_length=20,
        help_text='Корреспондентский счёт банка (20 цифр)',
        blank=True,
        null=True
    )
    checking_account = models.CharField(
        'Номер расчётного счёта',
        max_length=20,
        help_text='Расчётный счёт организации (20 цифр)',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name_organ

    class Meta:
        verbose_name = 'Данные организации'
        verbose_name_plural = 'Данные организаций'
