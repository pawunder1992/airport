from django.db.models import F, Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from airport.models import AirplaneType, Crew, Airport, Airplane, Route, Flight, Order
from airport.serializers import AirplaneTypeSerializer, CrewSerializer, AirportSerializer, AirplaneSerializer, \
    AirplaneListSerializer, AirplaneRetrieveSerializer, RouteSerializer, RouteListSerializer, RouteRetrieveSerializer, \
    FlightSerializer, FlightListSerializer, FlightRetrieveSerializer, OrderSerializer, OrderListSerializer, \
    OrderRetrieveSerializer


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


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return FlightListSerializer
        elif self.action == 'retrieve':
            return FlightRetrieveSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            source_city = self.request.query_params.get('source_city')
            destination_city = self.request.query_params.get('destination_city')
            date = self.request.query_params.get('date')
            available = self.request.query_params.get('available')
            if source_city:
                queryset = queryset.filter(route__source__city__icontains=source_city)
            if destination_city:
                queryset = queryset.filter(route__destination__city__icontains=destination_city)
            if date:
                queryset = queryset.filter(departure_time__date=date)

            queryset = queryset.select_related(
                "route__source",
                "route__destination",
                "airplane"
            ).annotate(
                total_seats=F("airplane__rows") * F("airplane__seats_in_row"),
                tickets_available=F("total_seats") - Count("tickets")
            )
            if available and available.lower() == "true":
                queryset = queryset.filter(tickets_available__gt=0)


        if self.action == "retrieve":
            queryset = queryset.select_related(
                "route__source",
                "route__destination",
                "airplane__airplane_type"
            ).prefetch_related("crew", "tickets")

        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related(
                "tickets__flight__airplane",
                "tickets__flight__route__source",
                "tickets__flight__route__destination",
            )
        return queryset


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        if self.action in ("retrieve", "update", "partial_update"):
            return OrderRetrieveSerializer

        return self.serializer_class
