from pyknow import *
from pyknow.fact import *
import random


class ScoreBoard(Fact):
    win = Field(int, default=0)
    lose = Field(int, default=0)
    tie = Field(int, default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Action(Fact):
    pass


class Results(Fact):
    winner = Field(str, mandatory=True)
    loser = Field(str, mandatory=True)
    why = Field(str, mandatory=True)


class ValidAnswer(Fact):
    answer = Field(str, mandatory=True)
    key = Field(str, mandatory=True)


class PlayerChoice(Action):
    key = Field(str, mandatory=True)


class Move(Action):
    role = Field(str, mandatory=True)
    answer = Field(str, mandatory=True)


class Quit(Action):
    quit = Field(str, mandatory=True)


def logger(func):
    def inner(*args, **kwargs):
        print(f'calling {func.__name__} with args={args} and kwargs={kwargs}')
        return func(*args, **kwargs)
    return inner


class RockPaperScissorsGame(KnowledgeEngine):
    @DefFacts()
    def game_rules(self):
        """Declare game rules and valid input keys for the user."""
        self.valid_answers = dict()

        yield ScoreBoard(win=0, lose=0, tie=0)
        yield Results(winner='rock👊', loser='scissors✌', why='Rock👊 smashes scissors✌')
        yield Results(winner='paper👋', loser='rock👊', why='Paper👋 covers rock👊')
        yield Results(winner='scissors✌', loser='paper👋', why='Scissors✌ cut paper👋')
        yield ValidAnswer(answer='rock👊', key='r')
        yield ValidAnswer(answer='paper👋', key='p')
        yield ValidAnswer(answer='scissors✌', key='s')

    @Rule(NOT(Action()),
          ValidAnswer(answer=MATCH.answer, key=MATCH.key))
    @logger
    def store_valid_answers(self, answer, key):
        self.valid_answers[key] = answer

    @Rule(AS.event1 << Action('get-player-move'))
    # @logger
    def get_player_move(self, event1):
        self.retract(event1)

        move = input(
            'please input your choice (R) for Rock, (S) for Scissor, (P) for Paper\n')
        choice = move.lower()
        print(choice)
        self.declare(PlayerChoice(key=choice))
        # if choice in self.valid_answers:
        #     answer = self.valid_answers[choice]
        #     self.declare(
        #         Move(answer=answer, role='player'))
        # else:
        #     self.declare(Action('get-player-move'))

    @Rule(AS.event << PlayerChoice(key=MATCH.choice),
          ValidAnswer(key=MATCH.choice, answer=MATCH.answer))
    def player_move(self, event, answer):
        self.retract(event)

        self.declare(Move(answer=answer, role='player'))

    @Rule(AS.event << PlayerChoice(key=MATCH._choice),
          NOT(ValidAnswer(key=MATCH._choice)))
    # @logger
    def player_bad_move(self, event):
        self.retract(event)

        print("Wrong input")
        self.declare(Action('get-player-move'))

    @Rule(Move(role='player'))
    # @logger
    def get_computer_action(self):
        choice = random.choice(list(self.valid_answers))
        self.declare(Move(answer=self.valid_answers[choice], role='computer'))

    @Rule(AS.e2 << Move(answer=MATCH.player_answer, role='player'),
          AS.e3 << Move(answer=MATCH.computer_answer, role='computer'))
    def both_showed(self, player_answer, computer_answer):
        print(
            f'You showed {player_answer} and computer showed {computer_answer}')
        self.declare(Action('Judge'))

    @Rule(AS.e1 << Action('Judge'),
          AS.e2 << Move(answer=MATCH.player_answer, role='player'),
          AS.e3 << Move(answer=MATCH.computer_answer, role='computer'),
          AS.board << ScoreBoard(win=MATCH.wins),
          Results(winner=MATCH.player_answer,
                  loser=MATCH.computer_answer,
                  why=MATCH.explaination))
    # @logger
    def player_win(self, e1, e2, e3, board, explaination, wins):
        self.retract(e1)
        self.retract(e2)
        self.retract(e3)

        self.modify(board, win=wins + 1)
        print(f'You win! {explaination}')
        self.declare(Action('game-over'))

    @Rule(AS.e1 << Action('Judge'),
          AS.e2 << Move(answer=MATCH.player_answer, role='player'),
          AS.e3 << Move(answer=MATCH.computer_answer, role='computer'),
          AS.board << ScoreBoard(lose=MATCH.loses),
          Results(winner=MATCH.computer_answer,
                  loser=MATCH.player_answer,
                  why=MATCH.explaination))
    # @logger
    def computer_win(self, e1, e2, e3, board, explaination, loses):
        self.retract(e1)
        self.retract(e2)
        self.retract(e3)

        print(f'Computer wins! {explaination}')
        self.modify(board, lose=loses + 1)
        self.declare(Action('game-over'))

    @Rule(AS.e1 << Action('Judge'),
          AS.e2 << Move(answer=MATCH.player_answer, role='player'),
          AS.e3 << Move(answer=MATCH.computer_answer, role='computer'),
          NOT(Results(winner=MATCH.computer_answer,
                  loser=MATCH.player_answer)),
          NOT(Results(winner=MATCH.computer_answer,
                  loser=MATCH.computer_answer)),                  
          AS.board << ScoreBoard(tie=MATCH.ties))
    def tie(self, e1, e2, e3, board, ties):
        self.retract(e1)
        self.retract(e2)
        self.retract(e3)

        print('tie')
        self.modify(board, tie=ties + 1)
        self.declare(Action('game-over'))

    @Rule(AS.e << Action('game-over'),
          AS.board << ScoreBoard(lose=MATCH.loses, win=MATCH.wins, tie=MATCH.ties))
    def game_over(self, e, board, loses, wins, ties):
        self.retract(e)
        total = loses + wins + ties
        print(
            f'You have played {total} times, {wins} wins, {loses} loses and {ties} ties.')
        print('Would you like to play again?')

        choice = input("Please input N to leave, otherwise continue")

        self.declare(Quit(quit=choice.lower()))

    @Rule(AS.e << Quit(quit='n'))
    def quit(self, e):
        self.retract(e)
        print("I will miss you! Good bye!")
        self.halt()

    @Rule(AS.e << Quit(),
          NOT(Quit(quit='n')))
    def play_again(self, e):
        self.retract(e)
        self.declare(Action('get-player-move'))

    @Rule()
    @logger
    def startup(self):
        print("Lets play rock-paper-scissors!")
        # self.declare(WinTotals(human=0, computer=0, ties=0))
        self.declare(Action('get-player-move'))
        self.declare(Action('game-started'))


rps = RockPaperScissorsGame()
rps.reset()
rps.run()

print(rps.facts)
# print(rps.get_rules())
