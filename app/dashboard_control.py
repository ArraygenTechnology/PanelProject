from . import *
from .models import patients, panels, sys_users

@app.route('/', defaults={'user_type':'User'})
@app.route('/<user_type>')
def login(user_type):
    if user_type in ['User', 'Technician', 'Physician', 'Admin']:
        if "login_id" in session:
            if session.get("role") == "User":
                return redirect("/user_index")
            else:
                return redirect("/dashboard")
        else:
            return render_template('login.html' , user_type = user_type)
    else:
        return redirect("/")

@csrf.exempt
@app.route('/forgotPassword' , methods=['POST'])
def forgotPassword():
    email = request.form.get('email')
    if request.form.get('user_type') == "User":
        user = patients.Patients.query.filter(patients.Patients.email == email).first()
        if user != None:
            email_for_forgot_password(user.password, email, request.form.get('user_type'))
            flash("Check your registered email id".title(), "info")
        else:
            flash("Email is not registered".title(), "error")
    else:
        user = sys_users.Users.query.filter(sys_users.Users.email == email).first()
        if user != None:
            email_for_forgot_password(user.password, email, request.form.get('user_type'))
            flash("Check your registered email id".title(), "info")
        else:
            flash("Email is not registered".title(), "error")
    return redirect("/"+request.form.get('user_type'))


@app.route('/dashboard')
def dashboard():
    if "login_id" in session:
        sys_users_cnt = db.session.query(sys_users.Users).count()
        patients_cnt = db.session.query(sys_users.Users).count()
        return render_template('dashboard.html', sys_users_cnt=sys_users_cnt, patients_cnt= patients_cnt)
    else:
        return redirect("/bad_request")


@app.route("/bad_request")
def bad_request():
    if "login_id" in session:
        return render_template("bad_request_internal.html", img=("dist/img/HTTP-Error-404.png", "dist/img/HTTP-Error-404-mobile.png"))
    else:
        return render_template("bad_request.html", img=("dist/img/HTTP-Error-404.png", "dist/img/HTTP-Error-404-mobile.png"))


def email_for_forgot_password(password, email, user):
    SENDER = 'bioinformatics.arraygen.ak@gmail.com'
    RECIPIENT = email
    SUBJECT = "Account Details of Scientific Wellness Center"
    BODY_TEXT = ""
    BODY_HTML = """<html>
    <head></head>
    <body>
      <center>
        <img src ='http://65.0.162.4/static/dist/img/Logo.png' style='height:100px;width:auto;'/>
      </center>
      <p>Dear """+user+""",<br/>
      <p>As you have made request of forgot password. Your Account details are given below,<br/>
      <strong> User Name : </strong> """+email+"""<br/>
      <strong> Password : </strong> """+password+"""<br/>
      <a href= 'http://65.0.162.4/"""+user+"""'>Click here to login</a>
      </p>
    </body>
    </html>
    """

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    region = "ap-south-1"
    sws_user = 'AKIA6GL7YMRN4LD7OJ4B'
    sws_key = 'd9yHTTMTe0J9a+D5gHlOpcWw+PUWJeIRWExvZiM3'

    client = boto3.client(service_name='ses', region_name=region, aws_access_key_id=sws_user,
                          aws_secret_access_key=sws_key)

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])