from django.urls import path, include
from rest_framework import routers
from catalog.views import CategoryListView

app_name = "catalog"
urlpatterns = [
    path(
        "categories/",
        CategoryListView.as_view(),
        name="category-list"
    ),
]
