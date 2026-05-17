from django.urls import path
from .ui_views import (
    CategoryListView,
    CategoryCreateView,
    CategoryUpdateView
)


urlpatterns = [
    path("categories/", CategoryListView.as_view()),
    path("categories/create/", CategoryCreateView.as_view()),
    path("categories/<int:id>/edit/", CategoryUpdateView.as_view()),
]

