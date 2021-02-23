from .. import db

class Users(db.Model):
    id =  db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True )
    f_name = db.Column(db.String(64),nullable = False)
    l_name = db.Column(db.String(64),nullable = False)
    gender = db.Column(db.String(20),nullable = False)
    dob = db.Column(db.String(20),nullable = False)
    email = db.Column(db.String(255),nullable = False, unique=True)
    contact_no = db.Column(db.String(50),nullable = False)
    password = db.Column(db.String(20), nullable=False)
    address =db.Column(db.Text(),nullable = False)
    role =db.Column(db.String(20),nullable = False)

    def __init__(self,f_name,l_name,gender,dob,email,contact_no,password,address,role):
        self.f_name = f_name
        self.l_name = l_name
        self.gender = gender
        self.dob = dob
        self.email = email
        self.contact_no = contact_no
        self.password = password
        self.address = address
        self.role = role

