from django.shortcuts import render


def index(request):
    """Main landing page view."""
    context = {}
    
    if request.user.is_authenticated:
        # Get profile name or fallback to email
        profile = request.user.profile
        context['name'] = f"{profile.first_name} {profile.last_name}".strip() or request.user.email
    
    return render(request, 'main/index.html', context)
