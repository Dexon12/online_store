from django import forms
from django.utils.translation import gettext_lazy as _ # What a difference between gettext_laty and gettext? Gettext вполняется(переводит текст) немедленно во время выполнения кода, а gettext_lazy также переводит текст но в момент когда нужно получить конкретную строку с переводом, это нужно для улучшения производительности

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int, label=_('Quantity')) #  choices мы получаем список из 20 чисел, мы создали выпадающий список и таким образом выбираем сколько будет такого товара в корзине
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput) # олжно ли выбранное количество заменить текущее
