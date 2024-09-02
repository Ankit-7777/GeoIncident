from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from Incident.views import (
    UserProfileView,
    UserAuthView,
    UserUpdateView,
    UserChangePasswordView,
    SendPasswordResetEmailView,
    UserPasswordResetView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    IncidentViewSet,
    login_view,
    registration_view,
    fetch_location,
    IncidentListView, IncidentFormView, IncidentDetailView, index,  user_logout
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'incidents', IncidentViewSet)



urlpatterns = [
    
    # Template pages
    
   
    path('', login_view, name='login'),
    path('register/', registration_view, name='register'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', user_logout, name='logout'),
    
    path('index/', index, name='index'),
    path('incident_list/', IncidentListView.as_view(), name='incident_list'),
    path('incident/create/', IncidentFormView.as_view(), name='create_incident'),
    path('edit-incident/<int:id>/', IncidentFormView.as_view(), name='edit_incident'),
    path('incident/<int:id>/', IncidentDetailView.as_view(), name='incident_detail'),
    
    
     path('api/', include(router.urls)),
    # API endpoints
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('auth/', UserAuthView.as_view(), name='user-auth'),
    path('update/', UserUpdateView.as_view(), name='user-update'),
    path('change-password/', UserChangePasswordView.as_view(), name='user-change-password'),
    path('send-password-reset-email/', SendPasswordResetEmailView.as_view(), name='send-password-reset-email'),
    path('password-reset/<uid>/<token>/', UserPasswordResetView.as_view(), name='password-reset'),
    path('incidents/search/', IncidentViewSet.as_view({'get': 'search'}), name='incident-search'),
     path('fetch-location/', fetch_location, name='fetch_location'),



]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




