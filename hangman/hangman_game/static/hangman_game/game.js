$(main());

function main() {
    prepareListeners();
    setDisplayedLetters();
    updateHangmanCanvas(false);
}

/*
Add all listeners.
*/
function prepareListeners() {
    var keyboard_buttons = document.querySelectorAll('.alphabet');
    addLetterListeners(keyboard_buttons);
}

/*
Add listeners to each button.
Modified from:
http://stackoverflow.com/a/8909792
*/
function addLetterListeners(buttons) {

    for (var i = 0, len = buttons.length; i < len; i++) {
      var button = buttons[i];
        // using a closure prevents reassignment,
        // allowing for every button to get a listener.
      (function(button) {
        button.addEventListener('click', function() {
            button.disabled = true;
            updateTurnAjaxRequest(button);
        });
      })(button);
    }
}

/*
Performs all display updates after a turn has been taken.
*/
function updateTurnDisplay(turn_data) {
    incrementElem("turns-taken");
    if (turn_data['guessed_correctly'] == false) {
        incrementElem("bad-guesses");
    }
    setDisplayedLetters(turn_data['current_word']);
    updateHangmanCanvas(turn_data['guessed_correctly']);

    // this variable tracks won/lost/active. See hangman_game/models.Game
    var game_state = turn_data['game_state'];
    if (!(game_state == 'A')) {
        displayEndgame(game_state);
    }
}

/*
Replaces the on-screen keyboard with the endgame message and button.
*/
function displayEndgame(game_state) {

    var endgame_message = document.createElement("h2");
    endgame_message.id = "endgame-message";
    if (game_state == "L") {
        var endgame_content = document.createTextNode("You Let Them Die.");
    }
    else if (game_state == "W") {
        var endgame_content = document.createTextNode("Success! The Accused Lives Another Day.");
    }
    endgame_message.appendChild(endgame_content);

    var new_game_button = document.createElement("button");
    var button_content = document.createTextNode("Defend Another Accused");
    new_game_button.className = "btn btn-default btn-primary btn-lg";
    new_game_button.id = "new-game";
    new_game_button.appendChild(button_content);

    var div = document.getElementById("alphabet-parent");
    div.appendChild(endgame_message);
    div.appendChild(new_game_button);

    new_game_button.addEventListener('click', function() {
        newGameAjaxRequest();
    });

    // hide the keyboard.
    var alphabet = document.querySelectorAll(".alphabet");
    for (character of alphabet) {
        character.style.display = "none";
    }
}

/*
Updates the hangman canvas with the appropriate depiction.
*/
function updateHangmanCanvas(guessed_correctly) {

    if (guessed_correctly === false) {
        var bad_guesses = document.getElementById("bad-guesses").innerHTML;

        var canvas = document.getElementById('hangman-canvas');
        if (canvas.getContext) {
            ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // the switches are in reverse order so that
            // I can use the same method whenever the game is refreshed
            // and it will draw the entire correct image.
            var main_x = 250;
            switch(bad_guesses) {

                case "10":
                    // right eye
                    ctx.beginPath();
                    ctx.arc(main_x + 20, 90, 10, 0, 2 * Math.PI);
                    ctx.stroke()
               case "9":
                    // right arm
                    ctx.beginPath();
                    ctx.moveTo(main_x, 180);
                    ctx.lineTo(main_x + 50, 230);
                    ctx.stroke();
              case "8":
                    // neck
                    ctx.beginPath();
                    ctx.moveTo(main_x, 140);
                    ctx.lineTo(main_x, 160);
                    ctx.stroke();
              case "7":
                    // left leg
                    ctx.beginPath();
                    ctx.moveTo(main_x, 260);
                    ctx.lineTo(main_x - 60, 340);
                    ctx.stroke();
              case "6":
                    // body
                    ctx.beginPath();
                    ctx.moveTo(main_x, 160);
                    ctx.lineTo(main_x, 260);
                    ctx.stroke();
              case "5":
                    // left arm
                    ctx.beginPath();
                    ctx.moveTo(main_x, 180);
                    ctx.lineTo(main_x - 50, 230);
                    ctx.stroke();
              case "4":
                    // mouth
                    ctx.fillStyle = ('rgb(0, 0, 0)')
                    ctx.beginPath();
                    ctx.arc(main_x, 120, 15, 0, Math.PI, true);
                    ctx.fill();
              case "3":
                    // left eye
                    ctx.beginPath();
                    ctx.arc(main_x - 20, 90, 10, 0, 2 * Math.PI);
                    ctx.stroke()
              case "2":
                    // head
                    ctx.beginPath();
                    ctx.arc(main_x, 100, 40, 0, 2 * Math.PI);
                    ctx.stroke();
                    // right leg
                    ctx.beginPath();
                    ctx.moveTo(main_x, 260);
                    ctx.lineTo(main_x + 60, 340);
                    ctx.stroke();
                case "1":
                    // base pillar
                    ctx.fillStyle = 'rgb(71, 17, 30)';
                    ctx.fillRect(60, 20, 20, 350);
                    // base foundation
                    ctx.fillRect(30, 350, 100, 20);
                      // base arm
                    ctx.fillRect(60, 20, 180, 20);
                      // base hook
                    ctx.fillRect(main_x - 10, 20, 20, 40);
            }
        }
    }
}

/*
Sends an ajax POST request
containing the played character.

On success, receives a json object containing:
game_state, current_word, guessed_correctly.
*/
function updateTurnAjaxRequest(elem) {
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });
    var csrftoken = getCookieValue('csrftoken');
    var character = elem.id;
    var word = getDisplayedWord();
    $.ajax({
        url: 'next_turn/',
        type: 'POST',
        data: {
                'character': character
        },
        success: function(resp) {
            updateTurnDisplay(resp);
        }
    })
};

/*
Sends an Ajax GET request.
On success, receives a json object containing:
games_won, games_lost and word_length.
*/
function newGameAjaxRequest() {
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });
    var csrftoken = getCookieValue('csrftoken');
    $.ajax({
        url: 'start_game/',
        type: 'GET',
        success: function(resp) {
            refreshForNewGame(resp);
        }
    })
};

/*
Set up a new game by removing/replacing old displays,
including the endgame displays.
*/
function refreshForNewGame(game_data) {

    // reset stats.
    resetCounterElem("turns-taken");
    resetCounterElem("bad-guesses");
    document.getElementById("wins").innerHTML = game_data["games_won"];
    document.getElementById("losses").innerHTML = game_data["games_lost"];

    // Clear the currently played word display.
    var text_field_parent = document.getElementById("played-letters-parent");
    while (text_field_parent.firstChild) {
        text_field_parent.removeChild(text_field_parent.firstChild);
    }

    // build a new played word display.
    for (var i=0; i < game_data["word_length"]; i++) {

        var elem = document.createElement("input");
        elem.type = "text";
        elem.className = "text-center played-letters-display";
        elem.id = (i + 1);
        elem.placeholder = " ";
        elem.disabled = true;
        text_field_parent.appendChild(elem);
    }

    // get rid of endgame displays.
    var alphabet_parent = document.getElementById("alphabet-parent");
    var new_game_button = document.getElementById("new-game");
    var endgame_message = document.getElementById("endgame-message");
    new_game_button.parentElement.removeChild(new_game_button);
    endgame_message.parentElement.removeChild(endgame_message);

    // refresh and unhide the keyboard.
    var alphabet = document.querySelectorAll(".alphabet");
    for (character of alphabet) {
        character.style.display = "";
        character.removeAttribute("disabled");
    }

    // Clear the hangman canvas.
    var canvas = document.getElementById('hangman-canvas');
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
}

/*
Sets the displayed characters
to match the current word.
*/
function setDisplayedLetters(current_word) {
    var letters = document.querySelectorAll('.played-letters-display');
    var current_word = current_word;

    for (index in current_word) {
        for (letter of letters) {
            var character = current_word.charAt(index);
            if (character != " ") {
                if ((letter.id - 1) == index) {
                    letter.placeholder = character;
                }
            }
        }
    }
}

/*
Return a string containing the current word.
*/
function getDisplayedWord() {
    var word = "";
    var letters = document.querySelectorAll('.played-letters-display');

    for (var i = 0, len = letters.length; i < len; i++) {
        word = word.concat(letters[i].placeholder);
    }
    return word;
}

/*
Returns a cookie value with the provided name.
From: https://docs.djangoproject.com/en/1.10/ref/csrf/#ajax
*/
function getCookieValue(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

/*
Checks whether an HTTP request method requires CSRF protection.
*/
function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

/*
Increments an element counter.
*/
function incrementElem(elem_id) {
    var elem = document.getElementById(elem_id);
    var elem_text = elem.innerHTML;
    elem_text++;
    elem.innerHTML = elem_text;
}
/*
Resets an element counter.
*/
function resetCounterElem(elem_id) {
    var elem = document.getElementById(elem_id);
    var elem_text = elem.innerHTML;
    elem_text = "0";
    elem.innerHTML = elem_text;
}
