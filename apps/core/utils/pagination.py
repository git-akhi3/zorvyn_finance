from rest_framework import pagination

from apps.core.utils.api_response import ApiResponse


class Pagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return ApiResponse(
            data={
                "page": self.page.number,
                "page_size": self.page.paginator.per_page,
                "total_pages": self.page.paginator.num_pages,
                "total_items": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


def paginate_queryset(queryset, request, serializer_class=None):
    paginator = Pagination()
    page = paginator.paginate_queryset(queryset, request)

    if page is None:
        items = serializer_class(queryset, many=True).data if serializer_class else list(queryset)
        return {
            "page": 1,
            "page_size": len(items),
            "total_pages": 1,
            "total_items": len(items),
            "next": None,
            "previous": None,
            "results": items,
        }

    results = serializer_class(page, many=True).data if serializer_class else list(page)
    return {
        "page": paginator.page.number,
        "page_size": paginator.page.paginator.per_page,
        "total_pages": paginator.page.paginator.num_pages,
        "total_items": paginator.page.paginator.count,
        "next": paginator.get_next_link(),
        "previous": paginator.get_previous_link(),
        "results": results,
    }
