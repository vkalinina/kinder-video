from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Category
from .serializers import CategorySerializer


class CategoryListView(ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(owner=self.request.user, is_active=True)
