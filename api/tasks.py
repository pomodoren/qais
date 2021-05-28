import json, sys, time
from rq import get_current_job
from api import app, db
from api.models import Task, PredictionModel, Instance

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
        starting_index = pm.taskspage * app.config['DOCUMENT_PER_PAGE']
        ending_index = starting_index + app.config['DOCUMENT_PER_PAGE']
        all_instances = Instance.query\
            .filter_by(
                Instance.id>=starting_index, 
                Instance.id<ending_index
            ).all()
        # train model 
        print(all_instances)
        # store parameters
    except Exception as e:
        flash(str(e))
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    _set_task_progress(100)
        
        
