from rest_framework import viewsets

from airport.models import AirplaneType, Crew, Airport, Airplane
from airport.serializers import AirplaneTypeSerializer, CrewSerializer, AirportSerializer, AirplaneSerializer, \
    AirplaneListSerializer, AirplaneRetrieveSerializer


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




    def get_serializer_class(self):
        if self.action == 'list':

            return AirplaneListSerializer

        elif self.action == 'retrieve':
            return AirplaneRetrieveSerializer
        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        airplane_type = self.request.query_params.get('airplane_type')
        if airplane_type:

            queryset = queryset.filter(airplane_type__id=airplane_type)

        if self.action in ('list', "retrieve"):
            return queryset.select_related("airplane_type")
        return queryset