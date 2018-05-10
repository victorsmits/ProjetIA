#!/usr/bin/env python3
# quarto.py
# Author: Quentin Lurkin
# Version: March 29, 2018

import argparse
import copy
import datetime
import json
import random
import time

from random import randint
from easyAI import TwoPlayersGame, AI_Player
from easyAI.AI import Negamax, TT
from easyAI.AI.solving import id_solve
from lib import game

server_time = []


# State of the game
class QuartoState(game.GameState):
    '''Class representing a state for the Quarto game.'''

    def __init__(self, initialstate=None, currentPlayer=None):
        self.__player = 0
        random.seed()
        if initialstate is None:
            pieces = []
            for shape in ['round', 'square']:
                for color in ['dark', 'light']:
                    for height in ['low', 'high']:
                        for filling in ['empty', 'full']:
                            pieces.append({
                                'shape': shape,
                                'color': color,
                                'height': height,
                                'filling': filling
                            })
            initialstate = {
                'board': [None] * 16,
                'remainingPieces': pieces,
                'pieceToPlay': None,
                'quartoAnnounced': False
            }

        if currentPlayer is None:
            currentPlayer = random.randrange(2)

        super().__init__(initialstate, currentPlayer=currentPlayer)

    def applymove(self, move):
        # {pos: 8, quarto: true, nextPiece: 2}
        stateBackup = copy.deepcopy(self._state)
        try:
            state = self._state['visible']
            if state['pieceToPlay'] is not None:
                try:
                    if state['board'][move['pos']] is not None:
                        raise game.InvalidMoveException('The position is not free')
                    state['board'][move['pos']] = state['remainingPieces'][state['pieceToPlay']]
                    del (state['remainingPieces'][state['pieceToPlay']])
                except game.InvalidMoveException as e:
                    raise e
                except:
                    raise game.InvalidMoveException("Your move should contain a \"pos\" key in range(16)")

            if len(state['remainingPieces']) > 0:
                try:
                    state['pieceToPlay'] = move['nextPiece']
                except:
                    raise game.InvalidMoveException("You must specify the next piece to play")
            else:
                state['pieceToPlay'] = None

            if 'quarto' in move:
                state['quartoAnnounced'] = move['quarto']
                winner = self.winner()
                if winner is 2 or winner == -1:
                    raise game.InvalidMoveException("There is no Quarto !")
            else:
                state['quartoAnnounced'] = False
        except game.InvalidMoveException as e:
            self._state = stateBackup
            raise e

    def _same(self, feature, elems):
        try:
            elems = list(map(lambda piece: piece[feature], elems))
        except:
            return False
        return all(e == elems[0] for e in elems)

    def _quarto(self, elems):
        return self._same('shape', elems) or self._same('color', elems) or self._same('filling', elems) or self._same(
            'height', elems)

    def winner(self):
        state = self._state['visible']
        board = state['board']
        player = self._state['currentPlayer']

        # 00 01 02 03
        # 04 05 06 07
        # 08 09 10 11
        # 12 13 14 15

        if state['quartoAnnounced']:
            # Check horizontal and vertical lines
            for i in range(4):
                if self._quarto([board[4 * i + e] for e in range(4)]):
                    return player
                if self._quarto([board[4 * e + i] for e in range(4)]):
                    return player
            # Check diagonals
            if self._quarto([board[5 * e] for e in range(4)]):
                return player
            if self._quarto([board[3 + 3 * e] for e in range(4)]):
                return player
        return 2 if board.count(None) == 0 else -1

    def displayPiece(self, piece):
        if piece is None:
            return " " * 6
        bracket = ('(', ')') if piece['shape'] == "round" else ('[', ']')
        filling = 'E' if piece['filling'] == 'empty' else 'F'
        color = 'L' if piece['color'] == 'light' else 'D'
        format = ' {}{}{}{} ' if piece['height'] == 'low' else '{0}{0}{1}{2}{3}{3}'
        return format.format(bracket[0], filling, color, bracket[1])

    def prettyprint(self):
        state = self._state['visible']
        print('empty space:', self._state['visible']['board'].count(None))
        print('Board:')
        for row in range(4):
            print('             |', end="")
            for col in range(4):
                print(self.displayPiece(state['board'][row * 4 + col]), end="|")
            print()
        print("00 01 02 03", '\n04 05 06 07', '\n08 09 10 11', '\n12 13 14 15\n')
        print('\nRemaining Pieces:')
        print('len:', len(state['remainingPieces']))
        print(", ".join([self.displayPiece(piece) for piece in state['remainingPieces']]))

        if state['pieceToPlay'] is not None:
            print('\nPiece to Play:')
            print(state['pieceToPlay'])
            print(self.displayPiece(state['remainingPieces'][state['pieceToPlay']]))

        global server_time
        print('\nTimer:')
        self.Timer(server_time)

    def nextPlayer(self):
        self._state['currentPlayer'] = (self._state['currentPlayer'] + 1) % 2

    def Timer(self, old_time):
        old_time.append(time.time())
        if len(old_time) == 1:
            print('start')
        else:
            delta = old_time[-1] - old_time[-2]
            total = old_time[-1] - old_time[0]
            Time_Delta = str(datetime.timedelta(seconds=delta))
            Time_Total = str(datetime.timedelta(seconds=total))
            print('Player {} play in: {}'.format(self._state['currentPlayer'], Time_Delta))
            print('total execution time: {}'.format(Time_Total))


# code server
class QuartoServer(game.GameServer):
    '''Class representing a server for the Quarto game.'''

    def __init__(self, verbose=False):
        super().__init__('Quarto', 2, QuartoState(), verbose=verbose)

    def applymove(self, move):
        try:
            move = json.loads(move)
        except:
            raise game.InvalidMoveException('A valid move must be a valid JSON string')
        else:
            self._state.applymove(move)


# game client 1
class QuartoClient(game.GameClient):
    """Class representing a client for the Quarto game."""

    def __init__(self, name, server, verbose=False):
        super().__init__(server, QuartoState, verbose=verbose)
        self.__name = name

    def _handle(self, message):
        pass

    def _nextmove(self, state):
        # solve the game and give the Move to do it, id_solve return:
        #   • Move: Best Move to play for the player.
        #   • Result: Either 1 (certain victory of the first player) or -1 (certain defeat) or 0 (either draw)
        #   • Depth: The minimal number of moves before victory (or defeat)

        Result, Depth, Move = id_solve(AIClient([], state), ai_depths=range(2, 4), win_score=90)
        return json.dumps(Move)  # send the Move


# game client 2 => use to test the AI
class QuartoClient2(game.GameClient):
    """Class representing a client for the Quarto game."""

    def __init__(self, name, server, verbose=False):
        super().__init__(server, QuartoState, verbose=verbose)
        self.__name = name

    def _handle(self, message):
        pass

    def _nextmove(self, State):
        AIClient.ttentry = lambda self: State       # send State to the Transposition tables
        AI = Negamax(6, tt=TT(), win_score=90)        # Algorithm(depth, scoring=None, win_score=inf,tt=None)
        Quarto = AIClient([AI_Player(AI), AI_Player(AI)], State)
        Move = Quarto.get_move()        # find the best move possible
        return json.dumps(Move)  # send the Move


# easy IA
class AIClient(TwoPlayersGame):
    def __init__(self, players, State):
        self.State = State
        self.players = players
        self.nplayer = 1

    def possible_moves(self):  # génere la liste de tout les coups possible en fonction du plateau
        liste = []
        visible = self.State._state['visible']

        if visible['board'].count(None) == 1:  # si il n'y a plus qu'une place sur le plateau joue la derniere piece
            liste.append({'pos': visible['board'].index(None), 'nextPiece': 0})

        else:
            for i in range(16):
                for n in range(len(visible['remainingPieces']) - 1):
                    move = {}
                    move['pos'] = i
                    move['nextPiece'] = n
                    move['quarto'] = True
                    if visible['board'][i] is None:
                        try:
                            CopyState = copy.deepcopy(self.State)
                            CopyState.applymove(move)
                        except:
                            del (move['quarto'])
                        liste.append(move)
        return liste

    def make_move(self, move):
        position = move['pos']
        visible = self.State._state['visible']
        if visible['board'][position] is None:
            self.State.applymove(move)

    def win(self):
        return self.State.winner()

    def is_over(self):
        return False if self.win() == -1 else True

    def show(self):
        self.State.prettyprint()

    def scoring(self):
        Score = self.win()
        if Score == self.nopponent:
            return 100
        if Score in [-1]:
            return 0
        else:
            return -100


# play against IA
class QuartoUser(game.GameClient):
    """Class representing a client for the Quarto game."""

    def __init__(self, name, server, verbose=False):
        super().__init__(server, QuartoState, verbose=verbose)
        self.__name = name

    def _handle(self, message):
        pass

    def _nextmove(self, state):
        visible = state._state['visible']

        move = {}

        remainingPieces = visible['remainingPieces']
        place = visible['pieceToPlay']

        try:
            pieceToPlay = state.displayPiece(remainingPieces[place])
            if visible['pieceToPlay'] is not None:
                move['pos'] = int(input('Play {} in position: '.format(pieceToPlay)))
        except:
            pass

        # select the first remaining piece
        move['nextPiece'] = int(input('Next Piece: '))

        # apply the move to check for quarto
        # applymove will raise if we announce a quarto while there is not
        move['quarto'] = True

        try:
            state.applymove(move)

        except:
            del (move['quarto'])

        # send the move
        return json.dumps(move)


# random AI
class QuartoRandom(game.GameClient):
    """Class representing a client for the Quarto game."""

    def __init__(self, name, server, verbose=False):
        super().__init__(server, QuartoState, verbose=verbose)
        self.__name = name

    def _handle(self, message):
        pass

    def _nextmove(self, state):
        visible = state._state['visible']
        move = {}

        remainingPieces = visible['remainingPieces']
        x = randint(0, (len(remainingPieces) - 2))

        if visible['pieceToPlay'] is not None:
            y = randint(0, 15)
            move['pos'] = y

        move['nextPiece'] = x

        move['quarto'] = True
        try:
            state.applymove(move)
        except:
            del (move['quarto'])

        return json.dumps(move)


# code client d'origine
class ProfAI(game.GameClient):
    '''Class representing a client for the Quarto game.'''

    def __init__(self, name, server, verbose=False):
        super().__init__(server, QuartoState, verbose=verbose)
        self.__name = name

    def _handle(self, message):
        pass

    def _nextmove(self, state):
        visible = state._state['visible']
        move = {}

        # select the first free position
        if visible['pieceToPlay'] is not None:
            move['pos'] = visible['board'].index(None)

        # select the first remaining piece
        move['nextPiece'] = 0

        # apply the move to check for quarto
        # applymove will raise if we announce a quarto while there is not
        move['quarto'] = True
        try:
            state.applymove(move)
        except:
            del (move['quarto'])

        # send the move
        return json.dumps(move)


if __name__ == '__main__':

    # Create the top-level parser
    parser = argparse.ArgumentParser(description='Quarto game')
    subparsers = parser.add_subparsers(description='server client clientB user AI rdm prof',
                                       help='Quarto game components',
                                       dest='component')

    # Create the parser for the 'server' subcommand
    server_parser = subparsers.add_parser('server', help='launch a server')
    server_parser.add_argument('--host', help='hostname (default: localhost)', default='localhost')
    server_parser.add_argument('--port', help='port to listen on (default: 5000)', default=5000)
    server_parser.add_argument('--verbose', action='store_true')

    # Create the parser for the 'client' subcommand
    client_parser = subparsers.add_parser('client', help='launch a client')
    client_parser.add_argument('name', help='name of the player')
    client_parser.add_argument('--host', help='hostname of the server (default: localhost)', default='127.0.0.1')
    client_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
    client_parser.add_argument('--verbose', action='store_true')

    # Create the parser for the 'clientB' subcommand
    client2_parser = subparsers.add_parser('clientB', help='launch a client')
    client2_parser.add_argument('name', help='name of the player')
    client2_parser.add_argument('--host', help='hostname of the server (default: localhost)', default='127.0.0.1')
    client2_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
    client2_parser.add_argument('--verbose', action='store_true')

    # Create the parser for the 'user' subcommand
    user_parser = subparsers.add_parser('user', help='launch a user')
    user_parser.add_argument('name', help='name of the player')
    user_parser.add_argument('--host', help='hostname of the server (default: localhost)', default='127.0.0.1')
    user_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
    user_parser.add_argument('--verbose', action='store_true')

    # Create the parser for the '2 AI games' subcommand
    AI_parser = subparsers.add_parser('ai', help='launch a ai client')
    AI_parser.add_argument('--verbose', action='store_true')

    # Create the parser for the 'random AI' subcommand
    rdm_parser = subparsers.add_parser('rdm', help='launch a random ai')
    rdm_parser.add_argument('name', help='name of the player')
    rdm_parser.add_argument('--host', help='hostname of the server (default: localhost)', default='127.0.0.1')
    rdm_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
    rdm_parser.add_argument('--verbose', action='store_true')

    # Create the parser for the 'prof' subcommand
    prof_parser = subparsers.add_parser('prof', help='launch a random ai')
    prof_parser.add_argument('name', help='name of the player')
    prof_parser.add_argument('--host', help='hostname of the server (default: localhost)', default='127.0.0.1')
    prof_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
    prof_parser.add_argument('--verbose', action='store_true')

    # Parse the arguments of sys.args
    args = parser.parse_args()
    if args.component == 'server':
        QuartoServer(verbose=args.verbose).run()

    if args.component == 'client':
        QuartoClient(args.name, (args.host, args.port), verbose=args.verbose)

    if args.component == 'clientB':
        QuartoClient2(args.name, (args.host, args.port), verbose=args.verbose)

    if args.component == 'rdm':
        QuartoRandom(args.name, (args.host, args.port), verbose=args.verbose)

    if args.component == 'prof':
        ProfAI(args.name, (args.host, args.port), verbose=args.verbose)

    if args.component == 'ai':
        state = QuartoState()
        result, depth, move = id_solve(AIClient([], state), ai_depths=range(2, 4), win_score=90)
        print('result =', result)
        print('depth =', depth)
        print('move =', move)
        # quarto.play()

    if args.component == 'user':
        QuartoUser(args.name, (args.host, args.port), verbose=args.verbose)
