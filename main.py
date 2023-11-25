from flask import Flask, request

application = Flask(__name__)

@application.route("/", methods=["GET", "POST"])
def index():
    return "Hello world"

@application.route ( "/requestBody", methods = ["POST"] )
def requestBody ( ):
    result = "";
    for item in request.json.items ( ):
        result += str ( item[0] ) + ": " + str ( item[1] ) + ";";
    return result;

if(__name__ == "__main__"):
    application.run(debug=True)