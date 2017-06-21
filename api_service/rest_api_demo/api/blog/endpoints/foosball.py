import logging
import json
import rethinkdb as r
import calendar
import time



from flask import request, jsonify
from flask_restplus import Resource
from api_service.rest_api_demo.api.blog.business import db_host, db_port
#from api_service.rest_api_demo.api.blog.serializers import category
from api_service.rest_api_demo.api.restplus import api
#from api_service.rest_api_demo.database.models import Category

log = logging.getLogger(__name__)

ns = api.namespace('foosball', description='Operations related to foosball')


@ns.route('/')
class CategoryCollection(Resource):

    #@api.marshal_list_with()
    @api.expect()
    def get(self):
        """
        Returns current GameID, score, and player names.

        HELLO
        """
        #categories = Category.query.all()
        #return categories

        #Init vars
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

        resp = (r.db('foosball').table("games").get(keys[0]).run())

        final_resp = json.loads(json.dumps(resp))

        return final_resp, 201

    @api.response(201, 'Game successfully created.')
    @api.expect()
    def post(self):
        """
        Create a new game. 

        Use this method add in new players and reset the foosball score.

        * Send a JSON object with the player names in the body.

        ```
        {
          "player1": {
            "score": 0,
            "email": "player1@cisco.com",
            "name": "Player1"
          }
          "player2": {
            "score": 0,
            "email": "player2@cisco.com",
            "name": "Player2"
          }
        }
        ```

        * Specify the ID of the category to modify in the request URL path.
        """
        keys = ["", ""]

        print("post!")
        r.connect(db_host, db_port).repl()
        active_game = r.db("foosball").table("games").filter(r.row["active"] == True)
        # Deactivate any active games
        for i, row in enumerate(active_game.run()):
            keys[i] = (str(row["id"]))
            r.db("foosball").table("games").filter({"id": row["id"]}).update({"active": False}).run()

        curr_time = str((calendar.timegm(time.gmtime())))
        print("Hello" + curr_time)


        # Create new game with input params
        try:
            data = json.loads((request.data).decode("utf-8"))
            print(data['player1'])
            db_data = json.loads(json.dumps({
                "player2": {
                    "name": data['player2']['name'],
                    "email": data['player2']['email'],
                    "score": 0
                },
                "player1": {
                    "name": data['player1']['name'],
                    "email": data['player1']['email'],
                    "score": 0
                },
                "active": True,
                "time": curr_time

        }))
            print(db_data)
        except Exception as e:
            return {"error": str(e), "code":"blog.endpoints.foosball.CategoryCollection.get"}

        # Create a new active game
        db_resp = r.db("foosball").table("games").insert(db_data).run()

        # Grab the ID to be returned
        resp_id = db_resp['generated_keys'][0]

        # Return HTTP response to client
        return {"id": resp_id}, 201


@ns.route('/<string:game_id>')
@api.response(404, 'Category not found.')
class CategoryItem(Resource):

    @api.expect()
    @api.response(200, 'Request sucessfully executed')
    def get(self, game_id):
        """
	Get the results of a historic game give the GameID in the URL.

        """
        r.connect(db_host, db_port).repl()
        resp = (r.db('foosball').table("games").get(game_id).run())

        final_resp = json.loads(json.dumps(resp))

        return final_resp, 200

    @api.response(204, 'Category successfully deleted.')
    def delete(self, game_id):
        """
        Deletes game.
        """
        r.connect(db_host, db_port).repl()
        try:
            resp = (r.db('foosball').table("games").get(game_id).delete().run())
        except Exception as e:
            return {"error": str(e),
                    "code": "blog.endpoints.foosball.CategoryItem.delete"}

        final_resp = json.loads(json.dumps(resp))

        return None, 204

@ns.route('/default')
#@api.response(404, 'Category not found.')
class CategoryItem(Resource):

    @api.expect()
    #@api.response(204, 'Category successfully updated.')
    def post(self):
        """
        Create a default game.

        Use this method to reset the system **wihtout input data**.

        * Useful for quick demos.

        """
        # Init vars
        keys = ["", ""]

        r.connect(db_host, db_port).repl()
        active_game = r.db("foosball").table("games").filter(r.row["active"] == True)
        # Delete any active games
        for i, row in enumerate(active_game.run()):
            keys[i] = (str(row["id"]))
            r.db("foosball").table("games").filter({"id": row["id"]}).update({"active": False}).run()

        curr_time = str((calendar.timegm(time.gmtime())))
        print("Hello" + curr_time)

        # Default Gameimport rethinkdb as r
        default_game = json.loads(json.dumps({
                "player2": {
                    "name": "Player2",
                    "email": "player2@cisco.com",
                    "score": 0
                },
                "player1": {
                    "name": "Player1",
                    "email": "player1@cisco.com",
                    "score": 0
                },
                "active": True,
                "time": curr_time

        }))

        # Create a new active game
        db_resp = r.db("foosball").table("games").insert(default_game).run()

        # Grab the ID to be returned
        resp_id = db_resp['generated_keys'][0]

        # Return HTTP response to client
        return {"id": resp_id}, 201

    def options(self):
        """
        Create a default game.

        Use this method to reset the system **wihtout input data**.

        * Useful for quick demos.

        """
        # Init vars
        keys = ["", ""]

        r.connect(db_host, db_port).repl()
        active_game = r.db("foosball").table("games").filter(r.row["active"] == True)
        # Delete any active games
        for i, row in enumerate(active_game.run()):
            keys[i] = (str(row["id"]))
            r.db("foosball").table("games").filter({"id": row["id"]}).update({"active": False}).run()

        curr_time = str((calendar.timegm(time.gmtime())))
        print("Hello" + curr_time)

        # Default Gameimport rethinkdb as r
        default_game = json.loads(json.dumps({
                "player2": {
                    "name": "Player2",
                    "email": "player2@cisco.com",
                    "score": 0
                },
                "player1": {
                    "name": "Player1",
                    "email": "player1@cisco.com",
                    "score": 0
                },
                "active": True,
                "time": curr_time

        }))

        # Create a new active game
        db_resp = r.db("foosball").table("games").insert(default_game).run()

        # Grab the ID to be returned
        resp_id = db_resp['generated_keys'][0]

        # Return HTTP response to client
        return {"id": resp_id}, 201


