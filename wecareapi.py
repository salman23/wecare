from flask import Flask, jsonify, session, request, abort, render_template
from flask.ext.api import FlaskAPI, status
from flask.ext.pymongo import PyMongo
from bson.json_util import dumps
from bson.objectid import ObjectId
import ast
import uuid
import string
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'wecaredb'
mongo = PyMongo(app, config_prefix='MONGO')


def make_login_response(message, session_token):
    response_message = {'status': 0, 'message': message, 'session_token': session_token}
    return response_message


def make_error_response(error_code, message, debug):
    response_message = {'status': error_code, 'message': message, 'debug': debug}
    return response_message


def make_user_response(status, message):
    response_message = {'status': status, 'message': message}
    return response_message


def authenticate(session_token):
    cursor = mongo.db.voluntere.find({"session_token": session_token})
    if cursor.count() != 1:
        return False
    else:
        for data in cursor:
            user_id = data.get("_id")
        return user_id

def check_null(data):
    if data:
        return data
    else:
        return ""


@app.route("/reg-voluntere/<string:email>/<string:password>/<string:name>/<string:phone>/<string:organization>/<string:district>/", methods=['GET'])
def reg_voluntere(email, password, name, phone, organization, district):
    """
    voluntere CRUD api
    """
    if mongo.db.user.find_one({'email': email}):
        response_message = make_error_response(1, "user already exists", "email exists")
    else:
        if phone == -2:
            phone=""
        if organization == -2:
            organization=""
        if district==-2:
            district=""
        voluntere_doc = {
            'email': email,
            'password': password,
            'name': name,
            'phone': phone,
            'organization': organization,
            'district': district,
        }
        oid = mongo.db.voluntere.insert(voluntere_doc)
        response_message = make_user_response(0, "Registered successfully")
    return jsonify(response_message)


@app.route("/product/<string:session_token>/<string:product_catagory>/<string:product_location>/<string:product_description>/", methods=['GET'])
@app.route("/product/<string:session_token>/<string:product_catagory>/<string:product_location>/", methods=['GET'])
def product(session_token, product_catagory, product_location, product_description=None):
    voluntere_id = authenticate(session_token)
    if not product_description:
        product_description=""
    product_doc = {
        'product_catagory': product_catagory,
        'product_location': product_location,
        'collected_by': voluntere_id,
        'product_description': product_description,
    }
    pid = mongo.db.product.insert(product_doc)
    response_message = make_user_response(0, "product added successsfully")
    return jsonify(response_message)


#login of a vlountere
@app.route("/voluntere-login/<string:email>/<string:password>/", methods=['GET'])
def login(email, password):
    cursor = mongo.db.voluntere.find({'email': email}, {'password': 1, '_id': 1})
    if cursor.count()<1:
        response_message = make_user_response(-1, "please register first")
    for data in cursor:
        v_id = data['_id']
        v_passw = data['password']
        if password == v_passw:
            session_token = str(uuid.uuid4())
            mongo.db.voluntere.update({"email": email},{"$set": {"session_token": session_token}})
            response_message = make_login_response("successful login", session_token)
        else:
            response_message = make_error_response(2, "password error", "user not logged in")
    return jsonify(response_message)



@app.route("/", methods=['GET', 'POST'])
def index():
    return "wecare for people"
    pass


#this will be used to see all available products
@app.route("/product-detail/<string:session_token>/", methods=['GET'])
def product_detail(session_token):
    user_id = authenticate(session_token)
    
    if user_id:
        query = mongo.db.product.find()
        jsondata={}
        productlist = []
        product = {}
        for data in query:
            product['product_catagory'] = data.get("product_catagory")
            product["product_description"]  = data.get("product_description")
            product["p_id"] = str(data.get("_id"))
            product["collected_by"] = str(data.get("collected_by"))
            product["status"] = data.get("status")
            if product["status"] == "donated":
                continue
            elif not product["status"]:
                product["status"] = "available"
                productlist.append(product)
                product = {} 
            else:
                productlist.append(product)
                product = {}
        jsondata["data"] = productlist
        response_message = jsondata
    else:
        response_message = make_error_response(2, "user not logged in", "please login first")
    return jsonify(response_message)



@app.route("/activity-recent/<string:session_token>/", methods=['GET'])
def activity_recent(session_token):
    user_id = authenticate(session_token)
    if user_id:
        query = mongo.db.activity.find()
        jsondata={}
        activitylist = []
        acitvity = {}
        for data in query:
            flag = False
            for item in activitylist:
                if item.get("product_id")==str(data.get('product_id')) :
                    flag = True
            if not flag:
                acitvity['voluntere_name'] = data.get("voluntere_name")
                acitvity["recipient_district"]  = data.get("recipient_district")
                acitvity["product_id"] = str(data.get("_id"))
                acitvity["product_catagory"] = data.get("product_catagory")
                acitvity["recipient"] = data.get("recipient")
                acitvity["product_location"] = data.get("product_location")
                activitylist.append(acitvity)
                acitvity={}
            else:
                continue
        jsondata["data"] = activitylist
        response_message = jsondata
    else:
        response_message = make_error_response(3, "login first !!", "session_expired")
    
    return jsonify(response_message)



@app.route("/donate-product/<string:session_token>/<string:product_id>/<string:recipient>/", methods=['GET'])
@app.route("/donate-product/<string:session_token>/<string:product_id>/<string:recipient>/<string:recipient_district>/", methods=['GET'])
def donate(session_token, product_id, recipient, recipient_district=None):
    user_id = authenticate(session_token)
    if user_id:
        v_id = ObjectId(user_id)
        p_id = ObjectId(product_id)
        if not recipient_district:
            recipient_district=""
        voluntere_info = mongo.db.voluntere.find_one({"_id": v_id})
        product_info = mongo.db.product.find_one({"_id": p_id})
        activity_doc = {
            "voluntere_name": voluntere_info.get("name"),
            "product_id": p_id,
            "voluntere_id": v_id,
            "recipient":  recipient,
            "recipient_district": recipient_district,
            "product_description": product_info.get("product_description"),
            "product_location": product_info.get("product_location"),
            "product_catagory": product_info.get("product_catagory"),
        }
        activity_id = mongo.db.activity.insert(activity_doc)
        mongo.db.product.update({"_id": p_id},{"$set": {"status": "donated"}})
        response_message = make_user_response(0, "donated successfully")
    else:
        response_message = make_error_response(3, "login first !!", "session_expired")
    
    return str(response_message)



if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
