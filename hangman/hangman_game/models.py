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
    def create_game(self):
        """
        Create a new game instance.
        """
        found_word = Word.objects.random().word_text
        game = self.create(winning_word=found_word)
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
        Return True if win/lose conditions are met.
        Otherwise return False.


        Peform operations related to updating a turn.
        Check for win/lose conditions,
        updating game_state accordingly.

        If the game isn't over:
        update the current_word with the passed value
        and increment the turn counter.

        In either case, update the letters-played list.
        """
        # kept all in one method
        # to reduce calls to save()/db access.
        game_is_over = False
        if word == self.winning_word:
            self.game_state = 'W'
            self.user_history.games_won += 1
            game_is_over = True

        elif self.num_failed_guesses == self.MAX_FAILED_GUESSES: # account for 0-index
            self.game_state = 'L'
            self.user_history.games_won += 1
            self.user_history.active_game = None
            game_is_over = True

        else:
            if character not in self.winning_word:
                self.nume_failed_guesses+=1

            self.current_word = word
            self.turns_taken += 1

        self.letters_played = self._get_string_union(word, self.letters_played)
        self.save()
        return game_is_over

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
