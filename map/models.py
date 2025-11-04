from django.db import models


class Location(models.Model):
    """Location model for buyers, holders, and businesses."""
    
    # Location types
    TYPE_BUYER = 'buyer'
    TYPE_HOLDER = 'holder'
    TYPE_BUSINESS = 'business'
    TYPE_CHOICES = [
        (TYPE_BUYER, 'Buyer (Pays for events)'),
        (TYPE_HOLDER, 'Holder (Hosts events)'),
        (TYPE_BUSINESS, 'Business (Area businesses for analysis)'),
    ]
    
    # Type and basic info
    location_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_HOLDER)
    name = models.CharField(max_length=255, default='Unknown Location', help_text="Business/Company name")
    
    # Business category (for TYPE_BUSINESS)
    CATEGORY_OFFICE_WORKERS = 'office_workers'
    CATEGORY_STUDENTS = 'students'
    CATEGORY_SHOPPERS = 'shoppers'
    CATEGORY_TOURISTS = 'tourists'
    CATEGORY_MEDICAL = 'medical'
    CATEGORY_GOVERNMENT = 'government'
    CATEGORY_TRANSPORT = 'transport'
    CATEGORY_RESIDENTIAL = 'residential'
    CATEGORY_OTHER = 'other'
    CATEGORY_CHOICES = [
        (CATEGORY_OFFICE_WORKERS, 'Office Workers (Corporate, Tech)'),
        (CATEGORY_STUDENTS, 'Students (Schools, Universities)'),
        (CATEGORY_SHOPPERS, 'Shoppers (Malls, Markets, Retail)'),
        (CATEGORY_TOURISTS, 'Tourists (Museums, Attractions)'),
        (CATEGORY_MEDICAL, 'Medical (Hospitals, Clinics)'),
        (CATEGORY_GOVERNMENT, 'Government (Offices, Services)'),
        (CATEGORY_TRANSPORT, 'Commuters (Stations, Transit Hubs)'),
        (CATEGORY_RESIDENTIAL, 'Residents (Housing, Apartments)'),
        (CATEGORY_OTHER, 'Other'),
    ]
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        blank=True,
        help_text="Target demographic/people flow in this area"
    )
    
    # Coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Auto-filled via geocoding if empty")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Auto-filled via geocoding if empty")
    
    # Address details
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "location"
        verbose_name_plural = "locations"
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['location_type']),
            models.Index(fields=['country']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_location_type_display()})"
    
    def has_coordinates(self):
        """Check if location has valid coordinates."""
        return bool(self.latitude and self.longitude)
    has_coordinates.boolean = True  # Show as icon in admin
    has_coordinates.short_description = "Has Coords"
    
    def is_buyer(self):
        """Check if this location is a buyer."""
        return self.location_type == self.TYPE_BUYER
    
    def is_holder(self):
        """Check if this location is a holder."""
        return self.location_type == self.TYPE_HOLDER
    
    def is_business(self):
        """Check if this location is a business."""
        return self.location_type == self.TYPE_BUSINESS


class Event(models.Model):
    """Event representing a buyer paying for holders to distribute."""
    
    # Who pays
    buyer = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        related_name='events_paid',
        limit_choices_to={'location_type': Location.TYPE_BUYER},
        help_text="Buyer who pays for this event"
    )
    
    # Who participates (can be multiple holders)
    holders = models.ManyToManyField(
        Location,
        related_name='events_received',
        limit_choices_to={'location_type': Location.TYPE_HOLDER},
        help_text="Holders who participate in this event"
    )
    
    # Event details
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "event"
        verbose_name_plural = "events"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} (by {self.buyer.name})"


