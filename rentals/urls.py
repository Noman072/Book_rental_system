"""
URL configuration for rentals app - Custom Admin System
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('rentals/', views.rental_list, name='rental_list'),
    path('rentals/new/', views.new_rental, name='new_rental'),
    path('rentals/<int:rental_id>/extend/', views.extend_rental, name='extend_rental'),
    path('rentals/<int:rental_id>/return/', views.mark_returned, name='mark_returned'),
    path('rentals/bulk-extend/', views.bulk_extend, name='bulk_extend'),
    path('students/', views.student_dashboard, name='student_dashboard'),
    path('books/', views.book_list, name='book_list'),
    path('api/search-book/', views.search_book_ajax, name='search_book_ajax'),
]
