from . import *
from .models import panels

@app.route('/panel_category_<id>', defaults={'category_id':0, 'trait_id':0}, methods = ['GET', 'POST'])
@app.route('/panel_category_<id>_<category_id>', defaults={'trait_id':0}, methods = ['GET', 'POST'])
@app.route('/panel_category_trait_<id>_<category_id>_<trait_id>')
def panel_category(id, category_id, trait_id):
    if "login_id" in session and session.get("role") == "Admin" :
        panel_info = panels.Panels.query.get(id)
        categories = panels.Category.query.filter(panels.Category.panel_id ==id).order_by(panels.Category.rank.asc())
        if category_id == 0 and trait_id == 0:
            return render_template('panel_category.html', panel_info=panel_info, categories=categories)
        elif category_id != 0  and trait_id==0:
            category = panels.Category.query.get(category_id)
            return render_template('panel_category.html', panel_info = panel_info, categories = categories, category= category)
        elif category_id != 0  and trait_id != 0:
            trait = panels.Traits.query.get(trait_id)
            return render_template('panel_category.html', panel_info=panel_info, categories=categories,
                                   trait=trait)
    else:
        return redirect("/bad_request")

# Add or Update Users
@csrf.exempt
@app.route('/category_add_update', defaults={'id':0}, methods = ['GET', 'POST'])
@app.route('/category_add_update_<int:id>', methods = ['GET', 'POST'])
def category_add_update(id):
    if "login_id" in session and session.get("role") == "Admin":
        if request.method == 'POST':
            data = request.form

            all_data = data.to_dict()
            del all_data['csrf_token']
            # update patient information
            if id != 0:
                category = panels.Category.query.get(id)
                #print(category)
                for attr_name, new_value in all_data.items():
                    setattr(category, attr_name, new_value)

                db.session.commit()
                flash("Category Updated Successfully".title(), "info")
            else:
            # add new category details
                # creating object
                category = panels.Category(**all_data)
                db.session.add(category)
                db.session.commit()
                flash("Category Added Successfully".title(), "info")

            return redirect('/panel_category_'+all_data['panel_id'])
        else:
            return redirect("/bad_request")
    else:
        return redirect("/bad_request")

@app.route('/category_delete_<panel_id>/<id>')
def category_delete(panel_id, id):
    if "login_id" in session and session.get("role") == "Admin":
        category = panels.Category.query.get(id)
        if category != None:
            db.session.delete(category)
            db.session.commit()
            flash("Category Deleted Successfully".title(), "info")
        return redirect('/panel_category_'+str(panel_id))
    else:
        return redirect("/bad_request")

@app.route('/view_traits_<panel_id>')
def view_traits(panel_id):
    if "login_id" in session and session.get("role") == "Admin" :
        traits = db.session.query (panels.Traits, panels.Category).filter(panels.Category.panel_id == panel_id,panels.Traits.category_id == panels.Category.id) #panels.Traits.query.all()
        #print(traits)
        traits = traits.all()
        #print(traits)
        return render_template('view_traits.html', traits = traits)
    else:
        return redirect("/bad_request")


# Add or Update Trait
@csrf.exempt
@app.route('/trait_add_update', defaults={'id':0}, methods = ['GET', 'POST'])
@app.route('/trait_add_update_<int:id>', methods = ['GET', 'POST'])
def trait_add_update(id):
    if "login_id" in session and session.get("role") == "Admin":
        if request.method == 'POST':
            data = request.form
            all_data = data.to_dict()

            del all_data['csrf_token']
            del all_data['panel_id']
            # update patient information
            if id != 0:
                traits = panels.Traits.query.get(id)

                if request.files != "":
                    print(traits.icon_img , request.files['icon_img'].filename)
                    if request.files['icon_img'].filename != "":
                        print(traits.icon_img, request.files['icon_img'].filename)
                        if request.files['icon_img'].filename not in traits.icon_img:
                            print(traits.icon_img, request.files['icon_img'].filename)
                            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], traits.icon_img)):
                                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], traits.icon_img))

                            file = request.files['icon_img']

                            if file.filename != "":
                                last_index = len(file.filename) - 1 - file.filename[::-1].index('.')
                                filename = os.path.join("trait_images",
                                                        secure_filename(all_data['name'].replace("_", "") + file.filename[last_index:]))
                                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                                all_data['icon_img'] = filename

                for attr_name, new_value in all_data.items():
                    setattr(traits, attr_name, new_value)

                db.session.commit()
                flash("Trait Updated Successfully".title(), "info")
            else:
                # add new category details
                # creating object
                if request.files != None:
                    file = request.files['icon_img']
                    last_index = len(file.filename) - 1 - file.filename[::-1].index('.')
                    filename = os.path.join("trait_images",
                                            secure_filename(all_data['name'].replace("_", "") + file.filename[last_index:]))
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    all_data['icon_img'] = filename

                traits = panels.Traits(**all_data)
                db.session.add(traits)
                db.session.commit()
                flash("Trait Added Successfully".title(), "info")

            return redirect('/panel_category_'+data['panel_id'])
        else:
            return redirect("/bad_request")
    else:
        return redirect("/bad_request")

@app.route('/trait_delete/<panel_id>-<id>')
def trait_delete(panel_id,id):
    if "login_id" in session and session.get("role") == "Admin" :
        delete_trait = panels.Traits.query.get(id)
        if delete_trait.icon_img != None:
            os.remove(
                os.path.join("/".join(app.root_path.split("/")[:-1]), app.config['UPLOAD_FOLDER'], delete_trait.icon_img))
        db.session.delete(delete_trait)
        db.session.commit()
        flash("Trait Deleted Successfully".title(), "info")
        return redirect('/view_traits_'+str(panel_id))
    else:
        return redirect("/bad_request")

# For Ajax

# To see About, Dietary Source and What to Do in one modal
@csrf.exempt
@app.route('/getTraits', methods=['POST'])
def getTraits():
    if "login_id" in session and session.get("role") == "Admin" :
        trait = panels.Traits.query.get(request.form['id'])
        trait_schema = panels.TraitsSchema()
        op = trait_schema.dumps(trait)
        d = json.loads(op)
        return json.dumps(d)
    else:
        return redirect("/bad_request")


# Display (TraitAlgorithmInfo)
def getDBTraitAlgorithmInfo(id):
    traitAlgorithmInfo = panels.TraitAlgorithmInfo.query.filter(
        panels.TraitAlgorithmInfo.trait_id == id).all()
    traitAlgorithmInfo_schema = panels.TraitAlgorithmInfoSchema()
    return [traitAlgorithmInfo_schema.dumps(x) for x in traitAlgorithmInfo]

@csrf.exempt
@app.route('/getTraitAlgorithmInfo', methods=['POST'])
def getTraitAlgorithmInfo():
    if "login_id" in session and session.get("role") == "Admin" :
        op = getDBTraitAlgorithmInfo(request.form['id'])
        return jsonify(op)
    else:
        return redirect("/bad_request")

# Display Signle for Edit (TraitAlgorithmInfo)
@csrf.exempt
@app.route('/getSingleTraitAlgorithmInfo', methods=['POST','GET'])
def getSingleTraitAlgorithmInfo():
    if "login_id" in session and session.get("role") == "Admin" :
        trait_gene = panels.TraitAlgorithmInfo.query.get(request.form['id'])
        trait_gene_schema = panels.TraitAlgorithmInfoSchema()
        op = trait_gene_schema.dumps(trait_gene)
        d = json.loads(op)
        return json.dumps(d)
    else:
        return redirect("/bad_request")

# To add or update gene trait (TraitAlgorithmInfo)
@csrf.exempt
@app.route('/trait_gene_add_update', methods=['POST'])
def trait_gene_add_update():
    if "login_id" in session and session.get("role") == "Admin":
        if request.method == 'POST':
            data = request.form
            print(data)
            all_data = data.to_dict()
            id = all_data['gene_id']
            del all_data['csrf_token']
            del all_data['gene_id']

            print(all_data, type(all_data))
            # update patient information
            res = ""
            if int(id) != 0:
                category = panels.TraitAlgorithmInfo.query.get(id)
                for attr_name, new_value in all_data.items():
                    setattr(category, attr_name, new_value)

                db.session.commit()
            else:
                gene = panels.TraitAlgorithmInfo(**all_data)
                db.session.add(gene)
                db.session.commit()

            op = getDBTraitAlgorithmInfo(all_data['trait_id'])
            return jsonify(op)
        else:
            return redirect("/bad_request")
    else:
        return redirect("/bad_request")

# Delete (TraitAlgorithmInfo)
@csrf.exempt
@app.route('/deleteTraitAlgorithmInfo', methods=['POST'])
def deleteTraitAlgorithmInfo():
    if "login_id" in session and session.get("role") == "Admin" :
        delete_TraitAlgorithmInfo = panels.TraitAlgorithmInfo.query.get(request.form['id'])
        trait_id = delete_TraitAlgorithmInfo.trait_id
        db.session.delete(delete_TraitAlgorithmInfo)
        db.session.commit()
        op = getDBTraitAlgorithmInfo(trait_id)
        return jsonify(op)
    else:
        return redirect("/bad_request")


# To add or update (BloodAlgorithmInfo)
@csrf.exempt
@app.route('/blood_details_add_update', methods=['POST'])
def blood_details_add_update():
    if "login_id" in session and session.get("role") == "Admin":
        if request.method == 'POST':
            data = request.form

            all_data = data.to_dict()
            id = all_data['id']
            del all_data['csrf_token']
            del all_data['id']
            # update patient information

            res = ""
            if int(id) != 0:
                bloodAlgorithmInfo = panels.BloodAlgorithmInfo.query.get(id)
                for attr_name, new_value in all_data.items():
                    setattr(bloodAlgorithmInfo, attr_name, new_value)
                db.session.commit()
            else:
                blood = panels.BloodAlgorithmInfo(**all_data)
                db.session.add(blood)
                db.session.commit()

            op = getDBTraitAlgorithmInfo(all_data['trait_id'])
            return jsonify(op)
        else:
            return redirect("/bad_request")
    else:
        return redirect("/bad_request")


@csrf.exempt
@app.route('/getBloodDetails', methods=['POST'])
def getBloodDetails():
    if "login_id" in session and session.get("role") == "Admin":
        blood_data = panels.BloodAlgorithmInfo.query.filter(panels.BloodAlgorithmInfo.trait_id==request.form['id']).all()
        if len(blood_data) == 0:
            res = '{"id":0}'
        else:
            bloodAlgorithmInfoSchema = panels.BloodAlgorithmInfoSchema()
            res = bloodAlgorithmInfoSchema.dumps(blood_data[0])
        return jsonify(res)
    else:
        return redirect("/bad_request")


@csrf.exempt
@app.route('/allergy_details_add_update', methods=['POST'])
def allergy_details_add_update():
    if "login_id" in session and session.get("role") == "Admin":
        if request.method == 'POST':
            data = request.form
            #print(request.remote_addr)
            all_data = data.to_dict()
            id = all_data['id']
            del all_data['csrf_token']
            del all_data['id']
            # update patient information

            res = ""
            if int(id) != 0:
                allergyAlgorithmInfo = panels.AllergyAlgorithmInfo.query.get(id)
                for attr_name, new_value in all_data.items():
                    setattr(allergyAlgorithmInfo, attr_name, new_value)
                db.session.commit()
            else:
                blood = panels.AllergyAlgorithmInfo(**all_data)
                db.session.add(blood)
                db.session.commit()

            op = getDBTraitAlgorithmInfo(all_data['trait_id'])
            return jsonify(op)
        else:
            return redirect("/bad_request")
    else:
        return redirect("/bad_request")


@csrf.exempt
@app.route('/getAllergyDetails', methods=['POST'])
def getAllergyDetails():
    if "login_id" in session and session.get("role") == "Admin":
        allergy_data = panels.AllergyAlgorithmInfo.query.filter(panels.AllergyAlgorithmInfo.trait_id==request.form['id']).all()
        if len(allergy_data) == 0:
            res = '{"id":0}'
        else:
            allergyAlgorithmInfoSchema = panels.AllergyAlgorithmInfoSchema()
            res = allergyAlgorithmInfoSchema.dumps(allergy_data[0])
        return jsonify(res)
    else:
        return redirect("/bad_request")