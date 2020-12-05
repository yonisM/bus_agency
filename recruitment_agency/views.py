"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request
from recruitment_agency import app
import datetime
import os
import psycopg2
import boto3 
import random
import sys

#Connect to DB in Heroku
DATABASE_URL = 'postgres://naklrgmdeynszc:a03d0b95cbb2206a92c944ef4cff01ba95b342faea3adadf32915dc48e576993@ec2-34-252-98-12.eu-west-1.compute.amazonaws.com:5432/d1v07fd1ie2qui'
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


#Conenct to AWS
ACCESS_KEY="AKIAJINQRSUQW2XDYM4A"
SECRET_KEY="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"
s3 = boto3.client('s3',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)




@app.route('/', methods=["GET","POST"])
@app.route('/home')
def home():
    """Renders the home page."""

    if request.method == "POST":

            fullname = request.form.get("Fullname")
            email = request.form.get("email")
            postcode = request.form.get("postcode")

            random_number = random_number = random.randrange(10000,999999999999999999999999999)
            

            #Get the files that have been uploaded by user
            image_drivers_licence = request.files["licence"]
            image_CPC = request.files["CPC"]
            image_CV = request.files["CV"]

            #Get the name of the file uploaded by user
            get_filename_driver = image_drivers_licence.filename
            get_filename_CPC = image_CPC.filename
            get_filename_CV = image_CV.filename


            #Adding random values in fromt of filename to prevent S3 from rejecting duplicate names
            name_filename_licence = str(random_number) + get_filename_driver
            name_filename_CPC = str(random_number) + get_filename_CPC
            name_filename_CV = str(random_number) + get_filename_CV
           



            #Send data to the database and S3
            try: 
                with conn:
                    with conn.cursor() as cursor:

                        #Return URL of file uploaded to S3
                        drivers_licence = "https://busrecruitmentagency.s3.eu-west-2.amazonaws.com/" + name_filename_licence
                        cpc = "https://busrecruitmentagency.s3.eu-west-2.amazonaws.com/" + name_filename_CPC
                        cv = "https://busrecruitmentagency.s3.eu-west-2.amazonaws.com/" + name_filename_CV


                        #Add the data into the database
                        cursor.execute("INSERT into applicants VALUES(%s, %s, %s, %s, %s, %s);", (
                        fullname,
                        email,
                        postcode,
                        drivers_licence,
                        cpc,
                        cv
                        ))

                        #Upload the user's uploaded file to S3
                        s3.put_object(ACL='public-read', Body=image_drivers_licence, Bucket='busrecruitmentagency', Key=name_filename_licence)
                        s3.put_object(ACL='public-read', Body=image_CPC, Bucket='busrecruitmentagency', Key=name_filename_CPC)
                        s3.put_object(ACL='public-read', Body=image_CV, Bucket='busrecruitmentagency', Key=name_filename_CV)

                        
                        success = "Thanks, " + fullname + " we are working to process all applicants. We will get in touch with when we find a suitable opportunity."
                        

                        return render_template('confirmation.html', title='Confirmation', fullname=fullname, email=email, success=success)


            except psycopg2.errors.UniqueViolation:
                dupe = "Sorry, you have already submitted your application with us before. Once we find a suitable role, we will get in touch with you."
                return render_template('confirmation.html', title='Duplicate data', dupe=dupe, fullname=fullname, email=email)

    return render_template('index.html', title='Integrated Group Limited')

