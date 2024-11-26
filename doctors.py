from datetime import datetime
from bson import ObjectId
from flask import Flask, render_template, request, redirect, session, url_for, flash
from app import app
from db import my_col
doctors = my_col('doctors')



@app.route("/amrquiz/doctor", methods=["GET", "POST"])
def doctor_form():
    if request.method == "POST":
        # Handle form submission
        age = request.form["age"]
        gender = request.form["gender"]
        medical_college = request.form["medical_college"]
        specialty = request.form["specialty"]
        degree = request.form["degree"]

        # Create a unique submission form_id
       

        # Save the doctor's information into the database
        doctor_data = {
            "age": age,
            "gender": gender,
            "medical_college": medical_college,
            "specialty": specialty,
            "degree": degree,
            
            "submitted_at": datetime.now()
        }

        # Insert into the collection
        doctor =  doctors.insert_one(doctor_data)

        doctor_id = str(doctor.inserted_id)
        # Store the student ID in the session
        session["doctor_id"] = doctor_id
        
        flash("Professionals added successfully!", "success")
        
        # Redirect to the startquiz URL
        return redirect(url_for("dc_start_quiz"))

    # Handle GET request (render the form)
    return render_template("doctor_form.html")


