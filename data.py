import os
import django
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from airport.models import (
    AirplaneType,
    Airplane,
    Crew,
    Airport,
    Route,
    Flight,
    Order,
    Ticket,
)

User = get_user_model()


def main():

    admin, created = User.objects.get_or_create(
        email="admin@airport.com",
        defaults={"is_staff": True, "is_superuser": True},
    )
    if created:
        admin.set_password("password123456789")
        admin.save()
        print("Admin admin@airport.com (password: password123456789)")

    passenger, created = User.objects.get_or_create(
        email="passenger@gmail.com",
        defaults={"first_name": "Ivan", "last_name": "Ivanov"},
    )
    if created:
        passenger.set_password("password123456789")
        passenger.save()
        print("— Passenger: passenger@gmail.com (password: password123456789)")

    pilot1, _ = Crew.objects.get_or_create(
        first_name="John", last_name="Doe", role=Crew.RoleChoices.PILOT
    )
    pilot2, _ = Crew.objects.get_or_create(
        first_name="Alex", last_name="Smith", role=Crew.RoleChoices.PILOT
    )
    stewardess, _ = Crew.objects.get_or_create(
        first_name="Anna", last_name="Jane", role=Crew.RoleChoices.STEWARDESS
    )
    steward, _ = Crew.objects.get_or_create(
        first_name="Tom", last_name="Brown", role=Crew.RoleChoices.STEWARD
    )
    navigator, _ = Crew.objects.get_or_create(
        first_name="Ben", last_name="Miller", role=Crew.RoleChoices.NAVIGATOR
    )

    boeing_type, _ = AirplaneType.objects.get_or_create(name="Boeing")
    airbus_type, _ = AirplaneType.objects.get_or_create(name="Airbus")

    plane1, _ = Airplane.objects.get_or_create(
        name="Boeing 737", rows=20, seats_in_row=6, airplane_type=boeing_type
    )
    plane2, _ = Airplane.objects.get_or_create(
        name="Airbus A320", rows=18, seats_in_row=6, airplane_type=airbus_type
    )

    kbp, _ = Airport.objects.get_or_create(
        code="KBP",
        defaults={"name": "Boryspil", "country": "Ukraine", "city": "Kyiv"},
    )
    lhr, _ = Airport.objects.get_or_create(
        code="LHR",
        defaults={
            "name": "Heathrow",
            "country": "United Kingdom",
            "city": "London",
        },
    )
    jfk, _ = Airport.objects.get_or_create(
        code="JFK",
        defaults={
            "name": "John F. Kennedy",
            "country": "USA",
            "city": "New York",
        },
    )

    route1, _ = Route.objects.get_or_create(
        source=kbp, destination=lhr, distance=2500
    )
    route2, _ = Route.objects.get_or_create(
        source=lhr, destination=jfk, distance=5500
    )

    now = timezone.now()

    flight1, _ = Flight.objects.get_or_create(
        route=route1,
        airplane=plane2,
        departure_time=now + timedelta(days=1, hours=2),
        arrival_time=now + timedelta(days=1, hours=5),
    )
    flight1.crew.set([pilot1, stewardess, steward])

    flight2, _ = Flight.objects.get_or_create(
        route=route2,
        airplane=plane1,
        departure_time=now + timedelta(days=2, hours=10),
        arrival_time=now + timedelta(days=2, hours=18),
    )
    flight2.crew.set([pilot2, stewardess, navigator])

    order, _ = Order.objects.get_or_create(user=passenger)

    Ticket.objects.get_or_create(row=1, seat="A", flight=flight1, order=order)
    Ticket.objects.get_or_create(row=1, seat="B", flight=flight1, order=order)

    Ticket.objects.get_or_create(row=5, seat="C", flight=flight2, order=order)

    print("\n🎉 Test data is created")


if __name__ == "__main__":
    main()
