from flask import Flask, request, jsonify, render_template, abort, redirect, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from redis import Redis
import sqlite3 as sqlite
import pandas as pd
import sys, os, json
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
    pred_models = PredictionModel.query.all()
    vals = [[i.page,i.accuracy] for i in pred_models if i.accuracy]
    train_vs_test_pos = [['Page','Train Time','Test Time']]\
        +[
            [i.page,i.train_time,i.test_time] 
            for i in pred_models if i.accuracy
        ]
    return render_template(
        'index.html', 
        page_accuracy=vals, 
        train_vs_test_pos=train_vs_test_pos
    )

@app.route('/api/v1/data', methods=['GET','POST'])
def api_filter():
    query_parameters = request.args
    
    if request.method == 'POST':
        json_data = request.get_json()
        # basic checks
        try:
            if not json_data or \
                not isinstance(json_data, list):
                abort(400)
            df = pd.DataFrame(json_data)  
            if set(df.columns) != set(['id','competence','network_ability','promoted']):
                abort(400)
        except Exception as e:
            abort(400)
        data_instances = []
        for i in json_data:
            try:
                instance_ = Instance()
                instance_.from_dict(i)
                data_instances.append(instance_)
            except Exception as e:
                print(e)
                abort(400)
            db.session.add_all(data_instances)
            db.session.commit()
        PredictionModel.start_training()
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

@app.route('/train_test')
def train_test():
    PredictionModel.start_training()
    return redirect(url_for('api_filter',page=0))

if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT'))
    else:
        app.run(debug=True, host='0.0.0.0')

