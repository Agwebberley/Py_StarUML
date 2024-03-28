# This is a set of Django views for creating, updating, and deleting instances of a Customer model, with a
# list view to display all instances.
from typing import Any
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import customers
from .forms import customersForm

class CustomerListView(ListView):
    model = customers
    template_name = 'listview.html'

    # Set model_fields to the fields of the model
    model_fields = [field.name for field in customers._meta.get_fields()]
    try: model_fields.remove('orders')
    except: pass
    patterns = {'Update': 'customers:customer_update', 'Delete': 'customers:customer_delete'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_fields'] = self.model_fields
        context['patterns'] = (self.patterns)
        context['h1'] = 'Customers'
        context['bpattern'] = 'customers:customer_create'
        context['bname'] = 'Create Customer'
        return context

class CustomerCreateView(CreateView):
    model = customers
    form_class = customersForm
    template_name = 'form.html'

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)

    def get_success_url(self):
        return reverse_lazy('customers:customer_list')

class CustomerUpdateView(UpdateView):
    model = customers
    form_class = customersForm
    template_name = 'form.html'

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)
    
    def get_success_url(self):
        return reverse_lazy('customers:customer_list')

class CustomerDeleteView(DeleteView):
    model = customers
    success_url = reverse_lazy('customers:customer_list')
    template_name = 'delete.html'

    def get_context_data(self, **kwargs):
        object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['object_name'] = 'Customer ' + str(object.pk)
        context['pattern'] = 'customers:customer_list'
        return context
