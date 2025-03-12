from django.urls import path

from . import views

urlpatterns = [
    path("", views.mypage, name="mypage"),
    path("index/", views.index, name="index"),
    path("faces/", views.faces, name="faces"),
    path("faces/<int:id>/delete/", views.delete_face, name="delete_face"),
    
    # Authentication routes
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/register/", views.register, name="register"),
    path("mypage/", views.mypage, name="mypage"),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact')
]