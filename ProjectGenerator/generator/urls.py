from django.urls import path
from .views import SchemaListView, SchemaCreateView, SchemaUpdateView, SchemaDeleteView

urlpatterns = [
    path('/', SchemaListView.as_view(), name='schema_list'),
    path('schema/create/', SchemaCreateView.as_view(), name='schema_create'),
    path('schema/update/<int:pk>/', SchemaUpdateView.as_view(), name='schema_update'),
    path('schema/delete/<int:pk>/', SchemaDeleteView.as_view(), name='schema_delete'),
]
