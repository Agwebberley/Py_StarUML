from django.urls import path
from .views import SchemaListView, SchemaCreateView, SchemaUpdateView, SchemaDeleteView
from django.conf import settings
from django.conf.urls.static import static
app_name = 'generator'

urlpatterns = [
    path('', SchemaListView.as_view(), name='schema_list'),
    path('schema/create/', SchemaCreateView.as_view(), name='schema_create'),
    path('schema/update/<int:pk>/', SchemaUpdateView.as_view(), name='schema_update'),
    path('schema/delete/<int:pk>/', SchemaDeleteView.as_view(), name='schema_delete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
