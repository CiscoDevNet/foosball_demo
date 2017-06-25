import logging
import json
import rethinkdb as r


from flask import request
from flask_restplus import Resource
from api.blog.business import db_host, db_port
from api.blog.serializers import scores
from api.restplus import api
from database.models import Category

log = logging.getLogger(__name__)

ns = api.namespace('score', description='Operations related to the score')


@ns.route('/')
class CategoryCollection(Resource):

    #@api.marshal_list_with(category)
    @api.expect()
    def get(self):
        """
        Returns current score.
        """
        keys = ["",""]

        r.connect(db_host, db_port).repl()
        active_game = r.db("foosball").table("games").filter(r.row["active"] == True)
        for i, row in enumerate(active_game.run()):
            keys[i] = (str(row["id"]))
        print(keys)

        if keys[0] == "":
            resp = {"message": "There are no active games"}
            return resp, 200
        if keys[1] != "":
            resp =  {"error":"internal error has occured, multiple games in active state not allowed",
                    "code":"blog.endpoints.foosball.CategoryCollection.get"}
            return resp, 500

        resp = json.loads(json.dumps((r.db('foosball').table("games").get(keys[0]).run())))

        resp = {
            "player1_score": resp["player1"]["score"],
            "player2_score": resp["player2"]["score"]
        }

        return resp, 201

    @api.response(204, 'Score successfully updated.')
    @api.expect(scores)
    def put(self):
        """
        Update both players scores.
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
                    "score": data['player1_score']
                },
                "player2": {
                    "score": data['player2_score']
                }
            }))
        except Exception as e:
            return {"error": str(e), "code": "blog.endpoints.foosball.CategoryCollection.get"}

        try:
            r.db('foosball').table("games").get(keys[0]).update(db_data).run()
        except Exception as e:
            resp = {"error": str(e),
                    "code": "blog.endpoints.score.CategoryCollection.post"}
            return resp, 500

        return None, 204

@ns.route('/<player>')
@api.response(404, 'Category not found.')
class CategoryItem(Resource):

    #@api.marshal_with()
    def get(self, player):
        """
        Returns the score for a given player.
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
                    "code": "blog.endpoints.score.CategoryItem.get"}
            return resp, 500

        resp = json.loads(json.dumps((r.db('foosball').table("games").get(keys[0]).run())))

        resp = {
            "score": resp[player]["score"]
        }

        return resp, 201


@ns.route('/<player>/and1')
@api.response(404, 'Category not found.')
class and1(Resource):

    @api.expect()
    @api.response(204, 'Score Updated')
    def put(self, player):
        """
        Increments the player specified in the url's score by 1 point.

        """
        keys = ["", ""]
        # Bool representing if the player has won
        winner = False
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

        # Update the given player's score
        try:
            if player not in ("player1", "player2"):
                resp = {"error": "URL must be player1 or player2"}
                return resp, 404

        except Exception as e:
            return {"error": str(e), "code": "blog.endpoints.foosball.and1.put"}

        try:
            curr_game = r.db('foosball').table("games").get(keys[0]).run()
            player_score = curr_game[player]['score']
            player_score += 1

            print(player_score)

            db_data = json.loads("""{
                "%s": {
                    "score": %i
                }
            }""" % (player, player_score))
            r.db('foosball').table("games").get(keys[0]).update(db_data).run()
        except Exception as e:
            resp = {"error": str(e),
                    "code": "blog.endpoints.score.and1.put"}
            return resp, 500

        return db_data, 204


@ns.route('/<player>/<int:url_score>')
@api.response(404, 'Category not found.')
class ScoreByPlayer(Resource):

    @api.expect()
    @api.response(204, 'Score Updated')
    def put(self, player, url_score):
        """
        Sets the score for a the player specified in the ULR the the score specified by url_score
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

        # Update the given player's score
        try:
            if player not in ("player1", "player2"):
                resp = {"error": "URL must be player1 or player2"}
                return resp, 404
            db_data = """{
                "%s": {
                    "score": %i
                }
            }""" % (player, url_score)
            db_data = json.loads(db_data)
        except Exception as e:
            return {"error": str(e), "code": "blog.endpoints.foosball.CategoryCollection.put"}

        try:
            r.db('foosball').table("games").get(keys[0]).update(db_data).run()
        except Exception as e:
            resp = {"error": str(e),
                    "code": "blog.endpoints.score.CategoryCollection.post"}
            return resp, 500

        return None, 204