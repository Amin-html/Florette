from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review, Flower, Category


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'
        self.fields['username'].widget.attrs['placeholder'] = 'Имя пользователя'
        self.fields['password1'].widget.attrs['placeholder'] = 'Пароль'
        self.fields['password2'].widget.attrs['placeholder'] = 'Повторите пароль'


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-input'}),
            'text': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Поделитесь впечатлением...'}),
        }
        labels = {
            'rating': 'Оценка',
            'text': 'Ваш отзыв',
        }


class FlowerForm(forms.ModelForm):
    class Meta:
        model = Flower
        fields = ['name', 'category', 'description', 'price', 'image', 'in_stock', 'is_featured']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Название цветка'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'image': forms.FileInput(attrs={'class': 'form-input'}),
        }


class CheckoutForm(forms.Form):
    address = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Улица, дом, квартира'}),
        label='Адрес доставки'
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7 (xxx) xxx-xx-xx'}),
        label='Телефон'
    )
