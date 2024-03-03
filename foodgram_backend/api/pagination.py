from users import quantity as q
from rest_framework.pagination import PageNumberPagination


class LimitedPagePagination(PageNumberPagination):
    page_size = q.PAGINATION_PAGE_SIZE
    page_size_query_param = "limit"
