from flask import Flask, render_template, request, redirect, session, url_for, flash
from app import app
from db import my_col
students = my_col('students')

@app.route("/amrquiz/student", methods=["GET", "POST"])
def create_student():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        college_name = request.form.get("college_name")
        year_and_session = request.form.get("year_and_session")
        contact_number = request.form.get("contact_number")
        email = request.form.get("email")

        # Check if the email already exists in the database
        if students.find_one({"email": email}):
            flash("Email already exists. Please use a different one.", "danger")
            return redirect(url_for("create_student"))
        
        # Insert student data into MongoDB
        student_data = {
            "name": name,
            "age": age,
            "gender": gender,
            "college_name": college_name,
            "year_and_session": year_and_session,
            "contact_number": contact_number,
            "email": email,
        }
        
        student = students.insert_one(student_data)

        student_id = str(student.inserted_id)
        # Store the student ID in the session
        session["student_id"] = student_id
        
        flash("Student added successfully!", "success")
        
        # Redirect to the startquiz URL
        return redirect(url_for("start_quiz"))
    
    return render_template("create_student.html")
