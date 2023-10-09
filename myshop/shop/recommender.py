import redis
from django.conf import settings

from .models import Product

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

MAX_SUGGESTIONS = 6


class Recommender():
    def get_product_key(self, id):
        return f'product:{id}:purchased_with'

    def products_bought(self, products):
        product_ids = [product.id for product in products]
        for product_id in product_ids:
            for with_id in product_ids:
                if product_id != with_id:
                    r.zincrby(
                        self.get_product_key(product_id), 1, with_id
                    )

    def suggest_products_for(self, products, max_results=MAX_SUGGESTIONS):
        product_ids = [product.id for product in products]
        if len(products) == 1:
            suggestions = r.zrange(
                name=self.get_product_key(product_ids[0]),
                start=0,
                end=-1,
                desc=True
            )[:max_results]
        else:
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = f'tmp_{flat_ids}'
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)
            r.zrem(tmp_key, *product_ids)
            suggestions = r.zrange(
                name=tmp_key,
                start=0,
                end=-1,
                desc=True
            )[:max_results]
            r.delete(tmp_key)
        suggestions_ids = [int(id) for id in suggestions]
        suggestions_products = list(
            Product.objects.filter(id_in=suggestions_ids)
        )
        suggestions_products.sort(key=lambda x: suggestions_ids.index(x.id))
        return suggestions_products

    def clear_purchases(self):
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))
