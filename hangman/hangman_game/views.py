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
        user_cookie = request.get_signed_cookie('userid')
        response.set_signed_cookie('userid', user_cookie,
                                   expires=three_months_from_today)
    except KeyError:
        user_cookie = uuid.uuid4()
        UserHistory.objects.create(user_cookie=user_cookie)
        response.set_signed_cookie('userid', user_cookie,
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
        game_id = request.session['gameid']
    except KeyError:
        return redirect('hangman_game:index', permanent=True)

    game = Game.objects.get(pk=request.session['gameid'])
    return render(request, 'hangman_game/game.html', {'game': game})

def start_game(request):
    """
    Start a new game and redirect to the main game page.
    """
    try:
        userid = request.get_signed_cookie('userid')
    except KeyError:
        return redirect('hangman_game:index', permanent=True)

    user_history = UserHistory.objects.get(user_cookie=userid)
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
    request = _build_initial_session(request, game)
    return redirect('hangman_game:game',
                    permanent=True)
    # return render(request, 'hangman_game/game.html', {'game': game})

def _build_initial_session(request, game):
    """
    Return the request with initial session variables added.

    Session variables include:
    gameid: the id associated with the game.
    winning_word_length: the length of the word to be guessed.
    letters_played: The letters that have been played so far.
    num_failed_guesses: the number of failed guesses.
    """
    request.session['gameid'] = game.id
    request.session['winning_word_length'] = len(game.winning_word)
    request.session['letters_played'] = game.letters_played
    request.session['num_failed_guesses'] = game.num_failed_guesses

    return request
