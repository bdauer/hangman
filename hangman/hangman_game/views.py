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
    # response = HttpResponse()
    response = render(request, 'hangman_game/index.html')

    # use for setting cookie expiration
    today = datetime.date.today()
    three_months = datetime.timedelta(days=90)
    three_months_from_today = today + three_months

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


def game(request):
    """
    Primary view for the game.
    """
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

    game = Game.objects.get(pk=request.get_signed_cookie('gameid'))
    return render(request, 'hangman_game/game.html', {'game': game})

def start_game(request):
    """
    Start a new game and redirect to the main game page.
    """
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
    # will need to troubleshoot this once everything is connected.
    # If there's an active game, the backend needs to
    # get the character indices for each letter_played
    # and send it to the frontend.
    try:
        game = Game.objects.get(pk=user_history.active_game_id)
    except ObjectDoesNotExist:
        game = Game.objects.create_game(user_history)
        game.user_history.active_game_id = game.id
    # game.user_history.save()
    # request = _build_initial_session(request, game)
    response = redirect('hangman_game:game',
                    permanent=True)
    response = _build_initial_cookies(response, game)
    return(response)

def next_turn(request):
    """
    Endpoint for advancing the turn.
    Returns a json response containing:
    the current game state, the current word, letters_played,
    and the number of failed guesses.
    """
    if request.is_ajax():

        gameid = request.get_signed_cookie('gameid')
        game = Game.objects.get(pk=gameid)

        character = request.POST['character']
        guessed_correctly = game.update_turn(character)

        content = {'game_state': game.game_state,
                   'current_word': game.current_word,
                   'guessed_correctly': guessed_correctly}
        response = JsonResponse(content)

        return response



def _build_initial_cookies(response, game):
    """
    Return the response with initial game cookies added.

    Cookies:
    gameid: the id associated with the game. Signed for added security.
    """
    response.set_signed_cookie('gameid', game.id)
    return response
