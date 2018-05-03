#!/usr/bin/env python3
# quarto.py
# Author: Quentin Lurkin
# Version: March 29, 2018

import argparse
import socket
import sys
import random
from random import randint
import json
from easyAI import TwoPlayersGame, AI_Player, Negamax, Human_Player, SSS
from lib import game


class QuartoState(game.GameState):
    """Class representing a state for the Quarto game."""

    def __init__(self, initialstate=None):
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

        super().__init__(initialstate)

    def setPlayer(self, player):
        self.__player = player

    def applymove(self, move):
        # {pos: 8, quarto: true, nextPiece: 2}
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

        try:
            state['pieceToPlay'] = move['nextPiece']
        except:
            raise game.InvalidMoveException("You must specify the next piece to play")

        if 'quarto' in move:
            state['quartoAnnounced'] = move['quarto']
            winner = self.winner()
            if winner is None or winner == -1:
                raise game.InvalidMoveException("There is no Quarto !")
        else:
            state['quartoAnnounced'] = False

    def _same(self, feature, elems):

        try:
            elems = list(map(lambda piece: piece[feature], elems))
        except:
            return False
        print('\nSAME:\nelems: {}\nfeature: {}'.format(elems, feature))
        return all(e == elems[0] for e in elems)

    def _quarto(self, elems):
        return self._same('shape', elems) or self._same('color', elems) or self._same('filling', elems) or self._same(
            'height', elems)

    def winner(self):
        state = self._state['visible']
        board = state['board']
        player = self.__player

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
        return None if board.count(None) == 0 else -1

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
        print()
        for row in range(4):
            print('                 |', end="")
            for col in range(4):
                print(self.displayPiece(state['board'][row * 4 + col]), end="|")
            print('\n')
        print()
        print("00 01 02 03", '\n04 05 06 07', '\n08 09 10 11', '\n12 13 14 15\n')
        print(", ".join([self.displayPiece(piece) for piece in state['remainingPieces']]))


class QuartoServer(game.GameServer):
    """Class representing a server for the Quarto game."""

    def __init__(self, verbose=False):
        super().__init__('Quarto', 2, QuartoState(), verbose=verbose)

    def applymove(self, move):
        try:
            move = json.loads(move)
        except:
            raise game.InvalidMoveException('A valid move must be a valid JSON string')
        else:
            self._state.setPlayer(self.currentplayer)
            self._state.applymove(move)


class QuartoClient(game.GameClient):
    """Class representing a client for the Quarto game."""

    def __init__(self, name, server, verbose=False):
        super().__init__(server, QuartoState, verbose=verbose)
        self.__name = name

    def _handle(self, message):
        pass

    def _nextmove(self, state):
        # ai = Negamax(5)
        # ai2 = SSS(5)
        quarto = simpleClient([AI_Player(Negamax(5)), AI_Player(SSS(5))], state)
        print(1)
        ai_moves = quarto.get_move()
        print(ai_moves)
        return json.dumps(ai_moves)


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

        # print('\n remainingPieces:', remainingPieces, '\n\n pieceToPlay:', visible['pieceToPlay'], '\n')

        # select the first free position
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


# easy IA
class simpleClient(TwoPlayersGame):
    def __init__(self, players, quartostate):
        self.quartostate = quartostate
        self.players = players
        self.nplayer = 1
        # print('SimpleClient created: {}'.format(self.quartostate._state['visible']))

    def possible_moves(self):
        visible = self.quartostate._state['visible']
        liste = []
        move = {}
        print(visible['board'])
        for i in range(0, len(visible['remainingPieces'])):
            move["nextPiece"] = i
            for n in range(0, 16):
                move["pos"] = n
                move['quarto'] = True
                liste.append(move)
                try:
                    print(move)
                    state.applymove(move)
                except:
                    del (move['quarto'])
        return liste

    def make_move(self, move):
        self.quartostate.applymove(move)

    def win(self):
        return self.quartostate.winner()

    def is_over(self):
        return self.win() != -1

    def show(self):
        self.quartostate.prettyprint()

    def scoring(self):
        return 1 if self.win() else 0


if __name__ == '__main__':

    # Create the top-level parser
    parser = argparse.ArgumentParser(description='Quarto game')
    subparsers = parser.add_subparsers(description='server client', help='Quarto game components', dest='component')

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

    # Create the parser for the 'user' subcommand
    user_parser = subparsers.add_parser('user', help='launch a user')
    user_parser.add_argument('name', help='name of the player')
    user_parser.add_argument('--host', help='hostname of the server (default: localhost)', default='127.0.0.1')
    user_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
    user_parser.add_argument('--verbose', action='store_true')

    # Create the parser for the '2 player games' subcommand
    user_parser = subparsers.add_parser('ai', help='launch a user')
    user_parser.add_argument('name', help='name of the player')
    user_parser.add_argument('--host', help='hostname of the server (default: localhost)', default='127.0.0.1')
    user_parser.add_argument('--port', help='port of the server (default: 5000)', default=5000)
    user_parser.add_argument('--verbose', action='store_true')

    # Parse the arguments of sys.args
    args = parser.parse_args()
    if args.component == 'server':
        QuartoServer(verbose=args.verbose).run()

    if args.component == 'client':
        QuartoClient(args.name, (args.host, args.port), verbose=args.verbose)

    if args.component == 'ai':
        ai = Negamax(13)
        ai2 = Negamax(10)
        state = QuartoState
        game = simpleClient([Human_Player(), AI_Player(ai2)], state)
        print(1)
        game.play()
        

    else:
        QuartoUser(args.name, (args.host, args.port), verbose=args.verbose)
