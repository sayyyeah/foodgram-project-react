from rest_framework.pagination import PageNumberPagination

from users import quantity as q


class LimitedPagePagination(PageNumberPagination):
    page_size = q.PAGINATION_PAGE_SIZE
    page_size_query_param = "recipes_limit"
