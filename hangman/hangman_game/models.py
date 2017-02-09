from django.db import models
import random

# Create your models here.

class GameManager(models.Manager):
    """
    Manager for the Game class.
    """
    def create_game(self):
        """
        Create a new game instance.
        """
        found_word = Word.objects.random()
        game = self.create(winning_word=found_word)
        return game

class Game(models.Model):
    """
    Represents one game of hangman.
    TOTAL_TURNS: the maximum number of turns in a game.
    wining_word: the word that the player must guess.
    current word: the player's current guess.
    turns_taken: the number of turns taken so far.
    letters_played: the letters a user has guessed.
    """
    objects = GameManager()
    TOTAL_TURNS = 10
    # max word length in current words.txt is 25.
    # if another word list is substituted,
    # may need to increase max_length for the following two fields.
    winning_word = models.CharField(max_length=25)
    current_word = models.CharField(max_length=25)
    turns_taken = models.SmallIntegerField(default=0)
    letters_played = models.CharField(max_length=10)

    GAME_STATES = ( ('A', 'active'),
                    ('W', 'won'),
                    ('L', 'lost'),)
    game_state = models.CharField(max_length=1,
                                  choices=GAME_STATES,
                                  default='A')

    def turns_remaining():
        """
        Return the remaining number of turns.
        """
        return self.TOTAL_TURNS - self.turns_taken

    def update_turn(self, word):
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
            game_is_over = True

        elif self.turns_taken == 10:
            self.game_state = 'L'
            game_is_over = True

        else:
            self.current_word = word
            self.turns_taken += 1

        self.letters_played = self._get_string_union(word, self.letters_played)
        self.save()
        return game_is_over

    def _get_string_union(self, string1, string2):
        """
        Return a new string
        containing all of the letters
        in the two passed strings, unordered.
        """
        return "".join(set(list(string1)) | set(list(string2)))


class UserHistory(models.Model):
    """
    Represents a user's history.
    """
    games_played = models.SmallIntegerField(default=0)
    games_won = models.SmallIntegerField(default=0)
    current_game = models.ForeignKey(Game, blank=True, null=True)
    user_ip = models.GenericIPAddressField(blank=True, null=True)

    def games_lost(self):
        """
        Return the number of games lost
        for a user.
        """
        return self.games_played - self.games_won

class WordManager(models.Manager):
    """
    Manager for the Word model.
    """

    def random(self):
        """
        Return a random word.
        """
        count = self.aggregate(count=models.Count('id'))['count']
        random_index = random.randint(0, count - 1)
        return self.all()[random_index]

class Word(models.Model):
    """
    Each row represents one word in the word list.
    """
    objects = WordManager()
    word_text = models.CharField(max_length=25)
