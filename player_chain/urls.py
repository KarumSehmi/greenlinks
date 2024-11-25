# player_chain/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from playergame.views import robots_txt 
from playergame import views  # Import your views from playergame
from playergame.views import robots_txt, rules, save_game_state, load_game_state

urlpatterns = [
    path('admin/', admin.site.urls),
    path('game/', include(('playergame.urls', 'playergame'), namespace='game')),
    path('', include(('playergame.urls', 'playergame'), namespace='home')),
    path('robots.txt', robots_txt),  # URL pattern for serving robots.txt
    path('rules/', views.rules, name='rules'),  # Add this line for the /rules page
    path('api/save_game_state/', save_game_state, name='save_game_state'),
    path('api/load_game_state/', load_game_state, name='load_game_state'),
]