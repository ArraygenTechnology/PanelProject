from . import *
from .models import patients, panels


@app.route('/patient/', defaults={'id': 0})
@app.route('/patient/<id>')
def patient(id):
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        all_patients = patients.Patients.query.all()
        if id == 0:
            # For Add patirnt view
            panels_obj = panels.Panels.query.order_by(panels.Panels.id).all()
            last_patient = patients.Patients.query.order_by(patients.Patients.id.desc()).first()
            if last_patient == None:
                patient_id = "SWCA00001"
            else:
                patient_id = last_patient.patient_id
                chr1 = patient_id[3]
                num = int(patient_id[4:])+1
                if num > 99999:
                    chr1 = chr(ord(chr1)+1)
                    num = 1
                patient_id = patient_id[:3]+chr1+(str(num).zfill(5))
            return render_template('patients.html', panels= panels_obj , patient_id=patient_id, patients = all_patients)
        else:
            # this for edit view
            panels_obj = panels.Panels.query.order_by(panels.Panels.id).all()
            exists = patients.Patients.query.get(id)
            if exists == None:
                return redirect("/bad_request")
            else:
                """ print(exists)
                print(exists.panels)"""
                return render_template('patients.html', panels= panels_obj, patient = exists , patients = all_patients)
    else:
        return redirect("/bad_request")

# Add or Update Users
@csrf.exempt
@app.route('/patients_add_update', defaults={'id':0}, methods = ['GET', 'POST'])
@app.route('/patients_add_update/<int:id>', methods = ['GET', 'POST'])
def patients_add_update(id):
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        if request.method == 'POST':
            data = request.form

            all_data = data.to_dict()
            if "panel" in data.keys():
                del all_data['panel']
            del all_data['csrf_token']
            # update patient information
            if id != 0:
                update_patient = patients.Patients.query.get(id)
                exists = patients.Patients.query.filter_by(email=all_data.get('email')).first()
                for attr_name, new_value in all_data.items():
                    setattr(update_patient, attr_name, new_value)

                patient_panels = data.getlist('panel')

                update_patient.panels = [panels.Panels.query.get(p_id) for p_id in patient_panels]
                #print(update_patient.panels)
                if exists == None:
                    update_patient.email = all_data.get('email')
                elif exists.id == id:
                    pass
                else:
                    flash("Email id not updated because it's email already exists".title(), "warning")
                db.session.commit()
                flash("Patient Information Updated Successfully".title(), "info")
            else:
            # add new patient details
                # get if any exists , with same email id
                exists =  patients.Patients.query.filter_by(email=all_data.get('email')).first()
                if exists == None:
                    # creating object
                    patient = patients.Patients(**all_data)
                    # get panels selected and appending it to parameter so that it can add it to relational table
                    patient_panels = data.getlist('panel')
                    for panel in patient_panels:
                        patient.panels.append(panels.Panels.query.get(panel))
                    db.session.add(patient)
                    db.session.commit()
                    flash("Patient Added Successfully".title(), "info")
                else:
                    flash("Patient Already Exists".title(), "error")
        return redirect('/patient')
    else:
        return redirect("/bad_request")

@app.route('/patients_view')
def patients_view():
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        patients_panels_refid = db.session.query(patients.Patients, panels.Panels, patients.Patient_panels).filter(
            patients.Patient_panels.panel_id == panels.Panels.id,
            patients.Patient_panels.patient_id == patients.Patients.id).order_by(patients.Patients.id).all()
        return render_template('patients_view.html', patients_panels_refid= patients_panels_refid)
    else:
        return redirect("/bad_request")


@app.route('/patient_delete/<id>')
def patient_delete(id):
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        uploaded_files = patients.Patient_panels.query.filter(patients.Patient_panels.patient_id == id)
        for file in uploaded_files:
            if file.dna_results != None:
                os.remove(os.path.join("/".join(app.root_path.split("/")[:-1]), app.config['UPLOAD_FOLDER'],file.dna_results))

            if file.blood_results != None:
                os.remove(os.path.join("/".join(app.root_path.split("/")[:-1]), app.config['UPLOAD_FOLDER'],file.blood_results))

            if file.allergy_results != None:
                os.remove(os.path.join("/".join(app.root_path.split("/")[:-1]), app.config['UPLOAD_FOLDER'],file.allergy_results))

            print(file.dna_results , file.blood_results , file.allergy_results)
        delete_patient = patients.Patients.query.get(id)

        db.session.delete(delete_patient)
        db.session.commit()
        flash("User Deleted Successfully".title(), "info")
        return redirect("/patient")
    else:
        return redirect("/bad_request")

# For Ajax
@csrf.exempt
@app.route('/getPatientById', methods=['POST'])
def getPatientById():
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        patient = patients.Patients.query.get(request.form['id'])
        patient_schema = patients.PatientsSchema()
        op = patient_schema.dumps(patient)
        return jsonify(op)
    else:
        return redirect("/bad_request")

@csrf.exempt
@app.route('/sendEmail', methods=['POST'])
def sendEmail():
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        '''
               msg = Message(request.form['subject'], sender='bioinformatics.arraygen.ak@gmail.com', recipients=[request.form['to']])
               msg.html = request.form['message']
               if len(request.files.getlist('attachment')) > 0:
                   for file in request.files.getlist('attachment'):
                       msg.attach(secure_filename(file.filename), file.content_type, file.read())
               mail.send(msg)
        '''
        update_patient_panels = patients.Patient_panels.query.get(
            (request.form['id'], request.form['patient_id'], request.form['panel_id']))
        #print(update_patient_panels)
        setattr(update_patient_panels, "send", 1)
        setattr(update_patient_panels, "send_date", datetime.datetime.now())
        db.session.commit()

        # Send Email Via Cloud
        region = "ap-south-1"
        sws_user = 'AKIA6GL7YMRN4LD7OJ4B'
        sws_key = 'd9yHTTMTe0J9a+D5gHlOpcWw+PUWJeIRWExvZiM3'
        subject = request.form['subject']
        body = request.form['message']

        client = boto3.client(service_name='ses', region_name=region, aws_access_key_id=sws_user,
                              aws_secret_access_key=sws_key)

        message = MIMEMultipart()
        message['Subject'] = subject
        message['From'] = 'bioinformatics.arraygen.ak@gmail.com'
        message['To'] = request.form['to']

        # message body
        part = MIMEText(body, 'html')
        message.attach(part)
        #print(request.files.getlist('attachment'))
        if len(request.files.getlist('attachment')) > 0:
            for file in request.files.getlist('attachment'):
                txt = file.read()
                part = MIMEApplication(txt)
                part.add_header('Content-Disposition', 'attachment', filename=secure_filename(file.filename))
                message.attach(part)
        try:

            result = client.send_raw_email(Source=message['From'], Destinations=[message['To'],],
                                           RawMessage={'Data': message.as_string(), })
            #return {'message': 'error', 'status': 'fail'} if 'ErrorResponse' in result else {
            #'message': 'mail sent successfully', 'status': 'success'}'''
        except ClientError as e:
            return {'message': e.response['Error']['Message'], 'status': 'fail'}


        flash("Email Is Sent Successfully To "+request.form['to'], "info")
        return redirect("/patients_view")
    else:
        return redirect("/bad_request")

# For Ajax
@csrf.exempt
@app.route('/updatePatientTechnicianStatus', methods=['POST'])
def updatePatientTechnicianStatus():
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        update_patient_panels = patients.Patient_panels.query.get((request.form['id'], request.form['patient_id'], request.form['panel_id']))
        setattr(update_patient_panels , "technician_status" , request.form['technician_status'])
        setattr(update_patient_panels , "technician_status_date" , datetime.datetime.now())
        db.session.commit()
        patient_panel_schema = patients.Patient_panelsSchema()
        op = patient_panel_schema.dumps(update_patient_panels)
        return op
    else:
        return redirect("/bad_request")

# For Ajax
@csrf.exempt
@app.route('/getPatientPhysicianDetails', methods=['POST'])
def getPatientPhysicianDetails():
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        get_patient_panels = patients.Patient_panels.query.get((request.form['id'], request.form['patient_id'], request.form['panel_id']))
        patient_panel_schema = patients.Patient_panelsSchema()
        op = patient_panel_schema.dumps(get_patient_panels)
        return jsonify(op)
    else:
        return redirect("/bad_request")


