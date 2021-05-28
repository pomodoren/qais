from flask import current_app, url_for, Markup
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, text, func, extract
from datetime import datetime, timedelta
from time import time
from itertools import groupby
import os, json

db = SQLAlchemy()
class Instance(db.Model):
    __tablename__ = 'instance'
    id = db.Column(db.Integer, primary_key=True)
    competence = db.Column(db.Integer)
    network_ability = db.Column(db.Integer)
    promoted = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "competence":self.competence,
            "promoted":self.promoted,
            "network_ability": self.network_ability
        }

    def from_dict(self,data):
        for each in ['id','competence','network_ability','promoted']:
            if each in data:
                setattr(self,each,data[each])
            

    def __repr__(self):
        return "<Instance {}>".format(self.id)


class PredictionModel(db.Model):
    # default
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    archived = db.Column(db.Boolean, default=False)

    # trained on which instances
    page = db.Column(db.Integer)
    instance_count = db.Column(db.Integer) 

    # specific
    n_train = db.Column(db.Integer)
    n_train_pos = db.Column(db.Integer)    
    accuracy = db.Column(db.Float)
    accuracy_history = db.Column(db.JSON)
    t0 = db.Column(db.DateTime)
    runtime_history = db.Column(db.JSON)
    total_fit_time = db.Column(db.Float)
    
    # TODO - need to define pickle object where to read from 
    # Alternative - store in a static space, and read from there using
    # a field in this database - this way skip the headache for now ...
    #pickle_obj = db.PickleType 

    def from_dict(self,data):
        for each in ['n_train','n_train_pos','accuracy',
            'accuracy_history','t0','runtime_history','total_fit_time']:
            if each in data:
                setattr(self,each,data[field])
            
    @classmethod
    def start_training(cls):
        """
        when load batch of 10
        - check if Instance.count == N 
            - if yes, then train new model
            - store model in PredictionModel Table
        - check elif Instance.count() % N == 0 - if yes
            - test existing model
            - store stats results
            - new model: train with the new N - this will wait for next input
            - store new model in db
        """ 

        # get last model
        last_model = PredictionModel.query.order_by(PredictionModel.timestamp.desc()).first()
        # check if first time running a model
        #if not last_model and Instance.query.count() > current_app.config['TRAIN_TEST_BATCH']:
        print("Entered")
        # create prediction model
        new_model = PredictionModel()
        new_model.page = 0
        new_model.instance_count = current_app.config['TRAIN_TEST_BATCH']
        db.session.add(new_model)
        db.session.commit()

        new_model.launch_task('run_model','partial fit the data')
        #else:
        # print('skip')

    def launch_task(self, name, description, *args, **kwargs):
        print("launching")
        rq_job = current_app.task_queue.enqueue(
            "api.tasks." + name, self.id, *args, **kwargs
        )
        task = Task(id=rq_job.get_id(), name=name, description=description, pm_id=self.id)
        db.session.add(task)
        db.session.commit()
        return task

    def get_tasks_in_progress(self):
        return Task.query.filter_by(pm_id=self.id, complete=False).all()

    def get_task_in_progress(self, name):
        return Task.query.filter_by(name=name, pm_id=self.id, complete=False).first()

            
class Task(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), index=True)
    description = db.Column(db.String(128))
    complete = db.Column(db.Boolean, default=False)
    
    pm_id = db.Column(db.Integer, db.ForeignKey("prediction_model.id"))

    def get_rq_job(self):
        try:
            rq_job = rq.job.Job.fetch(self.id, connection=current_app.redis)
        except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
            return None
        return rq_job

    def get_progress(self):
        job = self.get_rq_job()
        return job.meta.get("progress", 0) if job is not None else 100

