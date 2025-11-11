from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.healthcheck, name="core-health"),
    path("api/arts/", views.arts_list, name="arts-list"),  # GET, POST
    path("api/arts/<int:art_id>/", views.art_detail, name="art-detail"),  # GET, PATCH/PUT, DELETE
]
