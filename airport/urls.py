from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airport.views import AirplaneTypeViewSet, CrewViewSet, AirportViewSet, AirplaneViewSet

app_name = "airport"

router = DefaultRouter()

router.register("airplane-types", AirplaneTypeViewSet)
router.register("crew", CrewViewSet)
router.register("airports", AirportViewSet)
router.register("airplanes", AirplaneViewSet)

urlpatterns = [
    path("", include(router.urls)),

]