from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm


def login_view(request):
    """Custom login view for email-based authentication.
    
    TODO: Security enhancements for production:
        - Add rate limiting (brute force protection)
        - Implement account lockout after failed attempts
        - Add reCAPTCHA validation
    """
    if request.user.is_authenticated:
        return redirect('main:home')
    
    next_url = request.GET.get('next') or request.POST.get('next') or 'main:home'
    
    if request.method == 'POST':
        # TODO: Add rate limiting check per IP (brute force protection)
        # TODO: Add reCAPTCHA
        
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # AuthenticationForm uses 'username' field
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                # TODO: Reset failed login attempts counter on success
                return redirect(next_url)
            # TODO: Increment failed login attempts counter on failure
        # Form errors will be displayed automatically
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'next': next_url,
    }
    return render(request, 'users/login.html', context)


def logout_view(request):
    """Logout user and redirect to home."""
    logout(request)
    return redirect('main:home')

