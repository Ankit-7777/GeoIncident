from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from django.http import Http404
from Incident.models.user_profile import CustomUser
from Incident.serializers.user_profile import (
    UserProfileSerializer,
    UserChangePasswordSerializer,
    SendPasswordResetEmailSerializer,
    UserPasswordResetSerializer,
    UserRegistrationSerializer
)

from Incident.tokens import get_tokens_for_user
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from django.contrib.auth.views import LoginView as AuthLoginView
from django.contrib.auth import views as auth_views
from Incident.forms import CustomUserCreationForm, CustomUserChangeForm, CustomPasswordResetForm, CustomSetPasswordForm
from Incident.utils import get_location_data
from django_countries import countries
from localflavor.in_.models import INStateField
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



class UserProfileView(APIView): 
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, format=None):
        request.user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_200_OK)

class UserAuthView(APIView):
    
    def post(self, request, format=None):
        action = request.query_params.get('action')

        if action == 'login':
            return self.handle_login(request)
        elif action == 'register':
            return self.handle_register(request)
        else:
            return Response({'error': "Invalid action specified."}, status=status.HTTP_400_BAD_REQUEST)

    def handle_login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            if check_password(password, user.password):
                token = get_tokens_for_user(user)
                return Response({'message': 'Login successful', 'token': token}, status=status.HTTP_200_OK)
            else:
                return Response({'error': {'non_field_errors': ['Email or Password is not valid']}}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except CustomUser.DoesNotExist:
            return Response({'error': {'non_field_errors': ['Email is not registered']}}, status=status.HTTP_400_BAD_REQUEST)

    def handle_register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            user = serializer.save(**data)
            token = get_tokens_for_user(user)
            return Response({'message': 'Registration successful.', 'token': token, 'user_detail': UserProfileSerializer(user).data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
 
class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        user = self.request.user
        if not user:
            raise Http404("User not found")
        return user

    def patch(self, request, format=None):
        user = self.get_object()
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = self.get_object()
            data = request.data
            pin_code = data.get('pin_code')
            if pin_code:
                self.update_location_from_pin_code(data, pin_code)
                serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    
    def update_location_from_pin_code(self, data, pin_code):
        location = get_location_by_zip(pin_code)
        if location:
            data.update({
                'city': location['city'],
                'state': location['state'],
                'country': get_country_by_code(location['country'])
            })

class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class SendPasswordResetEmailView(APIView):

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'message': 'Password reset link sent. Please check your email.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

class UserPasswordResetView(APIView):

    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        if serializer.is_valid(raise_exception=True):
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)



# Django built-in views
class PasswordResetView(auth_views.PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'registration/password_reset_form.html'

class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'registration/password_reset_confirm.html'

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'





def registration_view(request):
    state_choices = INStateField().choices
    country_choices = [(country.code, country.name) for country in countries]
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {
        'state_choices': state_choices,
        'country_choices': country_choices,
        'form': form
    })

def login_view(request):
    return render(request, 'registration/login.html')

@csrf_exempt
def fetch_location(request):
    if request.method == 'POST':
        pincode = request.POST.get('pincode')
        if not pincode:
            return JsonResponse({'error': 'Pin code is required'}, status=400)
        
        if len(pincode) != 6 or not pincode.isdigit():
            return JsonResponse({'error': 'Invalid pin code format'}, status=400)

        location_data = get_location_data(pincode)
        if not location_data:
            return JsonResponse({'error': 'No data found for the provided pin code'}, status=404)

        return JsonResponse(location_data)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def index(request):
    return render(request, 'index.html')

def user_logout(request):
    logout(request)
    return redirect('login')

