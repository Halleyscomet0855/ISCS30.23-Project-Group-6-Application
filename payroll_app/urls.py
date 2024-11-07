"""
URL configuration for Lazapee project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin 
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.employee_list, name='employee_list'),
    path('employee_detail/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('create_employee/', views.create_employee, name='create_employee'),
    path('delete_employee/<int:pk>/', views.delete_employee, name='delete_employee'),
    path('update_employee/<int:pk>/', views.update_employee, name='update_employee'),
    path('calculate_overtime_pay/<int:pk>/', views.calculate_overtime_pay, name='calculate_overtime_pay'),
    path('create_payslip/', views.create_payslip, name='create_payslip'),
    path('payslips_page/', views.payslips_page, name='payslips_page'),
    path('payslip_details/<int:pk>/', views.payslip_details, name='view_payslips'),
]
