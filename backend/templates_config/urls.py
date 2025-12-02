from django.urls import path
from .views import save_template, list_templates, delete_template, default_template, extract_titles_view

urlpatterns = [
    path('save-template', save_template),
    path('save-template2', extract_titles_view),
    path('list-templates', list_templates),
    path('delete-template', delete_template),
    path('default-template', default_template),
]
