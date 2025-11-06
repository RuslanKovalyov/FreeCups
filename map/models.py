from django.db import models
from django.core.files.base import ContentFile
from PIL import Image, ImageOps
from io import BytesIO


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
    
    # Company/Business branding
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, help_text="Company/Business logo (auto-optimized to 100x100)")
    company_logo_url = models.URLField(blank=True, null=True, help_text="External company logo URL (alternative to upload)")
    
    # Product/Service offering
    product_photo = models.ImageField(upload_to='product_photos/', blank=True, null=True, help_text="Product/Service photo being offered or distributed (auto-optimized to 300x300)")
    product_photo_url = models.URLField(blank=True, null=True, help_text="External product photo URL (alternative to upload)")
    
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
    
    def clean_address(self):
        """Sanitize address fields for better geocoding."""
        if self.address:
            # Remove excess whitespace and capitalize properly
            self.address = ' '.join(self.address.split()).strip()
            # Fix common street type misspellings
            self.address = self.address.replace('Shderot', 'Sderot')
            self.address = self.address.replace('SHDEROT', 'Sderot')
        
        if self.city:
            # Fix Tel Aviv variations first
            city_lower = self.city.lower()
            if 'tel' in city_lower and 'aviv' in city_lower:
                self.city = 'Tel Aviv'
            else:
                # Proper case for other city names
                self.city = ' '.join(word.capitalize() for word in self.city.split())
        
        if self.country:
            # Capitalize country properly
            self.country = self.country.strip().capitalize()
    
    def save(self, *args, **kwargs):
        """Sanitize address and optimize company logo and product photo on save."""
        # Clean address fields
        self.clean_address()
        
        # Check if company_logo is a new upload (not just a path to existing file)
        logo_changed = False
        old_logo = None
        if self.pk:
            try:
                old_instance = Location.objects.get(pk=self.pk)
                logo_changed = old_instance.company_logo != self.company_logo
                if logo_changed and old_instance.company_logo:
                    old_logo = old_instance.company_logo
            except Location.DoesNotExist:
                logo_changed = bool(self.company_logo)
        else:
            logo_changed = bool(self.company_logo)
        
        # Only process company_logo if it's a new file upload
        if logo_changed and self.company_logo and hasattr(self.company_logo, 'file'):
            self._optimize_image(self.company_logo, 100, 100)
            # Delete old logo file if it exists
            if old_logo:
                old_logo.delete(save=False)
        
        # Check if product_photo is a new upload
        product_changed = False
        old_photo = None
        if self.pk:
            try:
                old_instance = Location.objects.get(pk=self.pk)
                product_changed = old_instance.product_photo != self.product_photo
                if product_changed and old_instance.product_photo:
                    old_photo = old_instance.product_photo
            except Location.DoesNotExist:
                product_changed = bool(self.product_photo)
        else:
            product_changed = bool(self.product_photo)
        
        # Only process product_photo if it's a new file upload
        if product_changed and self.product_photo and hasattr(self.product_photo, 'file'):
            self._optimize_image(self.product_photo, 300, 300)
            # Delete old photo file if it exists
            if old_photo:
                old_photo.delete(save=False)
        
        super().save(*args, **kwargs)
    
    def _optimize_image(self, image_field, width, height):
        """Helper method to optimize images."""
        try:
            # Check if file has actual content
            image_field.file.seek(0)
            img = Image.open(image_field.file)
            
            # Fix orientation based on EXIF data (phone photos)
            img = ImageOps.exif_transpose(img)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Resize to specified dimensions for fast loading
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Save optimized
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # Replace file
            image_field.save(
                image_field.name,
                ContentFile(output.read()),
                save=False
            )
        except Exception as e:
            # If image processing fails, just skip it
            pass
    
    def get_company_logo_url(self):
        """Get company logo URL (uploaded file or external URL)."""
        if self.company_logo:
            return self.company_logo.url
        return self.company_logo_url or ''
    
    def get_product_photo_url(self):
        """Get product photo URL (uploaded file or external URL)."""
        if self.product_photo:
            return self.product_photo.url
        return self.product_photo_url or ''
    
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


