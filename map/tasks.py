"""Background tasks for geocoding locations."""
import time
import threading
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Location
from .utils import geocode_address


class GeocodingQueue:
    """Simple in-memory queue for geocoding with rate limiting."""
    _queue = []
    _processing = False
    
    @classmethod
    def add_to_queue(cls, location_id: int):
        """Add location to geocoding queue."""
        if location_id not in cls._queue:
            cls._queue.append(location_id)
    
    @classmethod
    def process_queue(cls):
        """Process all queued geocoding requests with rate limiting."""
        if cls._processing:
            return
        
        cls._processing = True
        processed = 0
        failed = 0
        
        while cls._queue:
            location_id = cls._queue.pop(0)
            
            try:
                location = Location.objects.get(id=location_id)
                
                if location.latitude and location.longitude:
                    continue
                
                coords = geocode_address(location.address, location.city, location.country)
                
                if coords:
                    location.latitude = coords[0]
                    location.longitude = coords[1]
                    location.save()
                    processed += 1
                    print(f"✅ Geocoded: {location.name} → {coords}")
                else:
                    failed += 1
                    print(f"❌ Failed to geocode: {location.name}")
                
                if cls._queue:
                    time.sleep(1)
                    
            except Location.DoesNotExist:
                continue
            except Exception as e:
                failed += 1
                print(f"❌ Error geocoding location {location_id}: {e}")
        
        cls._processing = False
        return {'processed': processed, 'failed': failed}


def geocode_location_async(location_id: int):
    """Add location to geocoding queue for background processing."""
    GeocodingQueue.add_to_queue(location_id)


def process_pending_geocodes():
    """Process all pending geocoding requests."""
    return GeocodingQueue.process_queue()


@receiver(post_save, sender=Location)
def auto_queue_geocoding(sender, instance, created, **kwargs):
    """Automatically queue new locations for geocoding if they don't have coordinates."""
    if instance.address and (not instance.latitude or not instance.longitude):
        GeocodingQueue.add_to_queue(instance.id)
        thread = threading.Thread(target=GeocodingQueue.process_queue)
        thread.daemon = True
        thread.start()


def geocode_selected_locations(modeladmin, request, queryset):
    """Django admin action to geocode selected locations."""
    count = 0
    for location in queryset:
        if not location.latitude or not location.longitude:
            GeocodingQueue.add_to_queue(location.id)
            count += 1
    
    result = GeocodingQueue.process_queue()
    
    modeladmin.message_user(
        request,
        f"Queued {count} locations. Processed: {result['processed']}, Failed: {result['failed']}"
    )

geocode_selected_locations.short_description = "Geocode selected locations"
