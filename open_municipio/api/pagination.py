from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):

    page_size = 50
    page_size_query_param = "page_limit"
    max_page_size = 50
