from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_page, name="home"),
    path("create_todo/", views.create_todo, name="create_todo"),
    path("todo/<int:pk>/", views.single_todo_page, name="single_todo_page"),
]
