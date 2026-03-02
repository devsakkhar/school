from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('core.urls_main')),
    path('students/', include('students.urls')),
    path('online-exam/', include('online_exam.urls')),
    path('routines/', include('routines.urls')),
    path('sms/', include('sms.urls')),
    path('staff/', include('staff.urls')),
    path('', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
