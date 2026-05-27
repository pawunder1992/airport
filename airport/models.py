from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from django.template.defaultfilters import slugify
from config import settings
import string
import pathlib
import uuid




class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Crew(models.Model):
    class RoleChoices(models.TextChoices):
        PILOT = "pilot", "Pilot"
        STEWARDESS = "stewardess", "Stewardess"
        STEWARD = "steward", "Steward"
        NAVIGATOR = "navigator", "Navigator"
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=20,
        choices=RoleChoices.choices
    )

    def __str__(self):
        return f"{self.get_role_display()}: {self.first_name} {self.last_name}"



class Airport(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["name", "city"], name="unique_name_city")
        ]

    def __str__(self):
        return f"{self.name}({self.code}) : {self.country}/{self.city}"

def plane_image_path(instance: "Airplane", filename: str):
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}" + pathlib.Path(filename).suffix
    return pathlib.Path("upload/planes/") / pathlib.Path(filename)

class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE, related_name="airplanes")
    image = models.ImageField(null=True, upload_to=plane_image_path)

    @property
    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name





class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departure_routes")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrival_routes")
    distance = models.PositiveIntegerField()

    @staticmethod
    def validate_destination(source, destination, error_to_raise):
        if source == destination:
            raise error_to_raise("destination can`t be same as source")

    def clean(self):
        Route.validate_destination(self.source, self.destination, ValidationError)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.source.city}({self.source.code}) -> {self.destination.city}({self.destination.code})"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)

    @staticmethod
    def validate_flight_time(departure_time, arrival_time, error_to_raise):
        if departure_time > arrival_time:
            raise error_to_raise("departure_time can`t be greater than arrival_time")
        if departure_time < timezone.now():
            raise error_to_raise("Departure time can't be less than current time (in the past).")


    def clean(self):
        Flight.validate_flight_time(self.departure_time, self.arrival_time, ValidationError)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.route.source.city} > {self.route.destination.city} ({self.departure_time} - {self.arrival_time})"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    class Meta:
        ordering = ["created_at"]


    def __str__(self):
        return f"Order #{self.id} by {self.user.email} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"



class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.CharField(max_length=1)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["flight", "row", "seat"], name="unique_ticket_flight")
        ]
        ordering = ["row", "seat"]

    @staticmethod
    def validate_seat(seat, airplane_seats, error_to_raise):
        alphabet = string.ascii_uppercase
        if seat not in alphabet[:airplane_seats]:
            raise error_to_raise({"seat": f"seat must be a letter in range [A, {alphabet[airplane_seats-1]}], not {seat}"})
    @staticmethod
    def validate_row(row, airplane_rows, error_to_raise):
        if not (1 <= row <= airplane_rows):
            raise error_to_raise({"row": f"row must be in range [1, {airplane_rows}], not {row}"})

    def clean(self):
        Ticket.validate_seat(self.seat, self.flight.airplane.seats_in_row, ValueError)
        Ticket.validate_row(self.row, self.flight.airplane.rows, ValueError)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.full_clean()
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields
        )

    def __str__(self):
        return f"Row: {self.row}, Seat: {self.seat}"
