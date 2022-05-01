from flask_app import app
from flask import render_template, redirect, session

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/admin")
def admin():
    return render_template("admin.html")