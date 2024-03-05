import redis
from django.conf import settings

from .models import Product


r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)

class Recommender:
    def get_product_key(self, id): # Создает и возвращает ключ для хранения информации о покупках товара с определенным идентификатором. Вероятно, этот ключ используется для доступа к соответствующей записи в Redis.
        return f'product:{id}:purchased_with'
    
    def products_bought(self, products): # Метод, который регистрирует информацию о покупках, основываясь на списке продуктов.
        product_ids = [p.id for p in products] # Создает список идентификаторов продуктов из переданного списка.
        for product_id in product_ids: # Для каждого продукта в списке продуктов выполняется следующий блок.
            for with_id in product_ids: # Для каждого продукта в списке продуктов выполняется вложенный цикл. Этот цикл используется для обработки связей между парами продуктов.
                if product_id != with_id: # Проверяет, чтобы не учитывать покупки продукта самого себя
                    r.zincrby(self.get_product_key(product_id), 1, with_id) # Использует метод zincrby Redis для увеличения значения связанного продукта в сортированном множестве для данного продукта (product_id). Значение увеличивается на 1 для продукта, с которым был совершен покупка (with_id).

    def suggest_products_for(self, products, max_results=6): # Метод, предлагающий похожие продукты на основе истории покупок.
        product_ids = [p.id for p in products] # Создает список идентификаторов продуктов из переданного списка.
        if len(products) == 1: # Если в списке продуктов только один продукт, используется история его покупок для предложения похожих продуктов.
            suggestions = r.zrange(self.get_product_key(product_ids[0]), 0, -1, desc=True)[:max_results] # Используется метод zrange Redis для получения отсортированного списка похожих продуктов на основе истории покупок данного продукта. Возвращается указанное количество (max_results) результатов.
        else: # Если в списке продуктов больше одного, создается временный ключ для хранения объединенного множества Redis.
            flat_ids = ''.join([str(id) for id in product_ids]) # Создает строку, объединяя идентификаторы продуктов в одну строку.
            tmp_key = f'tmp_{flat_ids}' #Формирует имя временного ключа.
            keys = [self.get_product_key(id) for id in product_ids] # Создает список ключей Redis для каждого продукта.
            r.zunionstore(tmp_key, keys) # Использует метод zunionstore Redis для объединения множеств ключей во временное множество.
            r.zrem(tmp_key, *product_ids) # Удаляет из временного множества ключи продуктов, присутствующие в списке продуктов.
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results] # Получает отсортированный список похожих продуктов из временного множества.
            r.delete(tmp_key) # Удаляет временное множество из Redis.
        suggested_products_ids = [int(id) for id in suggestions] # Преобразует идентификаторы продуктов из строкового формата в целые числа.
        suggested_products = list(Product.objects.filter( 
            id__in=suggested_products_ids
        )) # Получает объекты продуктов, соответствующие идентификаторам из результата Redis.
        suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id)) # Сортирует полученные продукты в порядке, соответствующему порядку идентификаторов в результатах Redis.
        return suggested_products # Возвращает отсортированный список похожих продуктов.
    
    def clear_purchases(self): # Метод, очищающий историю покупок для всех продуктов.
        for id in Product.objects.values_list('id', flat=True): # Итерируется по списку идентификаторов всех продуктов в базе данных.
            r.delete(self.get_product_key(id)) # Удаляет ключи, соответствующие истории покупок для каждого продукта из Redis.
