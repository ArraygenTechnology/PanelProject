from . import *
from .models import patients, panels

@app.route('/analysis_view')
def analysis_view():
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        technician_status = "Rejected"
        patients_panels_refid_rejected = db.session.query(patients.Patients, panels.Panels, patients.Patient_panels).filter(patients.Patient_panels.panel_id == panels.Panels.id,
            patients.Patient_panels.patient_id == patients.Patients.id,
            patients.Patient_panels.technician_status == technician_status).order_by(patients.Patients.id).all()
        #print(patients_panels_refid_rejected)
        patients_panels_refid_not_rejected = db.session.query(patients.Patients, panels.Panels, patients.Patient_panels).filter(
            patients.Patient_panels.panel_id == panels.Panels.id,
            patients.Patient_panels.patient_id == patients.Patients.id,
            ( (patients.Patient_panels.technician_status  == None) | (patients.Patient_panels.technician_status != technician_status))
        ).order_by(patients.Patients.id).all()


        return render_template('analysis.html',
                               patients_panels_refid_not_rejected = patients_panels_refid_not_rejected,
                               patients_panels_refid_rejected = patients_panels_refid_rejected)
    else:
        return redirect("/bad_request")

def pdf_genration_genetics(user, user_algo , start_name):
    os_path = os.getcwd()
    categories = panels.Category.query.filter(panels.Category.panel_id == user_algo.panel_id).order_by(panels.Category.rank.asc()).all()
    all_traits = [panels.Traits.query.filter(panels.Traits.category_id == category.id).all() for category in
                  categories]
    if  user_algo.dna_results != None:
        f = open(os.path.join(app.config['UPLOAD_FOLDER'], user_algo.dna_results))
        user_rs_id_dict = {}
        for line in f:
            splitted = line.strip().split("\t")
            user_rs_id_dict[splitted[0]] = splitted[-1]
        algorithm_info = []
        for traits in all_traits:
            for trait in traits:
                algo_list = []
                algo = panels.TraitAlgorithmInfo.query.filter(panels.TraitAlgorithmInfo.trait_id == trait.id).all()
                for data in algo:
                    if data.rs_id in user_rs_id_dict.keys():
                        user_genotype = user_rs_id_dict[data.rs_id]
                        if user_genotype == data.genotype:
                            algo_list.append(data)
                algorithm_info.append(algo_list)
        blood_dict = {}
        if user_algo.blood_results != None:
            f = open(os.path.join(app.config['UPLOAD_FOLDER'], user_algo.blood_results))
            for line in f:
                splitted = line.strip().split("\t")
                blood_data = panels.BloodAlgorithmInfo.query.filter(panels.BloodAlgorithmInfo.trait_id == int(splitted[0])).all()
                if len(blood_data) > 0:
                    blood_data = blood_data[0]
                    if blood_data.min != "" and blood_data.max != "" and splitted[1].strip() != "":
                        blood_dict[int(splitted[0])] = (float(splitted[1]), (
                        float(blood_data.min), float(blood_data.max), float(blood_data.extended_range)))
                    else:
                        break
            f.close()

        allergy_dict = {}
        if user_algo.allergy_results != None:
            f = open(os.path.join(app.config['UPLOAD_FOLDER'], user_algo.allergy_results))
            for line in f:
                splitted = line.strip().split("\t")
                allergy_data = panels.AllergyAlgorithmInfo.query.filter(
                    panels.AllergyAlgorithmInfo.trait_id == int(splitted[0])).all()
                if len(allergy_data) > 0:
                    allergy_data = allergy_data[0]
                    if allergy_data.min != "" and allergy_data.max != "" and splitted[1].strip() != "":
                        allergy_dict[int(splitted[0])] = (float(splitted[1]), (float(allergy_data.min), float(allergy_data.max)))
                    else:
                        break
            f.close()
        html = render_template('genetics_pdf.html', blood_data = blood_dict, allergy_data = allergy_dict, os_path=os_path, categories=categories,
                               all_traits=all_traits, algorithm_info=algorithm_info, user=user, patient_panel=user_algo)
        options = {
            'page-size': 'A4',
            'margin-top': '0in',
            'margin-right': '0in',
            'margin-bottom': '0in',
            'margin-left': '0in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        pdf = pdfkit.from_string(html, os.path.join(app.config['UPLOAD_FOLDER'], "analysis_data",
                                                    start_name+user.f_name + user.l_name + ".pdf"), options=options)

@csrf.exempt
@app.route('/submit_analysis_data', methods = ['POST'])
def submit_analysis_data():
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        if request.form.get("analysis_result",None) != None:
            ref_id = request.form['ref_id']
            update_patient_panels = patients.Patient_panels.query.get((int(ref_id), request.form['patient_id'], request.form['panel_id']))# patients.Patient_panels.query.get(int(ref_id))

            files_dict = {'dna_results': request.files['dna_result'] , 'blood_results':request.files['blood_result'], 'allergy_results':request.files['allergy_result']}
            flag = 0
            for name, file in files_dict.items():
                if file and allowed_file(file.filename):
                    last_index = len(file.filename) - 1 - file.filename[::-1].index('.')
                    filename = os.path.join("analysis_data", secure_filename(ref_id+"_"+name+file.filename[last_index:]))
                    # filtering ata depends on rsid of panel starts here

                    if name == "dna_results":
                        rs_ids = {data.rs_id.lower() for data in panels.TraitAlgorithmInfo.query.all()}
                        file1 = [line.strip().split("\t") for line in file.read().decode("utf-8").split("\n") if not line.startswith("#") and len(line.strip().split("\t"))>3 and line.strip().split("\t")[0].lower() in rs_ids]
                        file1.insert(0,['rs_id',"chromosome","position","genotype"])
                        f= open(os.path.join(app.config['UPLOAD_FOLDER'],filename), "w")
                        for line in file1:
                            print("\t".join(line), file=f)
                        f.close()
                        setattr(update_patient_panels, name, filename)
                    elif name == "blood_results":
                        file1 = file.read().decode("utf-8")
                        print(file1.strip().split("\n")[0].split("\t"))
                        if len(file1.strip().split("\n")[0].split("\t")) > 1:
                            f = open(os.path.join(app.config['UPLOAD_FOLDER'],filename), "w")
                            print(file1, file=f)
                            f.close()
                            setattr(update_patient_panels, name, filename)
                        else:
                            flag = 1
                    else:
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
                        setattr(update_patient_panels, name, filename)
                    # filtering ata depends on rsid of panel ends here

            setattr(update_patient_panels, 'submitted_date' , datetime.datetime.now())
            setattr(update_patient_panels, 'result_status', 'Done')
            setattr(update_patient_panels, 'technician_status', '')
            db.session.commit()
            # PDF Generation

            user = patients.Patients.query.get(request.form['patient_id'])
            user_algo = patients.Patient_panels.query.get(
                (int(ref_id), request.form['patient_id'], request.form['panel_id']))

            print(user_algo.dna_results)
            if user_algo.dna_results != None:
                pdf_genration_genetics(user, user_algo,"1_")
                setattr(user_algo, 'first_result', os.path.join("analysis_data","1_"+user.f_name+user.l_name+".pdf"))
                db.session.commit()
                if flag == 1:
                    flash("Please check format of file before upload".title(), "error")
                else:
                    flash("Files Uploaded Successfully and Report is generated".title(), "info")
            else:
                flash("Files Uploaded Successfully and Report is not generated".title(), "info")
        return redirect("/analysis_view")
    else:
        return redirect("/bad_request")

@app.route('/download_analysis_data/<path:filename>')
def download_analysis_data(filename):
    #return redirect("/analysis_view")
    return send_from_directory(directory=os.path.join("/".join(app.root_path.split("/")[:-1]), app.config['UPLOAD_FOLDER'], "/".join(filename.split("/")[:-1])), filename=filename.split("/")[-1])

@app.route('/delete_analysis_data_file/<int:id>-<int:patient_id>-<int:panel_id>-<name>')
def delete_analysis_data_file(id, patient_id, panel_id, name):
    update_patient_panels = patients.Patient_panels.query.get((id, patient_id, panel_id))
    if os.path.exists(os.path.join("/".join(app.root_path.split("/")[:-1]), app.config['UPLOAD_FOLDER'],
                                   getattr(update_patient_panels,name))):
        os.remove(os.path.join("/".join(app.root_path.split("/")[:-1]), app.config['UPLOAD_FOLDER'],
                               getattr(update_patient_panels,name)))


    setattr(update_patient_panels , name, None)
    if name == "dna_results":

        if getattr(update_patient_panels, "first_result") != None:
            if os.path.exists(os.path.join("/".join(app.root_path.split("/")[:-1]), app.config['UPLOAD_FOLDER'],
                                           getattr(update_patient_panels, "first_result"))):
                os.remove(os.path.join("/".join(app.root_path.split("/")[:-1]), app.config['UPLOAD_FOLDER'],
                                       getattr(update_patient_panels, "first_result")))
        if getattr(update_patient_panels, "second_result") != None:
            if os.path.exists(os.path.join("/".join(app.root_path.split("/")[:-1]), app.config['UPLOAD_FOLDER'],
                                           getattr(update_patient_panels, "second_result"))):
                os.remove(os.path.join("/".join(app.root_path.split("/")[:-1]), app.config['UPLOAD_FOLDER'],
                                       getattr(update_patient_panels, "second_result")))

        setattr(update_patient_panels, "first_result", None)
        setattr(update_patient_panels, "second_result", None)
        setattr(update_patient_panels, "second_result", None)
        setattr(update_patient_panels, "second_result", None)
        setattr(update_patient_panels, "submitted_date", None)
        setattr(update_patient_panels, "technician_status_date", None)
        setattr(update_patient_panels, "physician_status_date", None)
        setattr(update_patient_panels, "physician_note", None)
        setattr(update_patient_panels, "result_status", "Pending")
        setattr(update_patient_panels, "technician_status", "Pending")
        setattr(update_patient_panels, "physician_status", None)
    db.session.commit()
    return redirect("/analysis_view")

@csrf.exempt
@app.route('/submitReport', methods=['POST'])
def submitReport():
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        all_data = {data.split(":")[0]:data.split(":")[1] for data in request.form["data"].split(",")}
        id = all_data.get('id')
        patient_id = all_data.get('patient_id')
        panel_id = all_data.get('panel_id')
        report_type = all_data.get('report_type')

        file_name = ""
        if report_type == "Blood":
            file_name = os.path.join("analysis_data",id+"_blood_results.csv")
        elif report_type == "Allergy":

            file_name = os.path.join("analysis_data",id+"_allergy_results.csv")

        if file_name != "":
            #print(report_type,os.path.join(app.config['UPLOAD_FOLDER'],file_name))
            fw = open(os.path.join(app.config['UPLOAD_FOLDER'],file_name), "w")
            for k, v in all_data.items():
                if k != "csrf_token" and k != "id" and k != "patient_id" and k != 'panel_id' and k != 'report_type':
                    print(k+"\t"+v+"\t"+panels.Traits.query.get(k).name, file= fw)
            fw.close()
            update_patient_panels = patients.Patient_panels.query.get((id, patient_id, panel_id))

            if report_type == "Blood":
                setattr(update_patient_panels, 'blood_results',file_name)
            elif report_type == "Allergy":
                setattr(update_patient_panels, 'allergy_results', file_name)
            setattr(update_patient_panels, 'submitted_date', datetime.datetime.now())
            db.session.commit()
        return jsonify(1) #redirect("/analysis_view")
    else:
        return redirect("/bad_request")

# For download report data format
# report type is used for to understanding which format we want to download
@app.route('/report_format_download_<report_type>', methods=['GET'])
def report_format_download(report_type):
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        if report_type == "blood":
            # Take out data which has blood report data
            all_data = db.session.query(panels.Traits , panels.BloodAlgorithmInfo).filter(panels.BloodAlgorithmInfo.trait_id == panels.Traits.id).all()
            # res list is used to store all data one by one in expected format so that we can put it to file
            res_list = []
            for trait_data, blood_algo_data in all_data:
                res_list.append(str(trait_data.id)+"\t\t"+str(trait_data.name))
            res = "\n".join(res_list)
            return Response(
                res,
                mimetype="text/csv",
                headers={"Content-disposition":
                             "attachment; filename="+report_type+".csv"})
            #return redirect("/analysis_view")
        else:
            return redirect("/analysis_view")
    else:
        return redirect("/bad_request")
# For Ajax
@csrf.exempt
@app.route('/getReportFields', methods=['POST'])
def getReportFields():
    if "login_id" in session and (session.get("role") == "Admin" or session.get("role") == "Technician"):
        get_patient_panels = patients.Patient_panels.query.get((request.form['id'], request.form['patient_id'], request.form['panel_id']))
        patient_panel_schema = patients.Patient_panelsSchema()
        op = patient_panel_schema.dumps(get_patient_panels)
        d = json.loads(op)
        if (request.form['report_type']=="Blood"):
            traits = db.session.query(panels.Traits , panels.BloodAlgorithmInfo).filter(panels.BloodAlgorithmInfo.trait_id == panels.Traits.id ).all()
        else:
            traits = db.session.query(panels.Traits, panels.AllergyAlgorithmInfo).filter(
                panels.AllergyAlgorithmInfo.trait_id == panels.Traits.id).all()
        report_list = []
        for traits , report in traits:
            data_dict = {}
            data_dict["id"] = traits.id
            data_dict["name"] = traits.name
            data_dict["min"] = report.min
            data_dict["max"] = report.max
            report_list.append(data_dict)
        d['formData'] = report_list

        """
        with open(os.path.join(app.config['UPLOAD_FOLDER'],"report_form_fields/"+request.form['report_type']+".txt")) as json_file:
            data = json.load(json_file)
            print(data)
            d['formData'] = data['formData']
            """
        #print(type(d),d)
        return json.dumps(d)
    else:
        return redirect("/bad_request")

