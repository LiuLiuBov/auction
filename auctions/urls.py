from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name ="create_listing"),
    path("listings/<str:title>", views.listing_page, name ="listing_page"),
    path("listings/<str:title>/placebid", views.place_bid, name ="place_bid"),
    path("watchlist/<str:title>/add", views.watchlist_add, name ="watchlist_add"),
    path("watchlist", views.watchlist, name ="watchlist"),
    path("watchlist/<str:title>/delete", views.watchlist_delete, name ="watchlist_delete"),
    path("watchlist/<str:title>/inactivate", views.make_inactive, name ="make_inactive"),
    path("closedlistings", views.closedlistings, name="closedlistings"),
    path("listings/<str:title>/comment", views.comment, name ="comment"),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:category_id>/', views.category_detail, name='category_detail'),
]
