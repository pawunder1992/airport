import json
from datetime import datetime, timedelta

def main():
    print("🚀 Генерація JSON-даних для бази даних...")

    # Допоміжна функція для форматування дати/часу для JSON
    now = datetime.now()
    def format_dt(dt):
        return dt.isoformat()

    # Створення структури даних
    data = {
        "users": [
            {
                "email": "admin@airport.com",
                "is_staff": True,
                "is_superuser": True,
                "password": "password123456789"
            },
            {
                "email": "passenger@gmail.com",
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "password": "password123456789"
            }
        ],
        "crew": [
            {"first_name": "John", "last_name": "Doe", "role": "PILOT"},
            {"first_name": "Alex", "last_name": "Smith", "role": "PILOT"},
            {"first_name": "Anna", "last_name": "Jane", "role": "STEWARDESS"},
            {"first_name": "Tom", "last_name": "Brown", "role": "STEWARD"},
            {"first_name": "Ben", "last_name": "Miller", "role": "NAVIGATOR"}
        ],
        "airplanes": [
            {"name": "Boeing 737", "rows": 20, "seats_in_row": 6, "type": "Boeing"},
            {"name": "Airbus A320", "rows": 18, "seats_in_row": 6, "type": "Airbus"}
        ],
        "airports": [
            {"code": "KBP", "name": "Boryspil", "country": "Ukraine", "city": "Kyiv"},
            {"code": "LHR", "name": "Heathrow", "country": "United Kingdom", "city": "London"},
            {"code": "JFK", "name": "John F. Kennedy", "country": "USA", "city": "New York"}
        ],
        "routes": [
            {"source": "KBP", "destination": "LHR", "distance": 2500},
            {"source": "LHR", "destination": "JFK", "distance": 5500}
        ],
        "flights": [
            {
                "route": {"source": "KBP", "destination": "LHR"},
                "airplane": "Airbus A320",
                "departure_time": format_dt(now + timedelta(days=1, hours=2)),
                "arrival_time": format_dt(now + timedelta(days=1, hours=5)),
                "crew": ["John Doe", "Anna Jane", "Tom Brown"]
            },
            {
                "route": {"source": "LHR", "destination": "JFK"},
                "airplane": "Boeing 737",
                "departure_time": format_dt(now + timedelta(days=2, hours=10)),
                "arrival_time": format_dt(now + timedelta(days=2, hours=18)),
                "crew": ["Alex Smith", "Anna Jane", "Ben Miller"]
            }
        ],
        "tickets": [
            {"user": "passenger@gmail.com", "flight_route": ["KBP", "LHR"], "row": 1, "seat": "A"},
            {"user": "passenger@gmail.com", "flight_route": ["KBP", "LHR"], "row": 1, "seat": "B"},
            {"user": "passenger@gmail.com", "flight_route": ["LHR", "JFK"], "row": 5, "seat": "C"}
        ]
    }

    # Запис у файл
    with open('initial_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print("— Файл 'initial_data.json' успішно створено!")

if __name__ == '__main__':
    main()