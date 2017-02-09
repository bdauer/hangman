from django.test import TestCase

from .models import GameManager, Game, UserHistory, WordManager, Word
# Create your tests here.

class GameManagerTestCases(TestCase):

    def setUp(self):
        Word.objects.create(word_text="fuzzypickles")

    def test_create_game(self):

        new_game = Game.objects.create()
        self.assertEqual(new_game.winning_word, "fuzzypickles")


class GameTestCases(TestCase):

    def setUp(self):
        Game.objects.create(pk=1, turns_taken=2, winning_word="fuzzypickles")

    def test_turns_remaining(self):
        """
        Test that turns_remaining calculates the difference between
        TOTAL_TURNS and turns_taken.
        """

        game = Game.objects.get(pk=1)
        self.assertEqual(game.turns_remaining, 8)

    def test_update_turn(word):

        game = Game.objects.get(pk=1)
        # verify initial state
        self.assertEqual(game.game_state, 'A')
        self.assertEqual(game.turns_taken, 2)
        self.assertEqual(game.letters_played, "")

        # test failed word
        game.update_turn("fuzzy")
        self.assertEqual(game.game_state, 'A')
        self.assertEqual(game.turns_taken, 3)
        self.assertEqual(set(list("fuzzy")), set(list(game.letters_played)))

        # test unmatching letters in word.
        game.update_turn("foyer")
        self.assertEqual(set(list("fuzyoer")), set(list(game.letters_played)))
        self.assertEqual(game.turns_taken, 4)

        # test winning condition met
        game.update_turn("fuzzypickles")
        self.assertEqual(game.game_state, 'W')
        self.assertEqual(game.turns_taken, 4)

        game.game_state = 'A'

        game.update_turn("f")
        game.update_turn("f")
        game.update_turn("f")
        game.update_turn("f")
        game.update_turn("f")
        game.update_turn("f")

        # test losing condition met
        self.assertEqual(game.game_state, 'L')


class UserHistoryTestCases(TestCase):

    def setUp(self):
        UserHistory.objects.create(pk=1, games_played=5, games_won=3)

    def test_games_lost(self):
        """
        Test that games lost returns games_played - games_won.
        """
        history = UserHistory.objects.get(pk=1)
        self.assertEqual(history.games_lost(), 2)


class WordManagerTestCases(TestCase):

    def setUp(self):
        Word.objects.create(word_text="fuzzypickles")

    def test_random(self):
        """
        Test that random returns the word in the database.
        """
        self.assertEqual(Word.objects.random(), "fuzzypickles")
        # I'm a little unsure of how to test a random output for a larger table.
