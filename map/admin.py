from django.contrib import admin
from .models import Location, Event
from .tasks import geocode_selected_locations


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_type', 'category', 'city', 'country', 'has_coordinates', 'created_at')
    list_filter = ('location_type', 'category', 'city', 'country', 'created_at')
    search_fields = ('name', 'address', 'city', 'country')
    readonly_fields = ('created_at', 'updated_at')
    actions = [geocode_selected_locations]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'location_type', 'category')
        }),
        ('Logo', {
            'fields': ('logo', 'logo_url'),
            'description': 'Upload image file (auto-optimized to 100x100) OR paste external URL'
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude'),
            'description': 'Leave empty to auto-geocode from address. Processing happens within 1 minute.'
        }),
        ('Address', {
            'fields': ('address', 'city', 'country'),
            'description': 'Required for auto-geocoding. Format: "Street Name Number, City, Country"'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'buyer', 'created_at', 'holder_count')
    list_filter = ('buyer', 'created_at')
    search_fields = ('name', 'description', 'buyer__name')
    filter_horizontal = ('holders',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Event Info', {
            'fields': ('name', 'description')
        }),
        ('Participants', {
            'fields': ('buyer', 'holders')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def holder_count(self, obj):
        """Display count of holders in this event."""
        return obj.holders.count()
    holder_count.short_description = 'Holders'

