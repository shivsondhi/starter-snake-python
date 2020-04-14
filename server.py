import os
import random
import cherrypy

"""
This is a simple Battlesnake server written in Python.
For instructions see https://github.com/BattlesnakeOfficial/starter-snake-python/README.md
"""


class Battlesnake(object):
    @cherrypy.expose
    def index(self):
        # If you open your snake URL in a browser you should see this message.
        return "Your Battlesnake is alive!"

    @cherrypy.expose
    def ping(self):
        # The Battlesnake engine calls this function to make sure your snake is working.
        return "Howdy!"

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def start(self):
        # This function is called everytime your snake is entered into a game.
        # cherrypy.request.json contains information about the game that's about to be played.
        # TODO: Use this function to decide how your snake is going to look on the board.
        data = cherrypy.request.json
        print("START")
        return {"color": "#000000", "headType": "fang", "tailType": "round-bum"}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def move(self):
        # This function is called on every turn of a game. It's how your snake decides where to move.
        # Valid moves are "up", "down", "left", or "right".
        # TODO: Use the information in cherrypy.request.json to decide your next move.
        data = cherrypy.request.json
        print(data)
        # Choose a random direction to move in
        dirns = {"up": 0, "down": 0, "left": 0, "right": 0}
        move_results = {
            "up": (0, 1),
            "down": (0, -1),
            "left": (-1, 0),
            "right": (1, 0)
        }
        possible_moves = ["up", "down", "left", "right"]
        # get environment data
        h = data["board"]["height"]
        w = data["board"]["width"]
        my_pos = data["you"]["body"][0]
        my_dirn = data["you"]["body"][1]
        # don't reverse into yourself 
        if my_dirn['x'] > my_pos['x']:
            possible_moves.remove("right")
        elif my_dirn['x'] < my_pos['x']:
            possible_moves.remove("left")
        if my_dirn["y"] > my_pos["y"]:
            possible_moves.remove("down")
        elif my_dirn["y"] < my_pos["y"]:
            possible_moves.remove("up")
        # don't go off the board 
        if my_pos['x'] == 0:
            possible_moves.remove('left')
        elif my_pos['x'] == w:
            possible_moves.remove('right')
        if my_pos['y'] == 0:
            possible_moves.remove('up')
        elif my_pos['y'] == h:
            possible_moves.remove('down')
        # find nearest piece of food
        food_dist = [(abs(food['x']-my_pos['x']) + abs(food['y']-my_pos['y'])) for food in data["board"]["food"]]
        move_to = data["board"]["food"][food_dist.index(min(food_dist))]
        backup_moves = []
        # move towards the food
        if move_to['x'] > my_pos['x'] and "left" in possible_moves:
            backup_moves.append("left")
            possible_moves.remove("left")
        elif move_to['x'] < my_pos['x'] and "right" in possible_moves:
            backup_moves.append("right")
            possible_moves.remove("right")
        else:
            if "left" in possible_moves:
                backup_moves.append("left")
                possible_moves.remove("left")
            if "right" in possible_moves:
                backup_moves.append("right")
                possible_moves.remove("right")
        if move_to["y"] > my_pos["y"] and "up" in possible_moves:
            backup_moves.append("up")
            possible_moves.remove("up")
        elif move_to["y"] < my_pos["y"] and "down" in possible_moves:
            backup_moves.append("down")
            possible_moves.remove("down")
        else:
            if "up" in possible_moves:
                backup_moves.append("up")
                possible_moves.remove("up")
            if "down" in possible_moves:
                backup_moves.append("down")
                possible_moves.remove("down")
        # if no possible moves towards food, include non-food going moves
        if not possible_moves:
            move = random.choice(backup_moves)
        else:
            move = random.choice(possible_moves)
        dirns[move] = 1
        # beware of yourself 
        for body_part in data["you"]["body"]:
            new_xpos = my_pos["x"] + move_results[move][0]
            new_ypos = my_pos["y"] + move_results[move][1]
            if new_xpos == body_part["x"] and new_ypos == body_part["y"]:
                if len(possible_moves) > 0:
                    possible_moves.remove(move)
                if not possible_moves:
                    if move in backup_moves:
                        backup_moves.remove(move)
                        if not backup_moves:
                            return {"move": "up"}
                    move = random.choice(backup_moves)
                else:
                    move = random.choice(possible_moves)
                dirns[move] = 1
        # beware of other snakes
        while True:
            for snake in data["board"]["snakes"]:
                for body_part in snake["body"]:
                    new_xpos = my_pos["x"] + move_results[move][0]
                    new_ypos = my_pos["y"] + move_results[move][1]
                    if new_xpos == body_part["x"] and new_ypos == body_part["y"]:
                        if move in possible_moves:
                            possible_moves.remove(move)
                        if possible_moves:
                            move = random.choice(possible_moves)
                            dirns[move] = 1
                        else:
                            spare_moves = [x for x in dirns.keys() if dirns[x]==0]
                            if spare_moves:
                                move = random.choice(spare_moves)
                            else:
                                move = random.choice(dirns.keys())
                                break
                        continue
            break

        print("MOVE: {}".format(move))
        return {"move": move}

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def end(self):
        # This function is called when a game your snake was in ends.
        # It's purely for informational purposes, you don't have to make any decisions here.
        data = cherrypy.request.json
        print("END")
        return "ok"


if __name__ == "__main__":
    server = Battlesnake()
    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.config.update(
        {"server.socket_port": int(os.environ.get("PORT", "8080")),}
    )
    print("Starting Battlesnake Server...")
    cherrypy.quickstart(server)
