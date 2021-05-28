import json, sys, time
from rq import get_current_job
from api.app import app
from api.models import db, Task, PredictionModel, Instance
from api.pm_processing import describe_model
from sqlalchemy import and_
import pandas as pd 
import pickle 

# ML tasks
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier, LogisticRegression

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
        if pm.page == 0:
            model = SGDClassifier(average=True)
        else:
            pm_previous = PredictionModel.query.get(pm_id-1)
            model = pickle.loads(pm_previous.pickle_obj)

        # extract the necessary instances to train on
        starting_index = pm.page * app.config['DOCUMENT_PER_PAGE']
        ending_index = starting_index + app.config['TRAIN_TEST_BATCH']
        all_instances = Instance.query\
            .filter(Instance.id>=starting_index)\
            .filter(Instance.id<ending_index)\
            .all()
        df = pd.DataFrame([i.to_dict() for i in all_instances])
        dataset = df[['competence','network_ability','promoted']] # skip id
        X_vals = dataset.iloc[:, :-1].values
        y_vals = dataset.iloc[:, -1].values
        # if not first model, test with the same data
        if pm.page != 0:
            
            test_start = time.time()
            pm_previous.accuracy = model.score(X_vals, y_vals)
            pm_previous.test_time = time.time() - test_start
            pm_previous.test_pos = int(sum(y_vals))
            db.session.commit()

        # train model 
        train_start = time.time()
        model.partial_fit(X_vals, y_vals, classes=[0,1])
        pm.train_time = time.time() - train_start
        pm.train_pos = int(sum(y_vals))

        # extract parameters
        model_description = describe_model(
            'model',model,dataset.iloc[:, :-1],None
        )
        pm.from_dict(model_description)

        # store model
        pickle_obj = pickle.dumps(model)
        pm.pickle_obj = pickle_obj

        db.session.commit()
    except Exception as e:
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    _set_task_progress(100)
        
        
