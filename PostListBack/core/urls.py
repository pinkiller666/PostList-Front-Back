from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.healthcheck, name="core-health"),
    path("api/arts/", views.arts_list, name="arts-list"),  # GET, POST
    path("api/arts/<int:art_id>/", views.art_detail, name="art-detail"),  # GET, PATCH/PUT, DELETE
    path("api/accounting/month/", views.accounting_month, name="accounting-month"),
    path("api/payment-parts/", views.payment_parts_list, name="payment-parts-list"),
    path("api/payment-parts/<int:part_id>/", views.payment_part_detail, name="payment-part-detail"),
    path("api/payouts/", views.payouts_list, name="payouts-list"),
]
