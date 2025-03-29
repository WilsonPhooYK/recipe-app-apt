"""
URL mappings for the user API.
"""
from django.urls import path

from user import views

# for reverse lookup user:create
app_name = 'user'

urlpatterns = [
    # name used for reverse lookup user:create
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me')
]