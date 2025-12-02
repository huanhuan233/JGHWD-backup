from rest_framework.routers import DefaultRouter
from .views import OutlineViewSet

router = DefaultRouter()
router.register(r'outlines', OutlineViewSet)

urlpatterns = router.urls
