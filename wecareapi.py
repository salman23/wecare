from flask import request, url_for
from flask.ext.api import FlaskAPI, status, exceptions
from flask.ext.pymongo import PyMongo
from bson.json_util import dumps

app = FlaskAPI(__name__)
app.config['MONGO_DBNAME'] = 'wecaredb'
mongo = PyMongo(app, config_prefix='MONGO')


@app.route("/reg_voluntere/", methods=['GET', 'POST'])
def reg_voluntere():
    if request.method == 'POST':
        voluntere_doc = request.data
        oid = mongo.db.voluntere.insert(voluntere_doc)
        return str(oid), status.HTTP_201_CREATED
    elif request.method == 'GET':
        jdata = request.data
        for key in jdata:
            try:
                email = jdata.get("email")
            except (TypeError, KeyError) as e:
                email = None
            try:
                name = jdata.get("name")
            except (TypeError, KeyError) as e:
                name = None
            results = []
            if email is None:
                name_query = mongo.db.voluntere.find({"name" : name},{"_id": 0})
                for data in name_query:
                    results.append(data)
                    return results
            else:
                email_query = mongo.db.voluntere.find({"email" : email}, {"_id" : 0})
                for data in email_query:
                    results.append(data)
                    return results
                    
if __name__ == "__main__":
    app.run(debug=True)
