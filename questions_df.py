from datetime import datetime
import random
import uuid
from bson import ObjectId
import pytz
from app import app
from db import my_col
from flask import flash, render_template, request, redirect, url_for, session

questions_collection = my_col("questions_dfest")
results_collection = my_col("results_dfest")
'''
@app.route("/amrquiz", methods=["GET"])
def display_questions():
    questions = list(questions_collection.find())
    #print(questions)
    return render_template("questions.html", questions=questions)


@app.route("/amrquiz/submit-answers", methods=["POST"])
def submit_answers():
    user_answers = request.form.to_dict(flat=False)
    results_collection.insert_one({
        "user_id": "anonymous",  # Replace with actual user identification logic
        "answers": user_answers
    })
    return redirect(url_for("thank_you"))

@app.route("/amrquiz/thank-you", methods=["GET"])
def thank_you():
    return "<h1>Thank you for submitting your answers!</h1>"

'''


@app.route("/amrquiz/startquizdf", methods=["GET"])
def start_quiz_df():

    student_id = session.get("student_id")
    now = datetime.now(pytz.utc)
    
    if not student_id:
        # If no student ID in session, redirect to the home page (or an error page)
        flash("No student found. Please register first.", "danger")
        return redirect(url_for("create_college"))
    # Record the start time in session
    session['start_time'] = now
    # Set maximum time for quiz (2 minutes = 120 seconds)
    session['max_time'] = 600  # in seconds    
    first_question = questions_collection.find_one(sort=[("question_id", 1)])  # Get the first question

    results_collection.insert_one({
        "student_id":ObjectId(student_id),
        "start_time":now,
        'type':1
    })
    return redirect(url_for("display_question_df", question_id=first_question["question_id"]))


@app.route("/amrquiz/startquizdfu", methods=["GET"])
def start_quiz_dfu():

    student_id = session.get("student_id")
    now = datetime.now(pytz.utc)
    
    if not student_id:
        # If no student ID in session, redirect to the home page (or an error page)
        flash("No student found. Please register first.", "danger")
        return redirect(url_for("create_university"))
    # Record the start time in session
    session['start_time'] = now
    # Set maximum time for quiz (2 minutes = 120 seconds)
    session['max_time'] = 600  # in seconds    
    first_question = questions_collection.find_one(sort=[("question_id", 1)])  # Get the first question

    results_collection.insert_one({
        "student_id":ObjectId(student_id),
        "start_time":now,
        'type':2
    })
    return redirect(url_for("display_question_df", question_id=first_question["question_id"]))


def make_aware(datetime_obj, timezone='UTC'):
    if datetime_obj.tzinfo is None:
        tz = pytz.timezone(timezone)
        datetime_obj = tz.localize(datetime_obj)
    return datetime_obj

@app.route("/amrquiz/questiondf/<string:question_id>", methods=["GET"])
def display_question_df(question_id):
    # Get the question from the database
    question = questions_collection.find_one({"question_id": question_id})

    if question:
        # Shuffle the 'options' array if it exists
        if 'options' in question:
            random.shuffle(question['options'])

    # Initialize start_time if not set in the session
    if 'start_time' not in session:
        # Save the start time in session as aware time (UTC timezone)
        session['start_time'] = make_aware(datetime.now(), timezone='UTC')
        session.modified = True  # Mark session as modified to persist it

    # Get start time from session
    start_time = session.get('start_time')

    # Get the current time
    now = datetime.now(pytz.utc)  # Current time in UTC (aware)
    
    # Calculate the time difference
    time_elapsed = (now - start_time).total_seconds()
    
    time_left = max(session['max_time'] - time_elapsed, 0)  # Remaining time in seconds

    # Round time_left to nearest integer
    time_left = round(time_left)

    # Convert time_left to minutes and seconds
    minutes = time_left // 60
    seconds = time_left % 60

    # Render the template with the time left and question
    return render_template("single_question_cu.html", question=question, minutes=minutes, seconds=seconds)


@app.route("/amrquiz/submit-answer-df/<string:question_id>", methods=["POST"])
def submit_answer_df(question_id):
    user_answer = request.form.getlist("answer")  # Get the user's selected answer(s)    
    next_question = questions_collection.find_one({"question_id": {"$gt": question_id}}, sort=[("question_id", 1)])

    if next_question:
        # Shuffle the 'options' array if it exists
        if 'options' in next_question:
            random.shuffle(next_question['options'])

    student_id = session.get("student_id")

    # Store the answer in the results collection
    # results_collection.insert_one({
    #     "student_id": ObjectId(student_id),  # Replace with actual user ID logic
    #     "question_id": question_id,
    #     "answer": user_answer
    # })

    form_id = str(uuid.uuid4())  # Generates a unique UUID-based form_id
    session["form_id"] = form_id

    # Check if the time is up (2 minutes)
    start_time = session.get('start_time')
    
    if start_time:
        # Convert start_time to a naive datetime if it's aware
        if start_time.tzinfo is not None:
            start_time = start_time.replace(tzinfo=None)
            start_time = pytz.utc.localize(start_time)
        
        # Get the current time in naive format
        current_time = datetime.now(pytz.utc)
        
        # Calculate time elapsed
        time_elapsed = (current_time - start_time).total_seconds()

    if len(user_answer) > 0:

        results_collection.update_one({
            'student_id':ObjectId(student_id)
        },{
            '$set':{
                "form_id":form_id,
                'time_elapsed':round(time_elapsed),
                question_id: {"answer": user_answer},
            }
        })
    
    
        
    if time_elapsed >= session['max_time']:
        # If time is up, submit the quiz and redirect to final page
        return redirect(url_for("final_submission_df"))
    
    if next_question:
        return redirect(url_for("display_question_df", question_id=next_question["question_id"]))
    else:
        return redirect(url_for("final_submission_df"))
    


@app.route("/amrquiz/final-submission-df", methods=["GET"])
def final_submission_df():
    student_id = session.get("student_id")

    form_id = session.get('form_id')

    results_collection.update_one({
        'student_id':ObjectId(student_id)
    },{
        '$set':{
            'end_time': datetime.now(),
        }
    })
    session.clear()
    # Here you can save the results or process them
    return render_template('thank_you.html', form_id=form_id)