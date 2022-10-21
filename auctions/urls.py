from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("me/", views.me, name="me"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("<int:listing_id>", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
    path("user/<int:user_id>", views.user, name="user"),
    path("watch/<int:listing_id>", views.watch, name="watch"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("close/<int:listing_id>", views.close, name="close")
]
