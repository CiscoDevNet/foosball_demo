import paho.mqtt.client as mqtt
import ast
from playsound import playsound
import rethinkdb as r
import json
import requests

MQTT = "test.mosquitto.org"
MQTTPORT = 1883
client = mqtt.Client()
type = "api"
score_to_win = 5


r.connect("192.168.194.11", 28015).repl()


def on_connect(client, userdata, flags, rc):
    print("Connected with result " + str(rc))

    client.subscribe("lights/on")


def on_message(client, userdata, msg, type):
    mess = msg.payload.decode('utf-8')
    print(mess)
    data = ast.literal_eval(mess)
    if data["Score"] == 1:
        playsound("/Users/jocreed/Downloads/ho-my-hes-on-fire.mp3")
        if type == "api":
            url = "http://localhost:5000/api/score/player%s/and1" % (str(data['Player']))

            headers = {
                'content-type': "application/json"
            }

            response = requests.request("PUT", url, headers=headers)

            print(response.text)

            resp = json.loads((response.data).decode("utf-8"))

            if resp['player%s' % data['Player']]['score'] >= score_to_win:
                playsound("/Users/jocreed/Downloads/ho-my-hes-on-fire.mp3")


        elif type == "db":
            active_game = r.db("foosball").table("games").filter(r.row["active"] == True)

            keys = ["", ""]
            curr_score = 0
            for i, row in enumerate(active_game.run()):
                keys[i] = str(row["id"])
                curr_score = row["player%s" % data['Player']]['score']
            score = {}
            score["player%s" % str(data['Player'])] = {"score": (curr_score + 1)}
            print(score)
            scored = json.loads(json.dumps(score))
            r.db("foosball").table("games").filter({"id": keys[0]}).update(scored).run()


client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT, MQTTPORT, 60)

client.loop_forever()
