from flask import Flask, abort,jsonify, request, render_template, redirect, url_for
import json,sys,urllib2,os
from functools import wraps
import analyze

app = Flask(__name__)
app.classifier = analyze.analyze()

def jsonp(f):
    """Wraps JSONified output for JSONP"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            content = str(callback) + '(' + str(f().data) + ')'
            return app.response_class(content, mimetype='application/json')
        else:
            return f(*args, **kwargs)
    return decorated_function


@app.route('/test')
def testClassifier():
	text = request.args['text'] if request.args['text'] else ''
	result = dict(prediction=0)
	if text:
		result['prediction'] = app.classifier.predictText(text)
	
	return jsonify( result )


if __name__ == '__main__':
    app.run(debug=True)










