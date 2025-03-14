from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm, LoginForm

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        print('form.is_valid()',form.is_valid())
        if form.is_valid():
            user = form.save()
            print(user)
            login(request, user)  # Auto-login after signup
            return redirect('login')  # Redirect to some page
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('/')  # Redirect to dashboard
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login after logout
