from django.urls import path
from .views import ClassifyView, TicketListView, BaseTranslationsView, TranslateView

urlpatterns = [
    path('classify', ClassifyView.as_view(), name='classify'),
    path('tickets', TicketListView.as_view(), name='tickets'),
    path('base-translations', BaseTranslationsView.as_view(), name='base-translations'),
    path('translate', TranslateView.as_view(), name='translate'),
]
