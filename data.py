import os
import django
from datetime import datetime, timedelta

# Налаштовуємо оточення Django (якщо папка з settings називається не config, зміни на свою)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from airport.models import AirplaneType, Airplane, Crew, Airport, Route, Flight, Order, Ticket

User = get_user_model()

def main():
    print("🚀 Запуск повного заповнення бази даних...")

    # 1. СТВОРЕННЯ КОРИСТУВАЧІВ
    admin, created = User.objects.get_or_create(
        email="admin@airport.com",
        defaults={"is_staff": True, "is_superuser": True}
    )
    if created:
        admin.set_password("admin123")
        admin.save()
        print("— Створено admіна: admin@airport.com (пароль: admin123)")

    passenger, created = User.objects.get_or_create(
        email="passenger@gmail.com",
        defaults={"first_name": "Ivan", "last_name": "Ivanov"}
    )
    if created:
        passenger.set_password("passenger123")
        passenger.save()
        print("— Створено пасажира: passenger@gmail.com (пароль: passenger123)")


    # 2. СТВОРЕННЯ ЕКІПАЖУ (Crew)
    pilot1, _ = Crew.objects.get_or_create(first_name="John", last_name="Doe", role=Crew.RoleChoices.PILOT)
    pilot2, _ = Crew.objects.get_or_create(first_name="Alex", last_name="Smith", role=Crew.RoleChoices.PILOT)
    stewardess, _ = Crew.objects.get_or_create(first_name="Anna", last_name="Jane", role=Crew.RoleChoices.STEWARDESS)
    steward, _ = Crew.objects.get_or_create(first_name="Tom", last_name="Brown", role=Crew.RoleChoices.STEWARD)
    navigator, _ = Crew.objects.get_or_create(first_name="Ben", last_name="Miller", role=Crew.RoleChoices.NAVIGATOR)
    print("— Персонал успішно додано")


    # 3. СТВОРЕННЯ ТИПІВ ЛІТАКІВ ТА ЛІТАКІВ
    boeing_type, _ = AirplaneType.objects.get_or_create(name="Boeing")
    airbus_type, _ = AirplaneType.objects.get_or_create(name="Airbus")

    plane1, _ = Airplane.objects.get_or_create(
        name="Boeing 737", rows=20, seats_in_row=6, airplane_type=boeing_type
    )
    plane2, _ = Airplane.objects.get_or_create(
        name="Airbus A320", rows=18, seats_in_row=6, airplane_type=airbus_type
    )
    print("— Літаки додано до ангару")


    # 4. СТВОРЕННЯ АЕРОПОРТІВ (ОНОВЛЕНО: Додано унікальні коди IATA)
    # Тепер get_or_create шукає по унікальному коду, а решту полів додає у defaults
    kbp, _ = Airport.objects.get_or_create(
        code="KBP",
        defaults={"name": "Boryspil", "country": "Ukraine", "city": "Kyiv"}
    )
    lhr, _ = Airport.objects.get_or_create(
        code="LHR",
        defaults={"name": "Heathrow", "country": "United Kingdom", "city": "London"}
    )
    jfk, _ = Airport.objects.get_or_create(
        code="JFK",
        defaults={"name": "John F. Kennedy", "country": "USA", "city": "New York"}
    )
    print("— Аеропорти побудовано (з кодами KBP, LHR, JFK)")


    # 5. СТВОРЕННЯ МАРШРУТІВ (Routes)
    route1, _ = Route.objects.get_or_create(source=kbp, destination=lhr, distance=2500)
    route2, _ = Route.objects.get_or_create(source=lhr, destination=jfk, distance=5500)
    print("— Маршрути прокладено")


    # 6. СТВОРЕННЯ РЕЙСІВ (Flights)
    now = timezone.now()

    # Рейс 1: Київ -> Лондон (виліт завтра)
    flight1, _ = Flight.objects.get_or_create(
        route=route1,
        airplane=plane2,
        departure_time=now + timedelta(days=1, hours=2),
        arrival_time=now + timedelta(days=1, hours=5),
    )
    flight1.crew.set([pilot1, stewardess, steward]) # Призначаємо екіпаж

    # Рейс 2: Лондон -> Нью-Йорк (виліт післязавтра)
    flight2, _ = Flight.objects.get_or_create(
        route=route2,
        airplane=plane1,
        departure_time=now + timedelta(days=2, hours=10),
        arrival_time=now + timedelta(days=2, hours=18),
    )
    flight2.crew.set([pilot2, stewardess, navigator])
    print("— Рейси сформовано та укомплектовано екіпажем")


    # 7. СТВОРЕННЯ ЗАМОВЛЕНЬ ТА КВИТКІВ
    order, _ = Order.objects.get_or_create(user=passenger)

    # Купуємо квитки пасажиру на Рейс 1 (Ряд 1 Місце 1, та Ряд 1 Місце 2)
    Ticket.objects.get_or_create(row=1, seat=1, flight=flight1, order=order)
    Ticket.objects.get_or_create(row=1, seat=2, flight=flight1, order=order)

    # Купуємо квиток на Рейс 2 (Ряд 5 Місце 3)
    Ticket.objects.get_or_create(row=5, seat=3, flight=flight2, order=order)
    print("— Продано перші тестові квитки")

    print("\n🎉 ВСЕ ГОТОВО! База даних заповнена на 100%. Можна запускати сервер!")

if __name__ == '__main__':
    main()