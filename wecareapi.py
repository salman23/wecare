from flask import Flask, jsonify, session, request, abort, render_template
from flask.ext.api import FlaskAPI, status
from flask.ext.pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
import ast

app = FlaskAPI(__name__)
app.config['MONGO_DBNAME'] = 'wecaredb'
mongo = PyMongo(app, config_prefix='MONGO')


@app.route("/voluntere/", methods=['GET', 'POST', 'DELETE', 'PUT'])
def voluntere():
    """
    voluntere CRUD api
    """
    if request.method == 'POST':    #add voluntere
        voluntere_doc = request.data
        v_doc = dict(voluntere_doc)
        data = v_doc.get('jsonData')
        mongodata = ast.literal_eval(data[0])
        oid = mongo.db.voluntere.insert(mongodata)
        voluntere_id =  str(oid)
        response_message = {"id": voluntere_id}
        print response_message
        return str(response_message)
    
    elif request.method == 'GET':
        raw_data = request.data
        print raw_data
        v_doc = dict(raw_data)
        data = v_doc.get('jsonData')
        jdata = ast.literal_eval(data[0])
        try:
            email = jdata.get("email")
        except (TypeError, KeyError) as e:
            email = None
        try:
            name = jdata.get("name")
        except (TypeError, KeyError) as e:
            name = None
        try:
            vol_id = ObjectId(jdata.get("id"))
        except (TypeError, KeyError) as e:
            name = None

        if vol_id:
            id_query = mongo.db.voluntere.find({"_id": vol_id})
            for data in id_query:
                vol_id = str(data.get('_id'))
                del(data['_id'])
                data['vid'] = vol_id
                return jsonify(data)
        if name:
            name_query = mongo.db.voluntere.find({"name": name})
            for data in name_query:
                vid = str(data.get('_id'))
                del(data['_id'])
                data['vid'] = vid
                return jsonify(data)
        else:
            email_query = mongo.db.voluntere.find({"email" : email})
            for data in email_query:
                vid = str(data.get('_id'))
                del(data['_id'])
                data['vid'] = vid
                return jsonify(data)


@app.route("/product/", methods=['GET', 'POST', 'DELETE', 'PUT'])
def product():
    """
    product CRUD api
    """
    if request.method == 'POST':
        product_doc = request.data
        pid = mongo.db.product.insert(product_doc)
        return str(pid), status.HTTP_201_CREATED
    if request.method == 'GET':
        jdata = request.data
        results = []
        if jdata.has_key('pid'):
            pid = ObjectId(jdata.get('pid'))
            query = mongo.db.product.find({'_id': pid})
        elif jdata.has_key('organization'):
            org = jdata.get('organization')
            query = mongo.db.product.find({'organization': org})

    
@app.route("/people/", methods=['GET', 'POST', 'DELETE', 'PUT'])
def people():
    """
    people CRUD api
    """
    if request.method == 'POST':
        people_doc = request.data
        pplid = mongo.db.product.insert(people_doc)
        return str(pplid), status.HTTP_201_CREATED



@app.route("/voluntere-login/", methods=['GET'])
def login():
    pass


@app.route("/", methods=['GET', 'POST'])
def index():
    return "wecare for people"
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
