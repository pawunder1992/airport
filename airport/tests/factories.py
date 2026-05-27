import string
import factory
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from airport.models import (
    AirplaneType,
    Crew,
    Airport,
    Airplane,
    Route,
    Flight,
    Order,
    Ticket,
)

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@airport.com")
    password = "password123"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class AirplaneTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AirplaneType

    name = factory.Sequence(lambda n: f"Type-{n}")


class CrewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Crew

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    role = factory.Iterator([Crew.RoleChoices.PILOT, Crew.RoleChoices.STEWARDESS])


class AirportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Airport

    code = factory.Sequence(lambda n: f"A{n:02d}"[:3].upper())
    name = factory.Sequence(lambda n: f"Airport International {n}")
    country = factory.Faker("country")
    city = factory.Sequence(lambda n: f"City {n}")


class AirplaneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Airplane

    name = factory.Sequence(lambda n: f"Boeing {n}")
    rows = 20
    seats_in_row = 6
    airplane_type = factory.SubFactory(AirplaneTypeFactory)
    image = None


class RouteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Route

    source = factory.SubFactory(AirportFactory)
    destination = factory.SubFactory(AirportFactory)
    distance = factory.Faker("random_int", min=300, max=5000)


class FlightFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Flight

    route = factory.SubFactory(RouteFactory)
    airplane = factory.SubFactory(AirplaneFactory)
    departure_time = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=2))
    arrival_time = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=5))

    @factory.post_generation
    def crew(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for member in extracted:
                self.crew.add(member)
        else:
            self.crew.add(CrewFactory(role=Crew.RoleChoices.PILOT))


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ticket
    row = factory.Sequence(lambda n: n + 1)
    seat = "A"

    flight = factory.SubFactory(FlightFactory)
    order = factory.SubFactory(OrderFactory)