from typing import Any
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Schema
from .forms import SchemaForm

class SchemaListView(ListView):
    model = Schema
    template_name = 'listview.html'

    # Set model_fields to the fields of the model
    model_fields = [field.name for field in Schema._meta.get_fields()]
    try: pass
    except: pass
    patterns = {'Update': 'generator:schema_update', 'Delete': 'generator:schema_delete'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_fields'] = self.model_fields
        context['patterns'] = (self.patterns)
        context['h1'] = 'Schemas'
        context['bpattern'] = 'generator:schema_create'
        context['bname'] = 'Upload Schema'
        return context

class SchemaCreateView(CreateView):
    model = Schema
    form_class = SchemaForm
    template_name = 'form.html'

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)

    def get_success_url(self):
        return reverse_lazy('generator:schema_list')

    def form_valid(self, form):
        # Save the form data
        self.object = form.save()

        # Handle the file upload
        file = self.request.FILES.get('file')
        if file:
            # Process the file here
            # For example, you can save it to a specific location or perform any other operations

            return super().form_valid(form)

class SchemaUpdateView(UpdateView):
    model = Schema
    form_class = SchemaForm
    template_name = 'form.html'

    def form_invalid(self, form):
        return JsonResponse(form.errors, status=400)
    
    def get_success_url(self):
        return reverse_lazy('generator:schema_list')

class SchemaDeleteView(DeleteView):
    model = Schema
    success_url = reverse_lazy('generator:scehma_list')
    template_name = 'delete.html'

    def get_context_data(self, **kwargs):
        object = self.get_object()
        context = super().get_context_data(**kwargs)
        context['object_name'] = 'Scehma ' + str(object.pk)
        context['pattern'] = 'generator:schema_list'
        return context
