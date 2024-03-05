from decimal import Decimal
from django.conf import settings

from typing import Union

from coupons.models import Coupon
from shop.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session # retrieve session, store as attribute of instance
        cart = self.session.get(settings.CART_SESSION_ID) # ID {'cart': ...} 
        if not cart: 
            cart = self.session[settings.CART_SESSION_ID] = {} # initialize an empty cart dictionary {'cart' ...}
        self.cart = cart  # store the cart in the instance 
        self.coupon_id = self.session.get('coupon_id') # coupon_id is being encased in the instance 


    @property # property, getter, setter, deletter
    def coupon(self): # cart.coupon
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass # Зачем тут делать исключение, если мы в ином случае возвращаем None? Не зачем, но так код становиться более правильным и читаемым
        return None
    
    def get_discount(self) -> float:
        """Computes the discount"""

        if self.coupon: # Это верхнее свойство? Да
            return (self.coupon.discount / Decimal(100)) * self.get_total_price() 
        return Decimal(0)
    
    def get_total_price_after_discount(self) -> Union[int, float]:
        return self.get_total_price() - self.get_discount()

    def add(self, product, quantity=1, override_quantity=False): 
        """Add product to cart"""

        product_id = str(product.id) # python dictionary can only contain strigns as keys что делает конкретно id in product.id 
        if product_id not in self.cart: # if not, add it with the specified quantity and price если добавляем второй раз тот же продукт то условие не сработает
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)} # Хочу визуализацию
        if override_quantity: # Если исскуственно указано override_quantity
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        """Delete product from cart"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def __iter__(self): # Когда мы хотим прокрутить элементы cart вызывается магический метод __iter__
        """Itering cart`s products in cycle and get products from DB`s table"""
        products_ids = self.cart.keys() # get all product IDs from the cart
        """ Get produst`s objects and add them to cart """
        products = Product.objects.filter(id__in=products_ids) # fetch the product objects from the database using the IDs ?
        cart = self.cart.copy() # shallow copy to work with during iteration

        for product in products: # for product in cart... -> it = cart.__iter__ while True: -> it.__next__ except StopIteration: break
            cart[str(product.id)]['product'] = product # update the cart items with actual product objects (from database) | create a new key
            
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            
            yield item

    def __len__(self): # this's fired when len() method is called
        """Counting all product`s position in the cart"""
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self) -> Union[int, float]:
        """Takes the products and computes the total sum"""

        return sum(Decimal(item['price']) * item['quantity'] # price, quantity
                   for item in self.cart.values()) # {...: {item}}
    
    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()



