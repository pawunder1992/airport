from rest_framework import viewsets

from airport.models import AirplaneType, Crew, Airport, Airplane, Route
from airport.serializers import AirplaneTypeSerializer, CrewSerializer, AirportSerializer, AirplaneSerializer, \
    AirplaneListSerializer, AirplaneRetrieveSerializer, RouteSerializer, RouteListSerializer, RouteRetrieveSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer



    def get_serializer_class(self):
        if self.action == 'list':

            return AirplaneListSerializer

        elif self.action == 'retrieve':
            return AirplaneRetrieveSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset
        airplane_type = self.request.query_params.get('airplane_type')
        if airplane_type:

            queryset = queryset.filter(airplane_type__id=airplane_type)

        if self.action in ('list', "retrieve"):
            return queryset.select_related("airplane_type")
        return queryset


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


    def get_serializer_class(self):
        if self.action == 'list':
            return RouteListSerializer
        elif self.action == 'retrieve':
            return RouteRetrieveSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset
        source_city = self.request.query_params.get('source_city')
        destination_city = self.request.query_params.get('destination_city')

        if source_city:
            queryset = queryset.filter(source__city__icontains=source_city)
        if destination_city:
            queryset = queryset.filter(destination__city__icontains=destination_city)

        if self.action in ('list', "retrieve"):
            return queryset.select_related("source", "destination")
        return queryset
