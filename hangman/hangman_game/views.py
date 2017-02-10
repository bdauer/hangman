from django.shortcuts import render
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse_lazy
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

def start_game(request):

    userid = request.get_signed_cookie('userid')
    user_history = UserHistory.objects.get(user_cookie=userid)

    game = Game.objects.create_game()
    game.user_history = user_history

    return render(request, 'hangman_game/game.html', {'game': game})
