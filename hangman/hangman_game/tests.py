from django.test import TestCase

from .models import GameManager, Game, UserHistory, WordManager, Word
# Create your tests here.

class GameManagerTestCases(TestCase):

    def setUp(self):
        Word.objects.create(word_text="fuzzypickles")
        UserHistory.objects.create()

    def test_create_game(self):
        uh = UserHistory.objects.get(pk=1)
        new_game = Game.objects.create_game(uh)
        self.assertEqual(new_game.winning_word, "fuzzypickles")


class GameTestCases(TestCase):

    def setUp(self):
        Word.objects.create(word_text="fuzzypickles")
        uh = UserHistory.objects.create()
        new_game = Game.objects.create_game(uh)
        new_game.save()

    def test_update_turn(self):

        game = Game.objects.get(pk=1)
        # verify initial state
        self.assertEqual(game.game_state, 'A')
        self.assertEqual(game.turns_taken, 0)
        self.assertEqual(game.letters_played, "")

        # test failed word
        game.update_turn("f")
        game.save()
        self.assertEqual(game.game_state, 'A')
        self.assertEqual(game.turns_taken, 1)
        self.assertEqual(set(list("f")), set(list(game.letters_played)))

        # test unmatching letters in word.
        game.update_turn("f")
        self.assertEqual(set(list("f")), set(list(game.letters_played)))
        self.assertEqual(game.game_state, 'A')
        self.assertEqual(game.turns_taken, 2)

        # test winning condition met
        game.update_turn("u")
        game.update_turn("z")
        game.update_turn("y")
        game.update_turn("p")
        game.update_turn("i")
        game.update_turn("c")
        game.update_turn("k")
        game.update_turn("l")
        game.update_turn("e")
        game.update_turn("s")
        self.assertEqual(game.game_state, 'W')

        # reset game state
        game.game_state = 'A'

        # test num_failed_guesses
        game.update_turn("a")
        self.assertEqual(game.num_failed_guesses, 1)

        # test matching indices returned with one match.
        self.assertEqual(game.update_turn("f"), True)

        # test matching indices returned with two matches.
        self.assertEqual(game.update_turn("z"), True)

        # test matching indices returned with zero matches.
        self.assertEqual(game.update_turn("x"), False)

        # create losing condition
        game.update_turn("a")
        game.update_turn("a")
        game.update_turn("a")
        game.update_turn("a")
        game.update_turn("a")
        game.update_turn("a")
        game.update_turn("a")
        game.update_turn("a")
        game.update_turn("a")

        # test losing condition met
        self.assertEqual(game.game_state, 'L')

    def test_letters_remaining(self):
        """
        Test that it returns all remaining letters after having played a few.
        """
        uh = UserHistory.objects.get(pk=1)
        new_game = Game.objects.create_game(uh)
        new_game.letters_played = "abc"
        new_game.save()
        remaining_letters = ['d', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                             'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
                             'x', 'y', 'z']
        self.assertEqual(new_game.letters_remaining(), remaining_letters)

class UserHistoryTestCases(TestCase):

    def setUp(self):

        UserHistory.objects.create(pk=1, games_played=5,
                                   games_won=3)

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
        random_word = Word.objects.random()
        self.assertEqual(random_word.word_text, "fuzzypickles")
        # I'm a little unsure of how to test a random output for a larger table.
