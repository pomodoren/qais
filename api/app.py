from flask import Flask, request, jsonify, render_template, abort
import sqlite3 as sqlite
import sys
import os
import json

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/api/v1/data', methods=['GET','POST'])
def api_filter():
    query_parameters = request.args
    conn = sqlite.connect('../data/main.db')
    if request.method == 'POST':
        json_data = request.get_json()
        # check if any issues with the data
        if not json_data or not isinstance(json_data, list):
            abort(400)
        for i in json_data:
            if not isinstance(i,dict) or\
             set(i.keys()) != set(['competence','network ability','promoted']) or\
             len([j for j in i.values() if not isinstance(j, (int, float))]):
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

    query = build_query(page)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query).fetchall()
    return jsonify(results)

def build_query(page):
    n_per_page = 10
    offset = page * n_per_page
    # Possibly vulnerable to SQL injection.
    query = "SELECT * FROM data LIMIT 10 OFFSET " + str(offset)
 
    return query 


if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT'))
    else:
        app.run(debug=True, host='0.0.0.0')

