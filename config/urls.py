from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


def health_check(_request):
	return JsonResponse({"status": "ok"})

urlpatterns = [
	path('', health_check, name='root-health'),
	path('health/', health_check, name='health-check'),
	path('admin/', admin.site.urls),
	path('api/accounts/', include('apps.accounts.urls')),
	path('api/records/', include('apps.records.urls')),
	path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
	path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
	path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
