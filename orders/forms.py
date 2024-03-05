from django import forms
from localflavor.us.forms import USZipCodeField

from .models import Order

class OrderCreateForm(forms.ModelForm):
    # postal_code = USZipCodeField() # Переменная должна быть такого же названия как и та переменная для которой мы устанавливаем доп. валидацию?
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']
        