from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
from app import app

from db import my_col
from util import *

questions_collection = my_col("questions")
results_collection = my_col("results")
results_collection_dc = my_col("results_doctors")
students = my_col('students')






def evaluate_students(questions, student_answers):
    """
    Evaluates students' answers, calculates scores, and ranks students based on score and time_elapsed.

    :param questions: List of questions with their correct answers.
    :param student_answers: List of students' answers and metadata (e.g., time_elapsed).
    :param students_collection: MongoDB collection to fetch student details.
    :return: Sorted list of student results.
    """
    student_results = []  # List to store results for each student

    for student in student_answers:
        student_id = student["student_id"]
        time_elapsed = student.get("time_elapsed", float("inf"))  # Default to max if missing
        total_score = 0  # Track the student's total score
        question_scores = {}  # Store scores for individual questions

        # Fetch student details from the database
        student_data = students.find_one({"_id": ObjectId(student_id)})

        #print(student_data)

        # Evaluate answers for each question
        for question in questions:
            question_id = question["question_id"]
            correct_answers = set(question["correct_answers"])
            student_answer_entry = student.get(question_id, {})
            print(student_id,student_answer_entry)
            student_answers_set = set(student_answer_entry.get("answer", []))

            # # Check if the question was not answered
            # if not student_answers_set:
            #     question_scores[question_id] = {"score": 0, "remark": "No answer given"}
            #     continue

            # Validate single-choice question format
            # if len(correct_answers) == 1 and len(student_answers_set) > 1:
            #     question_scores[question_id] = {
            #         "score": 0,
            #         "remark": "Invalid single-choice answer format"
            #     }
            #     continue

            # Calculate score
            if len(correct_answers) > 1:  # Multiple correct answers
                matched = len(correct_answers & student_answers_set)
                score = 0.5 * matched  # Each correct match = 0.5
            else:  # Single correct answer
                score = 1 if student_answers_set == correct_answers else 0

            question_scores[question_id] = {
                "score": score,
                #"remark": "Valid answer",
                "correct_answers": list(correct_answers),
                "student_answers": list(student_answers_set)
            }
            total_score += score

        

        # Store the results for this student
        student_results.append({
            "student_id": student_id,
            "student_data": student_data,
            "total_score": total_score,
            "time_elapsed": time_elapsed,
            "question_scores": question_scores
        })
        

    # Sort results by total_score (descending) and time_elapsed (ascending)
    student_results.sort(key=lambda x: (-x["total_score"], x["time_elapsed"]))
    return student_results

@app.route("/amrquiz/result", methods=["GET"])
def result():

    query = {
        "$and": [{"q{}".format(i): {"$exists": True}} for i in range(1, 16)]
    }

    student_answers = list(results_collection.find(query))


    questions = list(questions_collection.find({}).sort([("question_id", 1)]))


    student_results = evaluate_students(questions, student_answers)

    # data_json = MongoJSONEncoder().encode(results)
    # results = json.loads(data_json)

    # return jsonify({
    #     'result':results
    # })

    return render_template('results.html', student_results=student_results)


from collections import Counter

def calculate_question_statistics(questions, student_answers):
    statistics = {}

    for question in questions:
        question_id = question["question_id"]
        question_label = question["question_label"]
        correct_answers = set(question["correct_answers"])  # Correct answers for the question
        options = {option["option_id"]: option["option_label"] for option in question["options"]}
        all_answers = []  # Collect all answers provided for this question

        # Collect answers for the current question from all students
        for student in student_answers:
            student_answer_entry = student.get(question_id, {})
            student_answers_list = student_answer_entry.get("answer", [])
            all_answers.extend(student_answers_list)

        # Calculate answer percentages
        total_responses = len(all_answers)
        if total_responses > 0:
            answer_counts = Counter(all_answers)
            answer_percentages = [
                {
                    "option_id": answer,
                    "option_label": f"{options.get(answer, 'Unknown Option')} {'(Correct)' if answer in correct_answers else ''}",
                    "percentage": (count / total_responses) * 100,
                    "is_correct": answer in correct_answers
                }
                for answer, count in answer_counts.items()
            ]
        else:
            answer_percentages = []

        # Store statistics for the question
        statistics[question_id] = {
            "question_label": question_label,
            "total_responses": total_responses,
            "answer_percentages": answer_percentages,
            "correct_answers": list(correct_answers)  # Include correct answers for reference
        }

    return statistics




@app.route("/amrquiz", methods=["GET"])
def home():
    #student_answers = list(results_collection_dc.find({}))
    student_answers = list(results_collection.find({}))


    questions = list(questions_collection.find({}).sort([("question_id", 1)]))


    statistics = calculate_question_statistics(questions, student_answers)
    #return "<h1>Please dont come here its abandoned!</h1>"
    #data_json = MongoJSONEncoder().encode(student_results)
    #results = json.loads(data_json)

    #return jsonify({
    #     'result':results
    #})

    return render_template("statistics.html", statistics=statistics)
