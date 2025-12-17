from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('nemo/', include('nemo_park.urls')),  
    path('', RedirectView.as_view(url='/nemo/login/')),  
]