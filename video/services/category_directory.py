from django.db.models import Q

from video.models import Category


CATEGORY_DIRECTORY_QUERY_MAX_LENGTH = 120
CATEGORY_DIRECTORY_SORTS = {
    "name": ("name", "pk"),
    "name_desc": ("-name", "-pk"),
}


def get_category_directory(requested_query="", requested_sort="name"):
    selected_query = str(requested_query or "").strip()[:CATEGORY_DIRECTORY_QUERY_MAX_LENGTH]
    selected_sort = str(requested_sort or "").strip().lower()
    if selected_sort not in CATEGORY_DIRECTORY_SORTS:
        selected_sort = "name"

    categories = Category.objects.all()
    if selected_query:
        categories = categories.filter(
            Q(name__icontains=selected_query)
            | Q(description__icontains=selected_query)
        )

    return categories.order_by(*CATEGORY_DIRECTORY_SORTS[selected_sort]), selected_query, selected_sort
