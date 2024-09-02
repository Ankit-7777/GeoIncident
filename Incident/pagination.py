from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MyPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page_size'
    page_size_query_param = 'records'
    max_page_size = 100
    last_page_strings = ['end']
    
    def get_paginated_response(self, data):
        next_link = self.get_next_link()
        previous_link = self.get_previous_link()
        return Response({
            'next': next_link,
            'previous': previous_link,
            'count': self.page.paginator.count,
            'results': data
        })
