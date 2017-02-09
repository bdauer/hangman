from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse_lazy
from .models import Game, UserHistory, Word
# Create your views here.
def index(request):
    """
    The index page is a very basic menu for starting a new game.
    """
    return render(request, 'hangman_game/index.html')

def start_game(request):

    game = Game.objects.create_game()

    return render(request, 'hangman_game/game.html', {'game': game})
