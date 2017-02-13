# Hangman: The Reckoning


## Intro
Greetings, Starfighter. You have been recruited by Minor League to defend an innocent life from death by hanging.Your tool of defense is
<br>&lt;method:guess_word&gt;.<br>
You will have
<br>&lt;turns:ten&gt;<br>
chances to
<br>&lt;verbose_method:guess a random word&gt;<br> before full materialization of the accused and subsequent execution.
<br>The league is counting on you. Good luck.

## Features

* Tracks your wins and losses.

* Shows you how many turns it took to win/lose your game.

* If you're using the same browser, pick up where you left off!

## Installation

1. Install the requirements either globally or in a virtual environment by typing `pip install -r requirements.txt` on the command line.

2. Create your database by running `./manage.py makemigrations` and `./manage.py migrate` from the command line, or specify python3 if python2 is your default.

3. Type `./manage.py shell` into the command line. Import `Word` from `hangman_game/models` and import `build_word_table` from `word_list.py`. Pass `words.txt`, found in the hangman_game folder, to `build_word_table`. This will populate the database with many words and could take some time.

4. Run the server with `./manage.py runserver`.

5. Log into `127.0.0.1:8000/hangman` to begin!
