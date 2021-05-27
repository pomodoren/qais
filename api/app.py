from flask import Flask, request, jsonify, render_template, abort
from flask_migrate import Migrate
from flask_cors import CORS
import sqlite3 as sqlite
import sys
import os
import json
from redis import Redis
import rq, pickle

from config import CONFIG

migrate = Migrate()

app = Flask(__name__)

app.config.from_object(CONFIG)
CORS(app)  # This will enable CORS for all routes

app.redis = Redis.from_url(app.config["REDIS_URL"])
app.task_queue = rq.Queue(
    "model-tasks", 
    connection=app.redis, 
    default_timeout=100000, 
    serializer=pickle
)

from models import db, PredictionModel, Instance, Task

db.init_app(app)
migrate.init_app(app, db)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/api/v1/data', methods=['GET','POST'])
def api_filter():
    query_parameters = request.args

    if request.method == 'POST':
        json_data = request.get_json()
        # check if any issues with the data
        if not json_data or not isinstance(json_data, list):
            print('issue previous')
            abort(400)
        for i in json_data:
            if not isinstance(i,dict) or\
                set(i.keys()) != set(['id','competence','network_ability','promoted']) or\
                len([j for j in i.values() if not isinstance(j, (int, float))]):
                print('issue here')
                abort(400)
        for i in json_data:
            try:
                instance_ = Instance()
                instance_.from_dict(i)
                db.session.add(instance_)
                db.session.commit()
            except Exception as e:
                print(e)
                abort(400)

        # process
        return jsonify({
            "status":"success"
        })
    # updating to not get errors
    page_str = query_parameters.get('page')
    if not page_str:
        abort(404)
    page = int(page_str)
    instances = Instance.query.paginate(
            page, app.config['DOCUMENT_PER_PAGE'], False)
    results = instances.items
    return jsonify([i.to_dict() for i in results])



if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT'))
    else:
        app.run(debug=True, host='0.0.0.0')

