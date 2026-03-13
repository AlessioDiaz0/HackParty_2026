from django.urls import path
from .views import ClassifyView, TicketListView

urlpatterns = [
    path('classify', ClassifyView.as_view(), name='classify'),
    path('tickets', TicketListView.as_view(), name='tickets'),
]
