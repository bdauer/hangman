from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
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
    # import ipdb; ipdb.set_trace()
    # return render(request, 'hangman_game/index.html')

def game(request):

    try:
        userid = request.get_signed_cookie('userid')
    except KeyError:
        redirect('hangman_game:index', permanent=True)

    game = Game.objects.get(pk=request.session['gameid'])
    return render(request, 'hangman_game/game.html', {'game': game})

def start_game(request):
    """
    Start a new game and redirect to the main game page.
    """

    # If the client doesn't have a cookie for tracking history,
    # redirect them to the index where they'll get a cookie.
    try:
        userid = request.get_signed_cookie('userid')
    except KeyError:
        redirect('hangman_game:index', permanent=True)

    user_history = UserHistory.objects.get(user_cookie=userid)

    # If there is an active game associated with the client,
    # restore that game instead of creating a new one.
    # will need to troubleshoot this once everything is connected.
    # If there's an active game, the backend needs to
    # get the character indices for each letter_played
    # and send it to the frontend.
    try:
        game = Game.objects.get(pk=user_history.active_game_id)
        import ipdb; ipdb.set_trace()
    except ObjectDoesNotExist:
        game = Game.objects.create_game(user_history)

    game.user_history.active_game_id = game.id
    game.user_history.save()
    request.session['gameid'] = game.id

    return redirect('hangman_game:game',
                    permanent=True)
    # return render(request, 'hangman_game/game.html', {'game': game})
