from django.conf.urls import url

from . import views

urlpatterns = [
	# ex: /hbvapp/
    url(r'^$', views.home, name='home'),
]