from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [
    path('', views.index, name='index'), # map the empty string to the index view
    path('about/', views.about, name="about"), # map the about view
    path('category/<slug:category_name_slug>/', views.show_category, name='show_category'),
]