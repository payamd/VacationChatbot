from flask import Flask, render_template, request
from flask_cors import CORS
import json

# Intent service could be hosted remotely but for this project is hosted locally
from IntentService import getIntent

# The question resolution service could be hosted remotely or locally.

# QAVacationService is local
import QAVacationService

# WolframAlpha is an example of remote access
import WolframAlphaService


# Initializing Flask
app = Flask(__name__)

# Required for html page to interact with other sites
CORS(app)  # Enable CORS for all routes


# Defining a route for the root URL '/'
@app.route('/')
# When the route URL is accessed, render and return the 'index.html' template
def index():
    return render_template('index.html')

# Create endpoint to cater input query of Exploria


# Helper function to determine if the intent classification is a greeting
def isGreetingIntent(intent_classification):
    if (intent_classification == "greeting"):
        return True
    return False

# Helper function to determine if the intent classification is a lifestyle intent (offline mode)


def isLifestyleIntent(intent_classification):
    #
    # Make a list of all the intents that match to lifestyle
    # Travel, Movie, Cooking
    #
    allowed_classifications = ["cook_time", "travel_alert",
                               "travel_suggestion", "travel_notification", "international_visa", "movie"]

    return intent_classification in allowed_classifications

# Defining a route for '/submit', accepting both GET and POST methods


@app.route('/submit', methods=["GET", "POST"])
def processInputQuery():
    # getting  JSON data from the request
    req = request.get_json()
    if req is not None and "msg" in req:
        # extract message from the request
        utterance = req["msg"]

        #
        # The intent service could be remotely hosted and returns the intent classification with a confidence score.
        #
        # Call the getIntent function to classify the intent of the utterance.
        intent_json = json.loads(getIntent(utterance))
        intent_classification = intent_json["intent"]
        confidence_score = intent_json["confidence"]

        # dissambiguation prompt for when the intent detection confidence score is below 20
        if (confidence_score < 20):
            return "I didn't understand, please rephrase your question."
# First sentence of response for any utterance with intent confident over 20.
        # gives the confidence score and the intent
        response = f"I am {confidence_score} percent confident you asked about '{intent_classification}'"
        # Custom Aswers to append to response
        if (isLifestyleIntent(intent_classification)):
            #
            # Specialized responses for custom category
            #
            answer = QAVacationService.getAnswer(utterance)
            response = response + ".  " + answer

        elif (isGreetingIntent(intent_classification)):
            #
            # Custom Greeting
            #
            response = "Hello this is Exploria.  Ask me any question."
        else:
            #
            # General knowledge query will go to WolframAlpha
            #
            answer = WolframAlphaService.getAnswer(utterance)
            response = response + ".  " + answer

        return response
    else:
        return "Invalid input"


# Main to run the server on specific port
if __name__ == '__main__':
    app.run(debug=False, port=2412)
