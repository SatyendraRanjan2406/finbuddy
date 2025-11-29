from django.db.models import Q
from rapidfuzz import fuzz, process
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from .pagination import ProductPagination
from rest_framework.views import APIView


# 1. Search by Category + Name (Paginated)
# /api/products/search/?category=Loan&name=pm
class ProductSearchByCategoryName(APIView):
    def get(self, request):
        category = request.GET.get("category", "")
        name = request.GET.get("name", "")

        products = Product.objects.all()

        if category:
            products = products.filter(category__icontains=category)

        if name:
            products = products.filter(name__icontains=name)

        products = products.order_by("id")

        paginator = ProductPagination()
        paginated = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(paginated, many=True)

        return paginator.get_paginated_response(serializer.data)


"""
2. Advanced Search (Name + Purpose + Description)
/api/products/advanced-search/?q=farmer loan

Search across:

name

purpose

scheme_description
"""
class ProductAdvancedSearch(APIView):
    def get(self, request):
        query = request.GET.get("q", "")

        if not query:
            return Response({"message": "Query param 'q' required"}, status=400)

        # Search across 3 fields
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(purpose__icontains=query) |
            Q(scheme_description__icontains=query)
        ).order_by("id")

        paginator = ProductPagination()
        paginated = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)



"""
3. Fuzzy Search (Typo-Tolerant)
/api/products/fuzzy/?q=svanidi

(works even if user makes mistakes)
"""

class ProductFuzzySearch(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip()

        if not query:
            return Response({"message": "Query param 'q' required"}, status=400)

        all_products = Product.objects.all()

        # Mapping: name → id
        name_to_id = {p.name: p.id for p in all_products}

        # Provide only names (strings) to RapidFuzz
        choices = list(name_to_id.keys())

        best_matches = process.extract(
            query,
            choices,
            scorer=fuzz.WRatio,
            limit=50
        )

        # extract returns: [(matched_name, score, index)]
        matched_ids = [
            name_to_id[match[0]]   # match[0] = product name
            for match in best_matches
            if match[1] > 30        # threshold
        ]

        products = Product.objects.filter(id__in=matched_ids).order_by("id")

        paginator = ProductPagination()
        paginated = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)



"""
4. Elasticsearch-Style Suggestion API
/api/products/suggest/?q=pm

Returns top 10 autocomplete suggestions.
"""

class ProductSuggestion(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip()

        if not query:
            return Response({"suggestions": []})

        suggestions = (
            Product.objects.filter(name__istartswith=query)
            .values_list("name", flat=True)
            .distinct()[:10]
        )

        return Response({"suggestions": list(suggestions)})
