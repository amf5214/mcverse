from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

with app.app_context():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mcverse.db"
    db = SQLAlchemy(app)

    db.create_all()


@app.route('/')
def go_home():
    return render_template('index.html')


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contactus')
def contactus():
    return render_template('index.html')


if __name__ == '__main__':
   app.run(debug=True, port=54913)
   