from django.conf.urls import *

from rest_framework.routers import DefaultRouter

from open_municipio.api.acts import DeliberationViewSet, CGDeliberationViewSet
from open_municipio.api.people import PersonViewSet

router = DefaultRouter()
# acts
router.register(r'deliberations', DeliberationViewSet)
router.register(r'cgdeliberations', CGDeliberationViewSet)

# people
router.register(r'people', PersonViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)
