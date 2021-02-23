from . import *
from .models import sys_users, patients, panels

# Login
@csrf.exempt
@app.route("/sys_user_login", methods = ['POST'])
def sys_user_login():
    if request.method == 'POST' :
        email = request.form.get('email')
        password = request.form.get('password')
        user = sys_users.Users.query.filter(sys_users.Users.email == email).first()
        if user != None:
            user = sys_users.Users.query.filter(sys_users.Users.email == email, sys_users.Users.password == password).first()
            if user != None:

                session['login_id'] = user.email
                session['role'] = user.role
                session['l_name'] = user.l_name
                session['f_name'] = user.f_name
                session['gender'] = user.gender
                panels_obj = panels.Panels.query.order_by(panels.Panels.id).all()
                panel_schema = panels.PanelSchema()
                op = [json.loads(panel_schema.dumps(panels_obj_))for panels_obj_ in panels_obj]
                session['sidebar_panel'] = op

                print(panels_obj, op, panel_schema)

                flash("Logged in Successfully".title(), "info")
                return redirect("/dashboard")
            else:
                flash("Email Or Password Is Wrong".title(), "error")
        else:
            flash("Email Is Not Registered".title(), "error")
    else:
        flash("Bad Request 404".title(),"error")
    return redirect("/")

# Logout
@app.route("/sys_user_logout")
def sys_user_logout():
    session.pop('login_id',None)
    user_type = session.pop('role',None)
    session.pop('l_name',None)
    session.pop('f_name',None)
    session.pop('gender',None)
    session.pop('sidebar_panel',None)
    flash("Logged out successfully".title(), "info")
    return redirect("/"+user_type)

# Add or Update Users
@csrf.exempt
@app.route('/sys_users_add_update', defaults={'id':0}, methods = ['GET', 'POST'])
@app.route('/sys_users_add_update/<int:id>', methods = ['GET', 'POST'])
def sys_users_add_update(id):
    if request.method == 'POST':
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        gender = request.form['gender']
        dob = request.form['dob']
        email = request.form['email']
        contact_no = request.form['contact_no']
        password = request.form['password']
        address = request.form['address']
        role = request.form['role']
        if id != 0:
            update_user = sys_users.Users.query.get(id)
            update_user.f_name = f_name
            update_user.l_name = l_name
            update_user.gender = gender
            update_user.dob = dob
            update_user.contact_no = contact_no
            update_user.password = password
            update_user.address= address
            update_user.role = role
            exists = sys_users.Users.query.filter_by(email=email).first()
            if exists == None :
                update_user.email = email
            elif exists.id == id:
                pass
            else:
                flash("Email id not updated becuase it's email already exists".title(), "warning")
            db.session.commit()
            flash("User Information Updated Successfully".title(), "info")
        else:
            exists = sys_users.Users.query.filter_by(email=email).first()
            if exists == None:
                user = sys_users.Users(f_name, l_name, gender, dob, email, contact_no, password, address, role)
                db.session.add(user)
                db.session.commit()
                flash("User Added Successfully".title(),"info")
            else:
                flash("User Already Exists".title(), "error")
    return redirect('/sys_users_view')


@app.route('/sys_user/', defaults={'id': 0})
@app.route('/sys_user/<id>')
def sys_user(id):
    if "login_id" in session and session.get("role") == "Admin" :
        if id == 0:
            return render_template('sys_users.html')
        else:
            exists = sys_users.Users.query.get(id)
            if exists == None:
                return redirect("/bad_request")
            else:
                return render_template('sys_users.html', user = exists)
    else:
        return redirect("/bad_request")

@app.route('/sys_users_view')
def sys_users_view():
    if "login_id" in session and session.get("role") == "Admin":
        users = sys_users.Users.query.all()
        return render_template('sys_users_view.html', Users= users)
    else:
        return redirect("/bad_request")

@app.route('/sys_users_delete/<id>')
def sys_users_delete(id):
    if "login_id" in session and session.get("role") == "Admin":
        delete_user = sys_users.Users.query.get(id)
        db.session.delete(delete_user)
        db.session.commit()
        flash("User Deleted Successfully".title(), "info")
        return redirect("/sys_users_view")
    else:
        return redirect("/bad_request")

