import os
import subprocess
import requests
import time
from datetime import datetime
from flask import jsonify
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

from rq import Queue
from rq.job import Job
from worker import conn


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

q = Queue(connection=conn)

from models import *

def processor_heavy_operation():

	subprocess.call(["dd", "if=/dev/zero", "of=testfilefast", "bs=1024", "count=100240"])
	#dd if=/dev/random of=bigfile bs=1024 count=102400
	#subprocess.call(["dd", "if=/dev/urandom", "of=testfileslow", "bs=64M", "count=16"])
	return 69 

def ping_and_save_url(url):
    errors = []

    try:
        r = requests.get(url)
    except:
        errors.append(
            "Unable to get URL. Please make sure it's valid and try again."
        )
        return {"error": errors}

    start_time = time.time()
    processor_heavy_operation()
    #end_time = #
    operation_time = time.time() - start_time
    
    # save the results
    try:
    	from models import Result
        result = Result(
            url=url,
            operation_time = operation_time,
            operation_string= "dd if=/dev/random of=bigfile bs=1024 count=102400", 
            start_date = datetime.utcnow()          
        )
        db.session.add(result)
        db.session.commit()
        return result.id
    except:
        errors.append("Unable to add item to database.")
        return {"error": errors}


@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    if request.method == "POST":
        # get url that the person has entered
        url = request.form['url']
        if 'http://' not in url[:7]:
            url = 'http://' + url
        job = q.enqueue_call(
            func=ping_and_save_url, args=(url,), result_ttl=5000
        )
        print(job.get_id())
        print(url)


    return render_template('index.html', results=results)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    if request.method == "POST":
        # get url that the person has entered
        url = request.form['url']
        if 'http://' not in url[:7]:
            url = 'http://' + url
        job = q.enqueue_call(
            func=ping_and_save_url, args=(url,), result_ttl=5000
        )
        print(job.get_id())
        print(url)


    return render_template('index.html', results=results)

@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        return "Yay!", 200
    else:
        return "Nay!", 202

if __name__ == '__main__':
    app.run()