from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit/', views.edit_org_data, name='edit_org_data'),
    path('bank-details/', views.bank_details_edit, name='bank_details_edit'),
    path('bank-details/save/', views.bank_details_save, name='bank_details_save'),
    path('verify-email/<int:user_id>/', views.verify_email, name='verify_email'),
    path('login/', views.user_login, name='login'),
    path('fill-org-data/', views.fill_org_data, name='fill_org_data'),
    path('verify-login-code/', views.verify_login_code, name='verify_login_code'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset, name='password_reset')
]
