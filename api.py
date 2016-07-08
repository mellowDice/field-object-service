import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
import requests
import traceback

import eventlet.wsgi
import numpy as np

# from create_terrain_objects import save_terrain, create_or_update_terrain_object, get_all_food, get_all_obstacles

app = Flask(__name__)

# Absolute path to the configuraiton file
app.config.from_envvar('APP_CONFIG_FILE')
print(app.config['DB_URL'] + '/' + 'food' + '/add' + str(3))

height = 250
width = 250
count = 1

@app.route('/')
def test_connect(): 
    return "connected to objects service"

@app.route('/terrain_objects', methods=['GET'])
def get_terrain_objects():
    global height, width
    height = int(request.args.get('height'))
    width = int(request.args.get('width'))
    requests.post(app.config['SOCKET_URL'] + '/send_field_objects', json ={'food':get_all_food(), 'obstacles': get_all_obstacles()})
    return 'OK'

@app.route('/update_object', methods=['GET'])
def update_object():
    print('Updating!')
    objId = request.args.get('id')
    objType = request.args.get('type')
    obj = random_coordinates(objId)
    print(objId, objType, obj)
    requests.post(app.config['DB_URL'] + '/' + objType + '/add', json={str(objType):[obj]})
    return jsonify(obj)

@app.route('/get_pi_food', methods=['GET'])
def get_pi_food():
    global count
    x = float(request.args.get('x'))
    z = float(request.args.get('z'))
    print('Getting pi food!', x, z)
    foodCircle = []
    size = 10
    if count > 50:
        count = 1
    for i in range(size):
        foodCircle.append({'x': x + (np.sin(np.deg2rad(360 * i /size)) * 10),
                           'z': z + (np.cos(np.deg2rad(360 * i /size)) * 10),
                           'id': count + 100})
        count = count + 1
    # d = {'x': x , 'z': z }
    print(foodCircle)
    return jsonify({'food':foodCircle})


######## ----- Helper Functions ------- ########

def get_all_food():
    print('get all food')
    food = requests.get(app.config['DB_URL'] + '/food/get_all').json()
    print('food', food)
    if len(food) == 0:
        for i in range(100):
            coordinates = random_coordinates(i)
            food.append(coordinates)
            requests.post(app.config['DB_URL'] + '/food/add', json={'food': [coordinates]})
    print(food)
    return food

def get_all_obstacles():
    print('get all obstacles')
    obstacles = requests.get(app.config['DB_URL'] + '/obstacles/get_all').json()
    print('obstacles', obstacles)
    if len(obstacles) == 0:
        for j in range(15):
            coordinates = random_coordinates(j)
            obstacles.append(coordinates)
            requests.post(app.config['DB_URL'] + '/obstacles/add', json={'obstacles': [coordinates]})
    return obstacles

def random_coordinates(num):
  global height
  print(height)
  coordinates = np.random.randint(height, size=2).tolist()
  id = num
  x = coordinates[0]
  z = coordinates[1]
  return {'x': x, 'z': z, 'id': id}
    
# error handling
@app.errorhandler(500)
def internal_error(exception):
    """Show traceback in the browser when running a flask app on a production server.
    By default, flask does not show any useful information when running on a production server.
    By adding this view, we output the Python traceback to the error 500 page.
    """
    trace = traceback.format_exc()
    return("<pre>" + trace + "</pre>"), 500

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 7001)), app, debug=True)
