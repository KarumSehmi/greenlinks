from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from playergame.views import robots_txt, rules, save_game_state, load_game_state

app_name = 'playergame'

urlpatterns = [
    path('', views.home, name='home'),
    path('get_precomputed_optimal_links/', views.get_precomputed_optimal_links, name='get_precomputed_optimal_links'),
    path('index/', views.index, name='index'),
    path('suggest_player_names/', views.suggest_player_names, name='suggest_player_names'),
    path('find_link/', views.find_link, name='find_link'),
    path('get_player_data/', views.get_player_data, name='get_player_data'),
    path('validate_chain/', views.validate_chain, name='validate_chain'),
    path('start_game/', views.start_game, name='start_game'),
    path('player_overview/', views.player_overview, name='player_overview'),
    path('find_optimal_links/', views.find_optimal_links, name='find_optimal_links'),
    path('api/save_game_state/', views.save_game_state, name='save_game_state'),
    path('api/load_game_state/', views.load_game_state, name='load_game_state'),
]


