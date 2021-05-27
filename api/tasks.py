import json, sys, time
from rq import get_current_job
from api import app, db
from api.models import Task, PredictionModel

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


def run_long_document_extraction(profile_id, length=20):
    profile = PredictionModel.query.get(profile_id)
    _set_task_progress(0)
    # iteratively generate docs
    try:
        profile.search_cl(length)
    except Exception as e:
        flash(str(e))
        app.logger.error('Unhandled exception', exc_info=sys.exc_info())
    _set_task_progress(100)
        
        
