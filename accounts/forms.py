from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, OrganizationData

class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number']
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Пароли не совпадают.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user



class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = get_user_model().objects.get(email=email)
            except get_user_model().DoesNotExist:
                raise forms.ValidationError('Неверный email или пароль.')

            if not user.is_active:
                raise forms.ValidationError(
                    'Аккаунт не активирован. Подтвердите телефон по SMS.'
                )

            self.user_cache = authenticate(
                self.request,
                username=user.username,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError('Неверный email или пароль.')
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data



class VerificationCodeForm(forms.Form):
    code = forms.CharField(
        label='Код подтверждения',
        max_length=6,
        widget=forms.TextInput(attrs={'placeholder': '123456'})
    )



class OrganizationDataForm(forms.ModelForm):
    class Meta:
        model = OrganizationData
        fields = [
            'name_organ',
            'prav_form',
            'inn',
            'kpp',
            'ogrn',
            'address',
        ]
        widgets = {
            'name_organ': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название организации'
            }),
            'prav_form': forms.Select(attrs={'class': 'form-control'}),
            'inn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10 или 12 цифр'
            }),
            'kpp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '9 цифр (если есть)'
            }),
            'ogrn': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '13 или 15 цифр'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Полный адрес организации'
            }),
        }
        labels = {
            'name_organ': 'Название организации',
            'prav_form': 'Правовая форма',
            'inn': 'ИНН',
            'kpp': 'КПП',
            'ogrn': 'ОГРН',
            'address': 'Адрес',
        }
        error_messages = {
            'name_organ': {'required': 'Укажите название организации'},
            'prav_form': {'required': 'Выберите правовую форму'},
            'inn': {'required': 'Введите ИНН'},
            'ogrn': {'required': 'Введите ОГРН'},
            'address': {'required': 'Укажите адрес'},
        }

class EditOrganizationDataForm(OrganizationDataForm):
    pass
