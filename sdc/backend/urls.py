from rest_framework import routers
from .views import ProductViewSet, RecipeQueryViewSet


router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'recipes', RecipeQueryViewSet)
