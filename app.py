from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/sic-assigment-2"

mongo = PyMongo(app)
sensors_collection = mongo.db.sensors

@app.route('/sensor', methods=['POST'])
def insert_value_sensor():
    for sensor in request.json["sensor"] :
        if(sensors_collection.find_one({ "name": sensor }) != None) :
            sensors_collection.update_one({ "name": sensor }, { "$set" : { "value": request.json["sensor"][sensor] }})
        else :
            sensors_collection.insert_one({ "name": sensor, "value": request.json["sensor"][sensor] })
        
    return jsonify({"message": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)