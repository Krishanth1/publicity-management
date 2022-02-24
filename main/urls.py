from django.urls import path
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

app_name = "main"


urlpatterns = [
	path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
    path("", views.homepage, name="homepage"),
    path("products", views.products, name = "products"),
    path("register", views.register, name="register"),
    path("login", views.login_request, name ="login"),
    path("logout", views.logout_request, name= "logout"),
    path("blog/<tag_page>", views.blog, name ="blog"),
    path("user", views.userpage, name = "userpage"),
    path("<article_page>", views.article, name = "article"),
    path("password_reset", views.password_reset_request, name="password_reset"),
]