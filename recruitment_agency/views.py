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

#Connect to DB in Heroku
DATABASE_URL = 'postgres://nmycutomhjtncr:b8edfa3aaef122b3c98ad93d02487274627d438213a639e5b6d6151a4242a6d8@ec2-54-246-87-132.eu-west-1.compute.amazonaws.com:5432/d9bv6qupiocakn'
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


#Conenct to AWS
ACCESS_KEY="AKIAJINQRSUQW2XDYM4A"
SECRET_KEY="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"
s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)




@app.route('/', methods=["GET","POST"])
@app.route('/home')
def home():
    """Renders the home page."""

    if request.method == "POST":

            fullname = request.form.get("Fullname")
            email = request.form.get("email")
            postcode = request.form.get("postcode")
            licence = request.form.get("licence")
            CPC = request.form.get("CPC")
            CV = request.form.get("CV")

            random_number = random_number = random.randrange(10000,999999999999999999999999999)
            

            #Upload files to images
            if  request.files:
                
                image = request.files["licence"]
                get_filename = image.filename
                name_filename = str(random_number) + get_filename

                #Upload file to AWS S3
                s3.Bucket("busrecruitmentagency").put_object(Key=name_filename, Body=image)

            
            #Send data to the database
            try: 
                with conn:
                    with conn.cursor() as cursor:
                        cursor.execute("INSERT into applicants VALUES(%s, %s, %s);", (
                        fullname,
                        email,
                        postcode
                        ))

                        success = "Thanks, " + fullname + " we are working to process all applicants. We will get in touch with when we find a suitable opportunity."
                        

                        return render_template('confirmation.html', title='Home Page', fullname=fullname, email=email, success=success)


            except psycopg2.errors.UniqueViolation:
                dupe = "Sorry, you have already submitted your application with us before. Once we find a suitable role, we will get in touch with you."
                return render_template('confirmation.html', title='Home Page', dupe=dupe, fullname=fullname, email=email)

    return render_template('index.html', title='Home Page')

