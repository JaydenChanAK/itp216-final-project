'''
Jayden Chan, jaydenc@usc.edu
ITP 216, Fall 2024
Section: 32080
Final Project
Description: This program implement logistic regression on a dataset of heart disease. This program will also allow for users to see the visualized dataset and make predictions based on user inputs.
'''
import io
import os
import sqlite3 as sl
import base64
import uuid

import pandas as pd
from flask import Flask, redirect, render_template, request, session, url_for, send_file
from matplotlib.figure import Figure
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)
db = "heart-disease.db"
user_predictions = {}

def query_database(query, path="heart-disease.db"):
	"""Executes an SQL query on the database and returns a dataframe.

	Args:
		query (str): The SQL query.
		path (str, optional): Defaults to "heart-disease.db".

	Returns:
		pd.DataFrame: The DataFrame.
	"""
	conn = sl.connect(db)
	df = pd.read_sql_query(query, conn)
	conn.close()
	return df

def train_model(features, target, df):
	"""Trains a logistic regression model.

	Args:
		features (list): List of column names.
		target (str): Column name of target.
		df (pd.DataFrame): DataFrame containing training data.

	Returns:
		LogisticRegression: Trained logistic regression model.
	"""
	model = LogisticRegression()
	model.fit(df[features], df[target])
	return model

def generate_plots(features, df):
	"""_summary_

	Args:
		features (list): List of column names.
		df (pd.DataFrame): DataFrame containing the dataset.

	Returns:
		list: List of encoded strings representing matplotlib graphs.
	"""
	urls = []
	for feature in features:
		fig = Figure()
		ax = fig.add_subplot()
		df.boxplot(column=feature, by='target', ax=ax, vert=False, grid=False)
		
		ax.set_title(f"{feature} Distribution by Heart Disease")
		ax.set_ylabel("Heart Disease (0: Negative, 1: Positive)")
		ax.set_xlabel(feature)
		ax.figure.suptitle("Graph for Existing Data")
		
		buf = io.BytesIO()
		fig.savefig(buf, format="png")
		buf.seek(0)
		plot_url = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
		urls.append(plot_url) 
	return urls
  
@app.route("/")
def home():
	return render_template("home.html")

@app.route("/data_visualization", methods=["GET", "POST"])
def data_visualization():
	df = query_database("SELECT * FROM heart_disease")

	if request.method == "POST":
		age_min = int(request.form.get("age_min", 0))
		age_max = int(request.form.get("age_max", 120))
		gender = int(request.form.get("gender", -1))

		if gender == 0 or gender == 1:
			df = df[df["sex"] == gender]
		df = df[(df["age"] >= age_min) & (df["age"] <= age_max)]

	features = [col for col in df.columns if col != "target"]
	urls = generate_plots(features, df)
	
	return render_template("data_visualization.html", plots=urls)

@app.route("/make_prediction", methods=["GET", "POST"])
def make_prediction():
	df = query_database("SELECT * FROM heart_disease")
	
	features = [col for col in df.columns if col != "target"]
	
	if request.method == "POST":
		user_input = {feature: float(request.form[feature]) for feature in features}
		
		model = train_model(features, "target", df)
		
		inputs = [user_input[feature] for feature in features]
		prediction = model.predict([inputs])[0]
		probability = model.predict_proba([inputs])[0][1]
		
		# Generate unique ID for predictions
		predictionID = str(uuid.uuid4())
		user_predictions[predictionID] = {"prediction": int(prediction), "probability": round(probability, 2)}
  
		return redirect(url_for("prediction_result", predictionID=predictionID))

	return render_template('make_prediction.html', features=features)

@app.route("/prediction/<predictionID>")
def prediction_result(predictionID):
	if predictionID not in user_predictions:
		return redirect(url_for("make_prediction"))

	result = user_predictions[predictionID]
	return render_template("prediction_result.html", result=result["prediction"], probability=result["probability"])

@app.route('/<path:path>')
def catch_all(path):
	return redirect(url_for("home"))

if __name__ == "__main__":
	app.secret_key = os.urandom(12)
	app.run(debug=True)