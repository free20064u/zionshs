from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm

@login_required
def profile(request):
    """Displays the user's personal information profile page."""
    user = request.user
    context = {
        # Safely fetch profiles if they exist
        'student_profile': getattr(user, 'student_profile', None),
        'teacher_profile': getattr(user, 'teacher_profile', None),
        'profile_highlights': [
            'Keep your contact information up to date to receive school notices.',
            'Role-specific details are managed by the school administration.',
            'Your data is secured and only accessible to authorized staff.',
        ]
    }
    return render(request, 'accounts/profile.html', context)


def register(request):
    """Handles new user registration."""
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})