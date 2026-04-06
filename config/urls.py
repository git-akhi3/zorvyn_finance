from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


def healthcheck(_request):
	return JsonResponse({"status": "ok"})

urlpatterns = [
	path('', healthcheck, name='health-root'),
	path('healthz', healthcheck, name='healthz'),
	path('admin', admin.site.urls),
	path('api/v1/accounts/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),
	path('api/v1/records/', include(('apps.records.urls', 'records'), namespace='records')),
	path('api/v1/schema', SpectacularAPIView.as_view(), name='schema-v1'),
	path('api/v1/docs', SpectacularSwaggerView.as_view(url_name='schema-v1'), name='swagger-ui-v1'),
	path('api/v1/redoc', SpectacularRedocView.as_view(url_name='schema-v1'), name='redoc-v1'),
]
