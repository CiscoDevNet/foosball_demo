import logging
import json
import rethinkdb as r

from flask import request
from flask_restplus import Resource
from api.blog.business import db_host, db_port
from api.blog.serializers import player_names
from api.restplus import api
from database.models import Category

log = logging.getLogger(__name__)

ns = api.namespace('players', description='Operations related to players')


@ns.route('/')
class root_players(Resource):

    #@api.marshal_list_with(category)
    @api.expect()
    def get(self):
        """
        Returns current player names.
        """
        keys = ["", ""]

        r.connect(db_host, db_port).repl()
        active_game = r.db("foosball").table("games").filter(r.row["active"] == True)
        for i, row in enumerate(active_game.run()):
            keys[i] = (str(row["id"]))
        print(keys)

        if keys[0] == "":
            resp = {"message": "There are no active games"}
            return resp, 200
        if keys[1] != "":
            resp = {"error": "internal error has occured, multiple games in active state not allowed",
                    "code": "blog.endpoints.foosball.CategoryCollection.get"}
            return resp, 500

        resp = (r.db('foosball').table("games").get(keys[0]).run())

        resp = json.loads(json.dumps(resp))

        resp = {
            "player1": resp["player1"]["name"],
            "player2": resp["player2"]["name"]
        }

        return resp, 201

    @api.response(201, 'Category successfully created.')
    @api.expect(player_names)
    def put(self):
        """
        Update both players names.
        """
        keys = ["", ""]
        r.connect(db_host, db_port).repl()
        active_game = r.db("foosball").table("games").filter(r.row["active"] == True)
        for i, row in enumerate(active_game.run()):
            keys[i] = (str(row["id"]))
        print(keys)

        if keys[0] == "":
            resp = {"message": "There are no active games"}
            return resp, 200
        if keys[1] != "":
            resp = {"error": "internal error has occured, multiple games in active state not allowed",
                    "code": "blog.endpoints.foosball.CategoryCollection.get"}
            return resp, 500

        # Create new game with input params
        try:
            data = json.loads((request.data).decode("utf-8"))
            db_data = json.loads(json.dumps({
                "player1": {
                    "name": data['player1']
                },
                "player2": {
                    "name": data['player2']
                }
            }))
        except Exception as e:
            return {"error": str(e), "code": "blog.endpoints.player.root_players.get"}

        try:
            r.db('foosball').table("games").get(keys[0]).update(db_data).run()
        except Exception as e:
            resp = {"error": str(e),
                    "code": "blog.endpoints.score.CategoryCollection.post"}
            return resp, 500

        return None, 204


@ns.route('/<string:player>')
@api.response(404, 'Category not found.')
class root_player_player(Resource):

    # @api.marshal_with()
    def get(self, player):
        """
        Returns the name for a given player.

        Must be player1 or player2
        """
        keys = ["", ""]
        r.connect(db_host, db_port).repl()

        # Get active game
        active_game = r.db("secret").table("games").filter(r.row["active"] == True)
        for i, row in enumerate(active_game.run()):
            keys[i] = (str(row["id"]))
        print(keys)

        # Verify only one active game exists, or return error
        if keys[0] == "":
            resp = {"message": "There are no active games"}
            return resp, 200
        if keys[1] != "":
            resp = {"error": "internal error has occured, multiple games in active state not allowed",
                    "code": "blog.endpoints.foosball.CategoryCollection.get"}
            return resp, 500


        try:
            if player not in ("player1", "player2"):
                resp = {"error": "URL must be player1 or player2"}
                return resp, 404

            resp = json.loads(json.dumps((r.db('foosball').table("games").get(keys[0]).run())))
            resp = json.loads("""{
                "%s": "%s"
            }
            """ % (player, resp[player]["name"]))

        except Exception as e:
            resp = {"error": str(e),
                    "code": "blog.endpoints.score.CategoryCollection.post"}
            return resp, 500

        return resp, 200

@ns.route('/<string:player>/<string:name>')
@api.response(404, 'Category not found.')
class root_player_name(Resource):

    # @api.marshal_with()
    def put(self, player, name):
        """
        Updates the name for a given player.

        Must be player1 or player2
        """
        keys = ["", ""]
        r.connect(db_host, db_port).repl()

        # Get active game
        active_game = r.db("foosball").table("games").filter(r.row["active"] == True)
        for i, row in enumerate(active_game.run()):
            keys[i] = (str(row["id"]))
        print(keys)

        # Verify only one active game exists, or return error
        if keys[0] == "":
            resp = {"message": "There are no active games"}
            return resp, 200
        if keys[1] != "":
            resp = {"error": "internal error has occured, multiple games in active state not allowed",
                    "code": "blog.endpoints.foosball.CategoryCollection.get"}
            return resp, 500


        try:
            if player not in ("player1", "player2"):
                resp = {"error": "URL must be player1 or player2"}
                return resp, 404

            db_data = """{
                "%s": {
                    "name": "%s"
                }
            }""" % (player, name)
            db_data = json.loads(db_data)

        except Exception as e:
            resp = {"error": str(e),
                    "code": "blog.endpoints.score.CategoryCollection.post"}
            return resp, 500

        try:
            r.db('foosball').table("games").get(keys[0]).update(db_data).run()
        except Exception as e:
            resp = {"error": str(e),
                    "code": "blog.endpoints.score.root_player_name.put"}
            return resp, 500

        return None, 204