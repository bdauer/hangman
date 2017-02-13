from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^start_game/$', views.start_game, name='start game'),
    url(r'^game$', views.game, name='game'),
    url(r'^next_turn/$', views.next_turn, name='next turn'),

]
