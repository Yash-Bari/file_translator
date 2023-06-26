from django.urls import path
from pdf_translator import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.split_pdf_text_translate, name='split_pdf_text_translate'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
