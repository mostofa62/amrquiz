from flask import Flask, render_template, request, redirect, session, url_for, flash
from app import app
from db import my_col
students = my_col('students')

clg_students = my_col('clg_students')
uni_students = my_col('uni_students')

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



@app.route("/amrquiz/college", methods=["GET", "POST"])
def create_college():
    if request.method == "POST":
        # Get form data
       
        #contact_number = request.form.get("contact_number")
        email = request.form.get("email")

        data  = request.form.to_dict()

        # Check if the email already exists in the database
        if students.find_one({"email": email}):
            flash("Email already exists. Please use a different one.", "danger")
            return redirect(url_for("create_student"))
        
        # Insert student data into MongoDB
        student_data = data
        
        student = clg_students.insert_one(student_data)

        student_id = str(student.inserted_id)
        # Store the student ID in the session
        session["student_id"] = student_id
        
        flash("Student added successfully!", "success")
        
        # Redirect to the startquiz URL
        return redirect(url_for("start_quiz_df"))
    
    return render_template("create_student_cu.html",title='')




@app.route("/amrquiz/university", methods=["GET", "POST"])
def create_university():
    if request.method == "POST":
        email = request.form.get("email")

        data  = request.form.to_dict()

        # Check if the email already exists in the database
        if students.find_one({"email": email}):
            flash("Email already exists. Please use a different one.", "danger")
            return redirect(url_for("create_student"))
        
        # Insert student data into MongoDB
        student_data = data
        
        student = uni_students.insert_one(student_data)

        student_id = str(student.inserted_id)
        # Store the student ID in the session
        session["student_id"] = student_id
        
        flash("Student added successfully!", "success")
        
        # Redirect to the startquiz URL
        return redirect(url_for("start_quiz_dfu"))
    
    return render_template("create_student_cu.html",title='University')
