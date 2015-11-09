import unittest
import random

_colors = {"green": range(12, 0, -1), "blue": range(12, 0, -1), "yellow": range(2, 14, 1), "red": range(2, 14, 1)}


class TestRow(unittest.TestCase):
    def test_row_check(self):
        myRow = row("yellow")
        myRow.check(2)

        self.assertEqual('#'.join(str(i) for i in myRow._slots),
                         'X#3#4#5#6#7#8#9#10#11#12#13',
                         'Check 1st element appears not to work')

        myRow.check(4)
        self.assertEqual('#'.join(str(i) for i in myRow._slots),
                         'X#3#X#5#6#7#8#9#10#11#12#13',
                         'Check nth element appears not to work n=4')

    def test_row_complete(self):
        myRow = row("yellow")
        with self.assertRaises(Exception) as contextMgr:
            myRow.check(2)
            myRow.check(7)
            myRow.check(8)
            myRow.check(9)
            myRow.check(11)
            myRow.check(12)

        self.assertEqual("Row is closed", contextMgr.exception.args[0])
        myRowRev = row("blue")
        with self.assertRaises(Exception) as contextMgr:
            myRowRev.check(12)
            myRowRev.check(11)
            myRowRev.check(6)
            myRowRev.check(5)
            myRowRev.check(3)
            myRowRev.check(2)

        self.assertEqual("Row is closed", contextMgr.exception.args[0])

    def test_invalid_complete(self):
        myRow = row("yellow")
        with self.assertRaises(ValueError) as contextMgr:
            myRow.check(2)
            myRow.check(7)
            myRow.check(12)

        self.assertEqual("Row cannot be closed yet", contextMgr.exception.args[0])

        myRowRev = row("blue")

        with self.assertRaises(ValueError) as contextMgr:
            myRowRev.check(12)
            myRowRev.check(8)
            myRowRev.check(2)

        self.assertEqual("Row cannot be closed yet", contextMgr.exception.args[0])

    def test_invalid_slot(self):
        myRow = row("green")
        with self.assertRaises(ValueError) as contextMgr:
            myRow.check(6)
            myRow.check(3)
            myRow.check(4)
        self.assertEqual("Invalid slot number", contextMgr.exception.args[0])
        myRow = row("red")
        with self.assertRaises(ValueError) as contextMgr:
            myRow.check(13)
        self.assertEqual("Invalid slot number", contextMgr.exception.args[0])

        myRowRev = row("green")

        with self.assertRaises(ValueError) as contextMgr:
            myRowRev.check(12)
            myRowRev.check(12)

        self.assertEqual("Invalid slot number", contextMgr.exception.args[0])

    def test_score(self):

        # test all values apart from 66
        myRow = row("green")

        self.assertEqual(0, myRow.score(), "empty row is 0 points")
        increment = 0
        for pts in (1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 78):
            try:
                myRow.check(12 - increment)
            except(Exception) as e:
                if e.args[0] == "Row is closed":
                    pass
                else:
                    raise
            increment += 1

            self.assertEqual(myRow.score(), pts, "row with {} checks is {} points".format(increment, pts))

        # test 66 works
        myRow = row("yellow")
        increment = 0
        for pts in (1, 3, 6, 10, 15, 21, 28, 36, 45, 66):
            try:
                myRow.check(3 + increment)
            except(Exception) as e:
                if e.args[0] == "Row is closed":
                    pass
                else:
                    raise
            increment += 1

            self.assertEqual(myRow.score(), pts, "row with {} checks is {} points".format(increment, pts))


class row:
    def __init__(self, color, minToClose=5):
        """

        :type color: one of the keys from __colors
        """
        self._color = color
        self._slots = list(_colors[color])
        self._max = len(self._slots) - 2
        self._minToClose = minToClose
        self._last = -1
        self._count = 0

    def _getSlot(self, value):
        try:
            return self._slots.index(value)
        except:
            return -1

    def check(self, value):
        slot = self._getSlot(value)

        if slot > self._max or slot <= self._last:
            raise ValueError("Invalid slot number")

        if slot == self._max and self._count < self._minToClose:
            raise ValueError("Row cannot be closed yet")

        self._slots[slot] = 'X'
        self._last = slot
        self._count += 1

        if self._last == self._max:
            self._slots[slot + 1] = 'X'
            self._count += 1
            raise Exception('Row is closed')

    def score(self):
        score = 0
        for i in range(1, self._count + 1):
            score += i
        return score


class TestPlayer(unittest.TestCase):
    def test_player_init(self):
        myPlayer = Player()
        self.assertEqual(myPlayer.name, 'player-1', 'default player name')

        self.assertIsInstance(myPlayer.yellow, row)
        self.assertIsInstance(myPlayer.blue, row)
        self.assertIsInstance(myPlayer.green, row)
        self.assertIsInstance(myPlayer.red, row)

        with self.assertRaises(Exception):
            try:
                myPlayer.yellow.check(5)
                myPlayer.blue.check(4)
            except(Exception) as e:
                print("Exception {} was raised by check".format(e.args[0]))
                pass
            else:
                raise (Exception)

        myOtherPlayer = Player('Arnaud')
        self.assertEqual(myOtherPlayer.name, 'Arnaud', 'player name: Arnaud')

        myThirdPlayer = Player()
        self.assertEqual(myThirdPlayer.name, 'player-3', 'default player name: player-3')

    def test_player_maxfails(self):
        myPlayer = Player()
        with self.assertRaises(Exception):
            try:
                myPlayer.fail()
                myPlayer.fail()
                myPlayer.fail()
            except(Exception) as e:
                print("Exception {} was raised by one of the first 3 fails".format(e.args[0]))
                pass
            else:
                raise (Exception)
        with self.assertRaises(Exception) as cm:
            myPlayer.fail()
        self.assertEqual("Maximum failures reached", cm.exception.args[0])


class Player:
    _count = 0

    @staticmethod
    def reset():
        Player._count = 0

    def __init__(self, name=False, maximumFailures=4):
        Player._count += 1
        if name:
            self.name = name
        else:
            self.name = "player-" + str(Player._count)
        for color in _colors:
            self.__dict__[color] = row(color)

        self._fails = 0
        self._maxFail = maximumFailures

    def fail(self):
        self._fails += 1
        if self._fails == self._maxFail:
            raise Exception("Maximum failures reached")

def testSetupPlayer(self, players, **settings):
        self._players.append(Player("test-1", **settings))
        self._players.append(Player("test-2", **settings))
        self._players.append(Player("test-3", **settings))
        self._players.append(Player("test-4", **settings))

class TestGame(unittest.TestCase):

     def setValue(self):
         myGame = Game(2)
         myGame._state = 'WHITE'
         self.assertRaises(myGame.setValue('blah'),ValueError)

     def test_init_game(self):
        Game.setupPlayer = testSetupPlayer
        myGame = Game(4)
        self.assertEqual(myGame._state, 'ROLL')
        myGame.play()
        self.assertTrue(7 > myGame._colored_dices['blue'] > 0)
        self.assertTrue(7 > myGame._colored_dices['yellow'] > 0)
        self.assertTrue(7 > myGame._colored_dices['green'] > 0)
        self.assertTrue(7 > myGame._colored_dices['red'] > 0)
        self.assertEqual(myGame._state, 'WHITE')
        self.assertEqual('#'.join(myGame.valuesToSet()), 'white-color')
        myGame.play()
        self.assertEqual(myGame._state, 'WHITE')
        myGame.play()
        self.assertEqual(myGame._state, 'WHITE')
        myGame.play()
        self.assertEqual(myGame._state, 'WHITE')
        myGame.play()
        self.assertEqual(myGame._state, 'TOKENPLAYER')
        self.assertEqual('#'.join(myGame.valuesToSet()), 'colored-white-dice#colored-dice')
        myGame.play()
        self.assertEqual(myGame._state, 'ROLL')

     def tearDown(self):
        Player.reset()
        pass


class Game:
    def __init__(self, players=4, **settings):
        self._plays = {'ROLL': self._play_roll, 'WHITE': self._play_white, 'TOKENPLAYER': self._play_token_player,
                       'SCORE': self._play_score}

        self._numOfPlayers = players
        self._players = []
        self._status = {}
        self._round = 0
        self._dices = {}
        for col in _colors.keys():
            self._status[col] = True

        self.setupPlayer(players, **settings)
        self._state = 'ROLL'

    def valuesToSet(self):
        return self._plays[self._state].dices.keys()

    def setValue(self,param,value):
        if param in self.valuesToSet():
            self._plays[self._state].dices[param] = value
        else:
            raise ValueError('Invalid Parameter for this state : {}'.format(self._state))

    def setupPlayer(self, players, **settings):
        for i in range(1, players + 1):
            playerName = input("Enter name of player {} :".format(i))
            self._players.append(Player(playerName, **settings))

    def run(self):
        while self._state != "END":

            showTable = len(self.valuesToSet())
            if showTable:
                print("player : {}".format(self._currentPlayer.name))
                print("yellow: " + '#'.join(str(i) for i in self._currentPlayer.yellow._slots))
                print("red: " + '#'.join(str(i) for i in self._currentPlayer.red._slots))
                print("blue: " + '#'.join(str(i) for i in self._currentPlayer.blue._slots))
                print("green: " + '#'.join(str(i) for i in self._currentPlayer.green._slots))

            for param in self._plays[self._state].dices.keys():
                print(self.__dict__["_{}_dices".format(Game._map[param])])

            for param in self.valuesToSet():
                self._plays[self._state].dices[param] = self._chooseColor(param)

            self.play()

            if showTable:
                print("yellow: " + '#'.join(str(i) for i in self._currentPlayer.yellow._slots))
                print("red: " + '#'.join(str(i) for i in self._currentPlayer.red._slots))
                print("blue: " + '#'.join(str(i) for i in self._currentPlayer.blue._slots))
                print("green: " + '#'.join(str(i) for i in self._currentPlayer.green._slots))

            #            print ( "{} : {}  ".format(dice,self._dices[dice]) for dice in self._dices.keys() )

    def play(self, *args):
        self._plays[self._state](*args)

    def _roll_dices(self):
        self._colored_dices = {color: random.randint(1, 6) for color in self._status.keys() if
                               self._status.get(color, True)}
        self._white_dices = {color: random.randint(1, 6) for color in ['white-1', 'white-2']}

    def _play_roll(self, color=None):
        self._round += 1
        self._player_num = self._round % self._numOfPlayers
        self._tokenPlayer = self._players[self._player_num]
        self._currentPlayer = self._tokenPlayer
        self._close = {}
        self._played = {}
        self._roll_dices()
        self._state = 'WHITE'

    def _next_player(self):
        self._player_num = (self._player_num + 1) % self._numOfPlayers
        self._currentPlayer = self._players[self._player_num]
        if self._currentPlayer == self._tokenPlayer:
            raise Exception('Last Player')

    def _play_white(self):
        white = Game._play_white.dices['white-color']
        if white:
            try:
                value = self._getDiceValue('white-1') + self._getDiceValue('white-2')
                self._currentPlayer.__dict__[white].check(int(value))
                self._played[self._currentPlayer] = True
            except Exception as e:
                if e.args[0] == 'Row is closed':
                    self._close[white] = False
                else:
                    raise
        try:
            self._next_player()
        except Exception as e:
            if e.args[0] == 'Last Player':
                self._status.update(**self._close)
                self._state = 'TOKENPLAYER' if len(
                    [color for color in self._status if not (self._status[color])]) < 2 else 'SCORE'
            else:
                raise

    def _play_token_player(self):
        colored = Game._play_token_player.dices['colored-dice']
        white = Game._play_token_player.dices['colored-white-dice']
        try:
            if colored and self._status[colored]:
                try:
                    value = self._getDiceValue(colored) + self._getDiceValue(white)
                    self._tokenPlayer.__dict__[colored].check(int(value))
                except(Exception) as e:
                    if e.args[0] == 'Row is closed':
                        self._status[colored] = False
                    else:
                        raise
            elif not (self._played.setdefault(self._tokenPlayer, False)):
                self._tokenPlayer.fail()
            self._state = 'ROLL' if len([color for color in self._status if not (self._status[color])]) < 2 else 'SCORE'
        except(Exception) as e:
            if e.args[0] == "Maximum failures reached":
                self._state = 'SCORE'
            else:
                raise

    def _play_score(self):
        self._dices = {}
        for player in self._players:
            print("player {} your score is {}".format(player.name, sum(
                player.__dict__[color].score() for color in _colors.keys()) - 5 * player._fails))
        self._state = 'END'

    _play_white.dices = {"white-color": None}
    _play_score.dices = {}
    _play_token_player.dices = {"colored-dice": None, "colored-white-dice": None}
    _play_roll.dices = {}
    _map = {"white-color": "white", "colored-dice": "colored", "colored-white-dice": "white"}

    def _getDiceValue(self, color):
        dices = self._colored_dices if _colors.get(color, False) else self._white_dices
        return dices[color]

    def _chooseColor(self, color):
        white = input("{} enter value for {} : ".format(self._currentPlayer.name, color))
        return white


if __name__ == "__main__":
    #unittest.main()
    Game(2).run()
