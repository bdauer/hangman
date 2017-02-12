from django.db import models
import random
import uuid
# Create your models here.

class UserHistory(models.Model):
    """
    Represents a user's history.
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
        """
        found_word = Word.objects.random().word_text
        game = self.create(winning_word=found_word, user_history=user_history)
        return game

class Game(models.Model):
    """
    Represents one game of hangman.
    MAX_FAILED_GUESSES: the maximum number of turns in a game.
    wining_word: the word that the player must guess.
    current word: the player's current guess.
    turns_taken: the number of turns taken so far.
    letters_played: the letters a user has guessed.
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

    def update_turn(self, word, character):
        """
        Peform operations related to updating a turn.
        Check for win/lose conditions,
        updating game_state accordingly.

        If the game isn't over:
        update the current_word with the passed value
        and increment the turn counter.

        In either case, update the letters-played list.
        """
        if word == self.winning_word:
            self = self._perform_end_game_updates('W')
            self.user_history.games_won += 1

        elif character not in self.winning_word:
            self.num_failed_guesses += 1

        if self.num_failed_guesses == self.MAX_FAILED_GUESSES:
            self = self._perform_end_game_updates('L')

        self.current_word = word
        self.turns_taken += 1
        self.letters_played += character
        # self.letters_played = self._get_string_union(word, self.letters_played)
        indices = self._get_character_indices(self.winning_word, character)
        current_word_list = list(self.current_word)
        for index in indices:
            current_word_list[index] = character
        self.current_word = "".join(current_word_list)
        self.save()

    def _perform_end_game_updates(self, new_state):
        """
        Return the updated Game instance.

        Update game_state with new_state,
        increment games_played and reset active_game in related UserHistory.
        """
        self.game_state = new_state
        self.user_history.games_played += 1
        self.user_history.active_game_id = None
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

    def _get_string_union(self, string1, string2):
        """
        Return a new string
        containing all of the letters
        in the two passed strings, unordered.
        """
        return "".join(set(list(string1)) | set(list(string2)))

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
    """
    objects = WordManager()
    word_text = models.CharField(max_length=25)
