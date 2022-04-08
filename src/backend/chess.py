#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    This file is responsible for managing all the flask/website
    interactions involving the chess game
"""

#------------------------------STANDARD DEPENDENCIES-----------------------------#

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from flask_login import login_user, current_user, login_required, logout_user


#--------------------------------Project Includes--------------------------------#
from flask_helpers import flash_print, is_json, is_form, is_static_req, clear_flashes
from chess_table import ChessTable, ChessPiece, ChessPieceType, ChessTeam, create_chess_table

class ChessWeb():
    """An object responsible for all the flask/website interactions involving the chess game"""
    def __init__(self, app: Flask):
        """Initialize the chess class that works with the flask app

        Args:
            app (Flask): An existing flask app to extend
        """
        self.app = app
        self.chess_title = "WebGames Chess"
        self.create_chess()

    def create_chess(self):
        """Creates all the routes for playing chess"""
        self.create_board_pages()
        self.create_rule_pages()

    def create_board_pages(self):
        # TODO: eventually create a page to show existing games and button to play them

        # TODO: POSTs should change state of board in db so games can be picked back up later

        @self.app.route("/chess/board/", methods=["GET"])
        # @login_required
        def chess():
            """Renders a fresh gameboard"""
            chess_table = ChessTable(create_chess_table(None))
            return render_template("chess.html", title=self.chess_title, chess_table=chess_table)

        @self.app.route("/chess/board/<int:instance_id>", methods=["GET"])
        @login_required
        def load_chess_game(instance_id: int):
            """Provide frontend with the chess board of a given game instance

            Args:
                instance_id (int): The game to display

            Returns:
                _type_: _description_
            """
            # TODO: eventually query db for board
            # db_table_data = ...
            # chess_table = ChessTable(create_chess_table(db_table_data))
            chess_table = None
            return render_template("chess.html", title=self.chess_title, chess_table=chess_table)

    def create_rule_pages(self):
        @self.app.route("/chess/rules", methods=["GET", "POST"])
        @login_required
        def chess_rules():
            """
                GET:
                POST:
            """
            pass
