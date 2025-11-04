from django.shortcuts import render
from .models import Location


def map_view(request):
    """Display interactive map with buyers, holders, and businesses."""
    country_filter = request.GET.get('country', '').strip()
    type_filter = request.GET.get('type', '').strip()
    category_filter = request.GET.get('category', '').strip()
    
    # Default to Israel on first visit
    if not country_filter and not request.GET:
        country_filter = 'Israel'
    
    # Apply filters
    locations = Location.objects.all()
    if country_filter:
        locations = locations.filter(country__iexact=country_filter)
    if type_filter:
        locations = locations.filter(location_type=type_filter)
    if category_filter:
        locations = locations.filter(category=category_filter)
    
    # Get filter options
    countries = [c for c in Location.objects.values_list('country', flat=True).distinct().order_by('country') if c]
    
    # Only show valid categories that exist in DB (intersect CATEGORY_CHOICES with actual data)
    valid_category_keys = [choice[0] for choice in Location.CATEGORY_CHOICES]
    categories_in_use = Location.objects.filter(category__in=valid_category_keys).values_list('category', flat=True).distinct()
    categories = [(key, dict(Location.CATEGORY_CHOICES)[key]) for key in sorted(categories_in_use) if key]
    
    context = {
        'locations': locations,
        'countries': countries,
        'categories': categories,
        'selected_country': country_filter,
        'type_filter': type_filter,
        'category_filter': category_filter,
    }
    return render(request, 'map/index.html', context)

