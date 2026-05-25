from rest_framework import serializers

from airport.models import AirplaneType, Crew, Airport, Airplane


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
        fields = ("id", "name", "country", "city")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")