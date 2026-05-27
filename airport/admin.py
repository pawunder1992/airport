from django.contrib import admin
from .models import Airport, Airplane, AirplaneType, Crew, Ticket, Flight, Order, Route


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketInline]


admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Crew)
admin.site.register(Flight)
admin.site.register(Route)
