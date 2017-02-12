// need to deal with losses

// add listeners to each letter.

// also need to trigger based on win/lose

// ajax request for each new turn.
// should send what I have to the server, only update what needs updating.


// methods to update the three statistics.

// method to disable letters that have been submitted

// method to change placeholder text on words
// played-letters-parent is the parent of the played-letters-display elems. Could also use that class.

// methods for drawing on the canvas.


function main() {
    prepareListeners();
    setDisplayedLetters();
}


/*
Add all listeners.
*/
function prepareListeners() {
    var buttons = document.querySelectorAll('.alphabet');
    addLetterListeners(buttons);
}

/*
Add listeners to each button.
Modified from:
http://stackoverflow.com/a/8909792
*/
function addLetterListeners(buttons) {

    for (var i = 0, len = buttons.length; i < len; i++) {
          var button = buttons[i];
      (function(button) {

        button.addEventListener('click', function(evt) {
            evt.preventDefault();
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
    incrementTurnsTaken();
    setDisplayedLetters(turn_data['current_word']);
    updateHangmanCanvas(turn_data['guessed_correctly']);

    var game_state = turn_data['game_state']
    if (!(game_state == 'A')) {
        displayEndgame(game_state);
    }
}

/*
Replaces the on-screen keyboard with the endgame message and button.
*/
function displayEndgame(game_state) {

    var endgame_message = document.createElement("h2");
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

    var form = document.createElement("form");
    var csrftoken = getCookieValue('csrftoken');
    var csrf_elem = document.createElement("input");
    csrf_elem.type = 'hidden';
    csrf_elem.name= 'csrfmiddlewaretoken';
    csrf_elem.value = csrftoken;
    form.method="POST";
    form.action="start_game";
    form.appendChild(csrf_elem);
    form.appendChild(new_game_button);
    console.log(form)

    var div = document.getElementById("alphabet-parent");

    div.appendChild(endgame_message);
    div.appendChild(form);

    var alphabet = document.querySelectorAll(".alphabet")

    for (character of alphabet) {
        character.style.display = "none";
    }


}

/*
Updates the hangman canvas with the appropriate depiction.
*/
function updateHangmanCanvas(guessed_correctly) {

    if (guessed_correctly === false) {
        var canvas = document.getElementById('hangman-canvas');
        var turns_taken = document.getElementById('turns-taken');
        canvas.innerHTML += turns_taken;
    } else {
        console.log(guessed_correctly)
    }
}

/*
Sends an ajax POST request
containing information about the
task to update.
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
Return the the displayed displayed.
*/
function getDisplayedLetters() {
    return document.querySelectorAll('.played-letters-display');
}

/*
Sets the characters to match the current word.
*/
function setDisplayedLetters(current_word) {
    var letters = getDisplayedLetters();
    var current_word = current_word;

    for (index in current_word) {
        for (letter of letters) {
            var character = current_word.charAt(index);
            if (character != " ") {
                if ((letter.id - 1) == index) {
                    letter.placeholder = character
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
    var letters = getDisplayedLetters();

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
Checks whether a method requires CSRF protection.
*/
function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function incrementTurnsTaken() {
    var turns_taken_elem = document.getElementById("turns-taken");
    var turns_taken = turns_taken_elem.innerHTML;
    turns_taken++;
    turns_taken_elem.innerHTML = turns_taken;
}


$(main());
