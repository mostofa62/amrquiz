from datetime import datetime
import random
import uuid
from bson import ObjectId
import pytz
from app import app
from db import my_col
from flask import flash, render_template, request, redirect, url_for, session

questions_collection = my_col("questions")
results_collection = my_col("results_doctors")
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


@app.route("/amrquiz/dc-startquiz", methods=["GET"])
def dc_start_quiz():

    doctor_id = session.get("doctor_id")
    now = datetime.now(pytz.utc)
    
    if not doctor_id:
        # If no doctor ID in session, redirect to the home page (or an error page)
        flash("No professioanl found. Please register first.", "danger")
        return redirect(url_for("doctor_form"))
    # Record the start time in session
    session['start_time'] = now
    # Set maximum time for quiz (2 minutes = 120 seconds)
    session['max_time'] = 900  # in seconds    
    first_question = questions_collection.find_one(sort=[("question_id", 1)])  # Get the first question

    results_collection.insert_one({
        "doctor_id":ObjectId(doctor_id),
        "start_time":now
    })
    return redirect(url_for("dc_display_question", question_id=first_question["question_id"]))


def make_aware(datetime_obj, timezone='UTC'):
    if datetime_obj.tzinfo is None:
        tz = pytz.timezone(timezone)
        datetime_obj = tz.localize(datetime_obj)
    return datetime_obj

@app.route("/amrquiz/dc-question/<string:question_id>", methods=["GET"])
def dc_display_question(question_id):
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
    return render_template("dc_single_question.html", question=question, minutes=minutes, seconds=seconds)


@app.route("/amrquiz/dc-submit-answer/<string:question_id>", methods=["POST"])
def dc_submit_answer(question_id):
    user_answer = request.form.getlist("answer")  # Get the user's selected answer(s)    
    next_question = questions_collection.find_one({"question_id": {"$gt": question_id}}, sort=[("question_id", 1)])

    if next_question:
        # Shuffle the 'options' array if it exists
        if 'options' in next_question:
            random.shuffle(next_question['options'])

    doctor_id = session.get("doctor_id")

    # Store the answer in the results collection
    # results_collection.insert_one({
    #     "doctor_id": ObjectId(doctor_id),  # Replace with actual user ID logic
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
            'doctor_id':ObjectId(doctor_id)
        },{
            '$set':{
                "form_id":form_id,
                'time_elapsed':round(time_elapsed),
                question_id: {"answer": user_answer},
            }
        })
    
    
        
    if time_elapsed >= session['max_time']:
        # If time is up, submit the quiz and redirect to final page
        return redirect(url_for("dc_final_submission"))
    
    if next_question:
        return redirect(url_for("dc_display_question", question_id=next_question["question_id"]))
    else:
        return redirect(url_for("dc_final_submission"))
    


@app.route("/amrquiz/dc-final-submission", methods=["GET"])
def dc_final_submission():
    doctor_id = session.get("doctor_id")

    form_id = session.get('form_id')

    results_collection.update_one({
        'doctor_id':ObjectId(doctor_id)
    },{
        '$set':{
            'end_time': datetime.now(),
        }
    })
    session.clear()
    # Here you can save the results or process them
    return render_template('thank_you.html', form_id=form_id)