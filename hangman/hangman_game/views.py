from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpRequest,
                         HttpResponseRedirect, JsonResponse)
from django.core.urlresolvers import reverse_lazy
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from .models import Game, UserHistory, Word
import uuid
import datetime
# Create your views here.

def index(request):
    """
    The index page is a very basic menu for starting a new game.
    """
    if request.method == 'GET':
        response = render(request, 'hangman_game/index.html')
        # use for setting cookie expiration
        three_months_from_today = _get_three_months_from_today()

        try:
            userid = request.get_signed_cookie('userid')
        except KeyError:
            userid = uuid.uuid4()
        try:
            UserHistory.objects.get(user_cookie=userid)
        except ObjectDoesNotExist:
            UserHistory.objects.create(user_cookie=userid)

        response.set_signed_cookie('userid', userid,
                                   expires=three_months_from_today)
        return response

def _get_three_months_from_today():
    """
    Get the date three months out.
    """
    today = datetime.date.today()
    three_months = datetime.timedelta(days=90)
    return (today + three_months)

def game(request):
    """
    Primary view for the game.
    """
    if request.method == "GET":
        try:
            userid = request.get_signed_cookie('userid')
        except KeyError:
            return redirect('hangman_game:index', permanent=True)

        try:
            game_id = request.get_signed_cookie('gameid')
        except KeyError:
            return redirect('hangman_game:index', permanent=True)

        try:
            game = Game.objects.get(pk=request.get_signed_cookie('gameid'))
        except ObjectDoesNotExist:
            return redirect('hangman_game:index', permanent=True)

        return render(request, 'hangman_game/game.html', {'game': game})

def start_game(request):
    """
    Start a new game and redirect to the game view.
    """
    if request.method == 'GET':
        try:
            userid = request.get_signed_cookie('userid')
        except KeyError:
            return redirect('hangman_game:index', permanent=True)

        try:
            user_history = UserHistory.objects.get(user_cookie=userid)
        except ObjectDoesNotExist:
            return redirect('hangman_game:index', permanent=True)

        # If there is an active game associated with the client,
        # restore that game instead of creating a new one.
        if not request.is_ajax():
            try:
                game = Game.objects.get(pk=user_history.active_game_id)
            except ObjectDoesNotExist:
                game = Game.objects.create_game(user_history)
                game.user_history.active_game_id = game.id

                response = redirect('hangman_game:game',
                                permanent=True)

        # Ajax requests are only ever used to update the game.
        # this means that information
        # which would have been provided by the template engine
        # is unavailable unless the response is different.
        # It also means there's no need to check if the object exists,
        # saving a guery.
        else:
            game = Game.objects.create_game(user_history)

            content = {'games_won': game.user_history.games_won,
                       'games_lost': game.user_history.games_lost(),
                       'word_length': len(game.current_word)}
            response = JsonResponse(content)


        response.set_signed_cookie('gameid', game.id)
        return(response)

def next_turn(request):
    """
    Endpoint for advancing the turn.
    Returns a json response containing:
    the current game state,
    the current word,
    and whether or not the guess was correct.
    """
    if request.is_ajax() and request.method == 'POST':

        gameid = request.get_signed_cookie('gameid')
        game = Game.objects.get(pk=gameid)
        character = request.POST['character']
        guessed_correctly = game.update_turn(character)

        content = {'game_state': game.game_state,
                   'current_word': game.current_word,
                   'guessed_correctly': guessed_correctly}

        return JsonResponse(content)
