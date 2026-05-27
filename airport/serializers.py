from django.db import transaction
from rest_framework import serializers

from airport.models import AirplaneType, Crew, Airport, Airplane, Route, Flight, Ticket, Order


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class CrewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "role")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "code", "name", "country", "city")


class AirplaneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "image")


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(source="airplane_type.name", read_only=True)
    class Meta:
        model = Airplane
        fields = ("id", "name", "capacity", "airplane_type", "image")


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer()


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    def validate(self, attrs):
        Route.validate_destination(attrs["source"], attrs["destination"], serializers.ValidationError)
        return attrs

class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.code", read_only=True)
    destination = serializers.CharField(source="destination.code", read_only=True)

class RouteRetrieveSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)



class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")

    def validate(self, attrs):
        Flight.validate_flight_time(attrs["departure_time"], attrs["arrival_time"], serializers.ValidationError)
        return attrs


class FlightListSerializer(FlightSerializer):
    departure_time = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    arrival_time = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    route = serializers.CharField(source="route.__str__", read_only=True)
    airplane = serializers.CharField(source="airplane.name", read_only=True)
    total_seats = serializers.IntegerField(read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)
    crew = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "total_seats", "departure_time", "arrival_time", "tickets_available", "crew")

class FlightRetrieveSerializer(FlightSerializer):
    departure_time = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    arrival_time = serializers.DateTimeField(format="%d-%m-%Y %H:%M")
    route = RouteRetrieveSerializer(read_only=True)
    airplane = AirplaneRetrieveSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)
    taken_seats = serializers.StringRelatedField(
        many=True,
        read_only=True,
        source="tickets",
    )

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew", "taken_seats")

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")

    def validate(self, attrs):
        Ticket.validate_seat(attrs["seat"], attrs["flight"].airplane.seats_in_row, serializers.ValidationError)
        Ticket.validate_row(attrs["row"], attrs["flight"].airplane.rows, serializers.ValidationError)
        return attrs


class TicketListSerializer(TicketSerializer):

    flight = serializers.CharField(source="flight.route.__str__", read_only=True)
    class Meta:
        model = Ticket
        fields = ("row", "seat", "flight")

class TicketRetrieveSerializer(TicketSerializer):
    flight = FlightListSerializer(read_only=True)



class OrderSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    tickets = TicketSerializer(many=True, allow_empty=False)
    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order

class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

class OrderRetrieveSerializer(OrderSerializer):
    tickets = TicketRetrieveSerializer(many=True, read_only=True)