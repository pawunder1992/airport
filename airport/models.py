from django.db import models

from config import settings


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



class AirplaneType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=100)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE, related_name="airplanes")


    def __str__(self):
        return self.name


class Airport(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)


    def __str__(self):
        return f"{self.name} : {self.country}/{self.city}"


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departure_routes")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrival_routes")
    distance = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.source.city} -> {self.destination.city} ({self.distance} km)"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="flights")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew)


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
    seat = models.PositiveIntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["flight", "row", "seat"], name="unique_ticket_flight")
        ]
        ordering = ["row", "seat"]


    def __str__(self):
        return f"Ticket #{self.id} [Flight {self.flight_id}] - Row: {self.row}, Seat: {self.seat}"
