import json, sys, time
from rq import get_current_job
from api.app import app
from api.models import db, Task, PredictionModel, Instance
from api.pm_processing import describe_model
from sqlalchemy import and_
import pandas as pd 

# ML tasks
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier

app.app_context().push()

def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = Task.query.get(job.get_id())
        if progress >= 100:
            task.complete = True
        db.session.commit()


def run_model(pm_id):
    # extract prediction model from database
    pm = PredictionModel.query.get(pm_id)
    _set_task_progress(0)
    try:
        # create a model 
        model = SGDClassifier()

        # extract the necessary instances to train on
        starting_index = pm.page * app.config['TRAIN_TEST_BATCH']
        ending_index = starting_index + app.config['TRAIN_TEST_BATCH']
        all_instances = Instance.query\
            .filter(Instance.id>=starting_index)\
            .filter(Instance.id<ending_index)\
            .all()
        df = pd.DataFrame([i.to_dict() for i in all_instances])
        dataset = df[['competence','network_ability','promoted']] # skip id
        X_train = dataset.iloc[:, :-1].values
        y_train = dataset.iloc[:, -1].values

        # train model 
        model.partial_fit(X_train, y_train, classes=[0,1])

        # extract parameters
        print(describe_model('model',model,dataset.iloc[:, :-1],None))

    except Exception as e:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    _set_task_progress(100)
        
        
