from django.urls import path, include
from rest_framework.routers import DefaultRouter

from airport.views import AirplaneTypeViewSet

app_name = "airport"

router = DefaultRouter()



router.register("airplane-types", AirplaneTypeViewSet)


urlpatterns = [
    path("", include(router.urls)),

]