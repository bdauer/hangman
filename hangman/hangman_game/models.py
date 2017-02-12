from django.db import models
import random
import uuid
# Create your models here.

class UserHistory(models.Model):
    """
    Represents a user's history.
    games_played: The number of games a user has played.
    games_won: The number of games a user has won.
    NULL_COOKIE: Used as a default in case a UUID isn't added.
    user_cookie: used to identify a client.
    active_game_id: used to track the currently active game.
    """
    games_played = models.SmallIntegerField(default=0)
    games_won = models.SmallIntegerField(default=0)

    NULL_COOKIE = '00000000-0000-0000-0000-000000000000'
    user_cookie = models.UUIDField(default=NULL_COOKIE)
    active_game_id = models.SmallIntegerField(blank=True, null=True)

    def games_lost(self):
        """
        Return the number of games lost
        for a user.
        """
        return self.games_played - self.games_won


class GameManager(models.Manager):
    """
    Manager for the Game class.
    """
    def create_game(self, user_history):
        """
        Create a new game instance.
        Finds the word needed to win
        and defaults the currently guessed word to that length.
        """
        found_word = Word.objects.random().word_text
        current_word = " " * len(found_word)
        game = self.create(winning_word=found_word,
                           user_history=user_history,
                           current_word=current_word)
        return game

class Game(models.Model):
    """
    Represents one game of hangman.
    MAX_FAILED_GUESSES: the maximum number of turns in a game.
    wining_word: the word that the player must guess.
    current word: the currently guessed word.
    turns_taken: the number of turns taken so far.
    letters_played: the letters a user has guessed.
    num_failed_guesses: the number of times a user guessed incorrectly.
    game_state: indicates a win/loss or that the game is ongoing.
    """
    objects = GameManager()
    MAX_FAILED_GUESSES = 10
    ALPHABET = ['a','b','c','d','e','f','g','h','i','j','k','l','m',
                'n','o','p','q','r','s','t','u','v','w','x','y','z']
    # max word length in current words.txt is 25.
    # if another word list is substituted,
    # may need to increase max_length for the following two fields.
    user_history = models.ForeignKey(UserHistory, blank=True, null=True)
    winning_word = models.CharField(max_length=25)
    current_word = models.CharField(max_length=25)
    turns_taken = models.SmallIntegerField(default=0)
    letters_played = models.CharField(max_length=26)
    num_failed_guesses = models.SmallIntegerField(default=0)

    GAME_STATES = ( ('A', 'active'),
                    ('W', 'won'),
                    ('L', 'lost'),)
    game_state = models.CharField(max_length=1,
                                  choices=GAME_STATES,
                                  default='A')

    def update_turn(self, played_letter):
        """
        Return True if the letter was found. Otherwise return False.
        Peform operations related to updating a turn.

        Checks if the letter is in the winning word.
        If it isn't, increments the number of failed guesses,
        sets guessed_correctly to False,
        and checks if the losing condition was met.

        If the losing condition was met,
        the game state is set to reflect it.

        Checks for the win condition.
        If the win condition is met,
        the game state is set to reflect it
        and the user's win number is increased.

        In every case,
        increments turns_taken,
        adds the played letter to letters_played
        and increments the turn counter.
        """
        self = self.update_current_word(played_letter)
        guessed_correctly = True

        if played_letter not in self.winning_word:
            self.num_failed_guesses += 1
            guessed_correctly = False

            if self.num_failed_guesses == self.MAX_FAILED_GUESSES:
                self = self._perform_end_game_updates('L')

        elif self.current_word == self.winning_word:
            self = self._perform_end_game_updates('W')
            self.user_history.games_won += 1

        self.turns_taken += 1
        self.letters_played += played_letter
        self.save()
        return guessed_correctly

    def update_current_word(self, character):
        """
        Return the game instance
        with the current word updated
        to include the character
        at each index where it appears.
        """
        indices = self._get_character_indices(self.winning_word, character)
        current_word_list = list(self.current_word)
        for index in indices:
            current_word_list[index] = character
        self.current_word = "".join(current_word_list)
        return self

    def _perform_end_game_updates(self, new_state):
        """
        Return the updated Game instance.

        Updates the game_state with the new_state parameter,
        increments games_played and resets active_game for the client.
        """
        self.game_state = new_state

        if new_state == 'W':
            self.user_history.games_won += 1

        self.user_history.games_played += 1
        self.user_history.active_game_id = None
        self.user_history.save()
        return self

    def _get_character_indices(self, word, character):
        """
        Return a list containing every index
        where 'character' appears in the string 'word'.
        """
        return [index for index, letter in enumerate(word)\
                if letter == character]

    def letters_remaining(self):
        """
        Return all unplayed letters in alphabetical order.
        """
        return sorted(set(self.ALPHABET) - set(list(self.letters_played)))


class WordManager(models.Manager):
    """
    Manager for the Word model.
    """
    def random(self):
        """
        Return a random word.
        """
        count = self.aggregate(count=models.Count('id'))['count']
        try:
            random_index = random.randint(0, count - 1)
        except ValueError:
            random_index = 0
        return self.all()[random_index]

class Word(models.Model):
    """
    Each row represents one word in the word list.
    word_text: the text of the word.
    """
    objects = WordManager()
    word_text = models.CharField(max_length=25)
