#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This file is responsible for managing all the flask/website
    interactions involving the chess game
"""

#------------------------------STANDARD DEPENDENCIES-----------------------------#
from typing import Optional, Dict, List, Union, NamedTuple
from enum import Enum
from copy import deepcopy

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from flask_table import Table, Col
from flask_table.columns import LinkCol, ButtonCol

#--------------------------------Project Includes--------------------------------#
from flask_helpers import flash_print


# chess board constants
class ChessConstants():
    NUM_PAWNS   = 8
    NUM_KNIGHTS = 2
    NUM_BISHOPS = 2
    NUM_QUEENS  = 1
    NUM_KINGS   = 1

# maps ints to pieces
class ChessPieceType(Enum):
    empty     = 0
    pawn      = 1
    knight    = 2
    bishop    = 3
    rook      = 4
    queen     = 5
    king      = 6

class ChessTeam(Enum):
    white     = 0
    black     = 1
    neither   = 2

class ChessPiece(NamedTuple):
    piece: ChessPieceType
    team: ChessTeam

class ChessTable(Table):
    """
        X-Axis: a-h (left -> right)
        Y-Axis: 1-8 (bot -> top)
    """
    classes = ["table", "is-bordered", "is-striped", "is-hoverable", "is-fullwidth"]
    col_a = Col("a")
    col_b = Col("b")
    col_c = Col("c")
    col_d = Col("d")
    col_e = Col("e")
    col_f = Col("f")
    col_g = Col("g")
    col_h = Col("h")
    border = True

class ChessTableRow(object):
    def __init__(self, row_pieces: List[ChessPiece]):
        """Describes a chess cell / peice on the board

        Args:
            piece (List[ChessPiece]): List of chess pieces in this row
        """
        # add pieces in reverse order since rows go 8->1 (top->down)
        self.col_a = row_pieces[7]
        self.col_b = row_pieces[6]
        self.col_c = row_pieces[5]
        self.col_d = row_pieces[4]
        self.col_e = row_pieces[3]
        self.col_f = row_pieces[2]
        self.col_g = row_pieces[1]
        self.col_h = row_pieces[0]


b_piece = lambda c_type: ChessPiece(piece=c_type, team=ChessTeam.black)
w_piece = lambda c_type: ChessPiece(piece=c_type, team=ChessTeam.white)
empty_piece = lambda: ChessPiece(piece=ChessPieceType.empty, team=ChessTeam.neither)


def create_chess_table(cells: Optional[List[List[ChessPiece]]]) -> List[ChessTableRow]:
    """Creates a table based on the description of cells passed
    Args:
        cells (2D List of ChessPiece): None means generate brand new table
    Returns:
        List[ChessTableRow]: List of chess piece rows
            that can be passed to ChessTable's constructor
    """
    if cells is None:
        flash_print("setting up starting chess board")
        col_a = [
            b_piece(ChessPieceType.rook),
            b_piece(ChessPieceType.pawn),
            empty_piece(),
            empty_piece(),
            empty_piece(),
            empty_piece(),
            w_piece(ChessPieceType.pawn),
            w_piece(ChessPieceType.rook),
        ]
        col_b = [
            b_piece(ChessPieceType.knight),
            b_piece(ChessPieceType.pawn),
            empty_piece(),
            empty_piece(),
            empty_piece(),
            empty_piece(),
            w_piece(ChessPieceType.pawn),
            w_piece(ChessPieceType.knight),
        ]
        col_c = [
            b_piece(ChessPieceType.bishop),
            b_piece(ChessPieceType.pawn),
            empty_piece(),
            empty_piece(),
            empty_piece(),
            empty_piece(),
            w_piece(ChessPieceType.pawn),
            w_piece(ChessPieceType.bishop),
        ]
        col_d = [
            b_piece(ChessPieceType.queen),
            b_piece(ChessPieceType.pawn),
            empty_piece(),
            empty_piece(),
            empty_piece(),
            empty_piece(),
            w_piece(ChessPieceType.pawn),
            w_piece(ChessPieceType.queen),
        ]
        col_e = [
            b_piece(ChessPieceType.knight),
            b_piece(ChessPieceType.pawn),
            empty_piece(),
            empty_piece(),
            empty_piece(),
            empty_piece(),
            w_piece(ChessPieceType.pawn),
            w_piece(ChessPieceType.knight),
        ]
        # symmetrical now
        col_f = deepcopy(col_c)
        col_g = deepcopy(col_b)
        col_h = deepcopy(col_a)
        cells = [col_a, col_b, col_c, col_d, col_e, col_f, col_g, col_h]

    chess_table = [ChessTableRow(row) for row in cells]
    return chess_table
