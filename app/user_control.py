from . import *
from .models import patients, panels

@app.route('/user_index', defaults={'panel_id': 0 , 'category_id':0}, methods =['GET'])
@app.route('/user_index_<panel_id>', defaults={'category_id':0}, methods =['GET'])
@app.route('/user_index_<panel_id>_<category_id>', methods =['GET'])
def user_index(panel_id, category_id):
    if "login_id" in session and session.get("role") == "User":
        user = patients.Patients.query.get(session['login_id'])

        if panel_id == 0 and category_id == 0:
            categories = panels.Category.query.filter(panels.Category.panel_id==user.panels[0].id).all()
            traits = panels.Traits.query.filter(panels.Traits.category_id==categories[0].id).all()
            category_id = categories[0].id
            panel_id = user.panels[0].id

        elif category_id == 0:
            categories = panels.Category.query.filter(panels.Category.panel_id == panel_id).all()
            traits = panels.Traits.query.filter(panels.Traits.category_id == categories[0].id).all()
            category_id = categories[0].id

        else:
            categories = panels.Category.query.filter(panels.Category.panel_id == panel_id).all()
            traits = panels.Traits.query.filter(panels.Traits.category_id == category_id).all()

        user_algo = patients.Patient_panels.query.filter(patients.Patient_panels.panel_id==panel_id,patients.Patient_panels.patient_id==session['login_id']).first()
        f = open(os.path.join(app.config['UPLOAD_FOLDER'], user_algo.dna_results))
        user_rs_id_dict = {}
        for line in f:
            splitted = line.strip().split("\t")
            user_rs_id_dict[splitted[0]] = splitted[-1]
        f.close()

        algorithm_info = []
        for trait in traits:
            algo_list = []
            algo = panels.TraitAlgorithmInfo.query.filter(panels.TraitAlgorithmInfo.trait_id == trait.id).all()
            for data in algo:
                if data.rs_id in user_rs_id_dict.keys():
                    user_genotype = user_rs_id_dict[data.rs_id]
                    if user_genotype == data.genotype:
                        algo_list.append(data)
            algorithm_info.append(algo_list)

        f = open(os.path.join(app.config['UPLOAD_FOLDER'], user_algo.blood_results))
        blood_dict = {}
        for line in f:
            splitted = line.strip().split("\t")
            blood_data = panels.BloodAlgorithmInfo.query.filter(panels.BloodAlgorithmInfo.trait_id == splitted[0]).all()
            if len(blood_data) > 0:
                blood_data = blood_data[0]
                if blood_data.typical_min.isnumeric() and blood_data.typical_max.isnumeric() and blood_data.slightly_enhanced_min.isnumeric() and blood_data.slightly_enhanced_max.isnumeric() and blood_data.enhanced_min.isnumeric() and blood_data.enhanced_max.isnumeric():
                    blood_dict[int(splitted[0])] = (int(splitted[1]),(int(blood_data.typical_min), int(blood_data.typical_max), int(blood_data.slightly_enhanced_min) , int(blood_data.slightly_enhanced_max) , int(blood_data.enhanced_min) , int(blood_data.enhanced_max)))
        f.close()
        print(blood_dict)
        return render_template('patient_user/index.html', user= user, categories=categories, traits= traits , category_id = category_id , panel_id =panel_id, algorithm_info=algorithm_info, blood_data = blood_dict)
    else:
        return redirect("/bad_request")

@app.route("/user_trait_view_<category_id>_<trait_id>", methods = ['GET'])
def user_trait_view(category_id,trait_id):
    if "login_id" in session and session.get("role") == "User":
        category = panels.Category.query.get(category_id)
        trait = panels.Traits.query.get(trait_id)

        user_algo = patients.Patient_panels.query.filter(patients.Patient_panels.panel_id == category.panel_id,
                                                         patients.Patient_panels.patient_id == session['login_id']).first()
        f = open(os.path.join(app.config['UPLOAD_FOLDER'], user_algo.dna_results))
        user_rs_id_dict = {}
        for line in f:
            splitted = line.strip().split("\t")
            user_rs_id_dict[splitted[0]] = splitted[-1]

        algo_list = []
        algo = panels.TraitAlgorithmInfo.query.filter(panels.TraitAlgorithmInfo.trait_id == trait.id).all()
        for data in algo:
            if data.rs_id in user_rs_id_dict.keys():
                user_genotype = user_rs_id_dict[data.rs_id]
                if user_genotype == data.genotype:
                    algo_list.append(data)

        return render_template('patient_user/view_user_trait.html', category= category, trait = trait, algorithm_info = algo_list)
    else:
        return redirect("/bad_request")

# Login
@csrf.exempt
@app.route("/user_login", methods = ['POST'])
def user_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = patients.Patients.query.filter(patients.Patients.email == email).first()
        if user != None:
            user = patients.Patients.query.filter(patients.Patients.email == email, patients.Patients.password == password).first()
            if user != None:
                session['login_id'] = user.id
                session['role'] = "User"
                session['l_name'] = user.l_name
                session['f_name'] = user.f_name
                panel_schema = panels.PanelSchema()
                session['user_panel'] = [json.loads(panel_schema.dumps(panels_obj_)) for panels_obj_ in user.panels]
                #flash("Logged in Successfully".title(), "info")
                return redirect("/user_index")
            else:
                flash("Email Or Password Is Wrong".title(), "error")
        else:
            flash("Email Is Not Registered".title(), "error")
    else:
        flash("Bad Request 404".title(),"error")
    return redirect("/")

# Logout
@app.route("/user_logout")
def user_logout():
    session.pop('login_id',None)
    session.pop('f_name',None)
    session.pop('l_name',None)
    session.pop('role',None)
    flash("Logged out successfully".title(), "info")
    return redirect("/")
