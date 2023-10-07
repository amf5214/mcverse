from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

with app.app_context():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mcverse.db"
    db = SQLAlchemy(app)

    class FrequentlyAskedQuestion(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        author_user = db.Column(db.String, nullable=True)
        question = db.Column(db.String(200), nullable=True)
        answer = db.Column(db.String(200), default="")
        answer_author = db.Column(db.String(200), default="")

        def __repr__(self):
                return f"<FAQ {self.id}>"
        
        def to_string(self):
            return f"FAQ {self.id} by author {self.author_user}: {self.question}"

    db.create_all()


@app.route('/')
def go_home():
    frequently_asked_questions = FrequentlyAskedQuestion.query.order_by(FrequentlyAskedQuestion.id).all()
    return render_template('index.html', questions=frequently_asked_questions)


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contactus')
def contactus():
    return render_template('index.html')

@app.route('/newquestion', methods=['POST'])
def new_question():
    new_question = FrequentlyAskedQuestion(author_user=str(request.form["username"]), question=str(request.form["question"]))
    print(new_question.to_string())
    
    db.session.add(new_question)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
   app.run(debug=True, port=54913)
   