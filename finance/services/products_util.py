


from finance.models import Product


def get_suggested_products_util(ufhs_score):
    products = Product.objects.filter(ufhs_tag__gte=int(ufhs_score))
    return products
