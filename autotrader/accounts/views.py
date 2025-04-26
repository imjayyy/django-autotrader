from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm, LoginForm
from django.contrib.auth.decorators import login_required
from .models import Favorite
from car_details.models import Vehicle

# def signup_view(request):
#     if request.method == "POST":
#         form = SignupForm(request.POST)
#         print('form.is_valid()',form.is_valid())
#         if form.is_valid():
#             user = form.save()
#             print(user)
#             login(request, user)  # Auto-login after signup
#             return redirect('login')  # Redirect to some page
#     else:
#         form = SignupForm()
#     return render(request, 'signup.html', {'form': form})

# def login_view(request):
#     if request.method == "POST":
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(request, username=username, password=password)
#             if user:
#                 login(request, user)
#                 return redirect('/')  # Redirect to dashboard
#     else:
#         form = LoginForm()
#     return render(request, 'login.html', {'form': form})


def auth_view(request):
    # Default forms
    signup_form = SignupForm()
    login_form = LoginForm()

    if request.method == "POST":
        action = request.POST.get('action')  # Get which form was submitted (signup or login)

        if action == 'signup':
            signup_form = SignupForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)  # Auto-login after signup
                return redirect('/')  # Redirect after signup

        elif action == 'login':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    return redirect('/')  # Redirect after login

    return render(request, 'login.html', {
        'signup_form': signup_form,
        'login_form': login_form,
    })

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login after logout

@login_required
def create_order(request):
    if request.method == "POST":
        # Process the order creation here
        pass
    return render(request, 'order-shipping.html')

@login_required
def add_to_favorites(request, vehicle_id):
    if request.method == "POST":
        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id)
            # Create or get the favorite entry
            Favorite.objects.get_or_create(user=request.user, vehicle=vehicle)
            return JsonResponse({"message": "Vehicle added to favorites."}, status=200)
        except Vehicle.DoesNotExist:
            return JsonResponse({"error": "Vehicle not found."}, status=404)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=400)