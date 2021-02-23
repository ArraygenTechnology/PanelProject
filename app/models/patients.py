from .. import db , datetime , ma
from . import panels

class Patients(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    date = db.Column(db.DateTime, nullable = False, default=datetime.datetime.now())
    patient_id = db.Column(db.String(20), nullable=False)
    f_name = db.Column(db.String(64), nullable=False)
    l_name = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    ethnicity = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    contact_no = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text(), nullable=False)
    order_by = db.Column(db.String(20), nullable=False)
    collection_date = db.Column(db.String(20), nullable=False)
    received_date = db.Column(db.String(20), nullable=False)
    report_generated = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    bmi = db.Column(db.Integer, nullable=False)
    allergic_to = db.Column(db.String(255), nullable=True)
    additional1 = db.Column(db.String(255), nullable=True)
    additional2 = db.Column(db.String(255), nullable=True)
    additional3 = db.Column(db.String(255), nullable=True)
    remark = db.Column(db.Text(), nullable=True)
    panels = db.relationship(panels.Panels, secondary='patient_panels')


class Patient_panels(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    patient_id = db.Column(
      db.Integer,
      db.ForeignKey('patients.id'),
      primary_key = True)

    panel_id = db.Column(
       db.Integer,
       db.ForeignKey('panels.id'),
       primary_key = True)

    dna_results = db.Column(db.String(255), nullable= True)
    blood_results = db.Column(db.String(255), nullable= True)
    allergy_results = db.Column(db.String(255), nullable= True)
    submitted_date = db.Column(db.DateTime, default="")
    first_result = db.Column(db.String(255), nullable=True)
    result_status = db.Column(db.String(255), nullable= False, default="Pending")
    technician_status = db.Column(db.String(255), nullable= True)
    technician_status_date = db.Column(db.DateTime, default="")
    physician_note = db.Column(db.Text(), nullable=True)
    include_note = db.Column(db.String(255), nullable= True)
    physician_status = db.Column(db.String(255), nullable= True)
    physician_status_date = db.Column(db.DateTime, default="")
    second_result = db.Column(db.String(255), nullable=True)
    send = db.Column(db.String(255), nullable=True)
    send_date = db.Column(db.DateTime,  default="")
    print_and_issue = db.Column(db.String(255), nullable=True)
    print_and_issue_date = db.Column(db.DateTime,  default="")
    panel = db.relationship("Panels")
    patient = db.relationship("Patients")

class PatientsSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Patients
        fields = ('id' , 'date' , 'patient_id' , 'f_name' , 'l_name' , 'gender' , 'ethnicity' , 'dob' ,
                  'contact_no' , 'email' , 'password' , 'address' , 'order_by' , 'collection_date' , 'received_date' ,
                  'report_generated' , 'age' , 'weight' , 'height' , 'bmi' , 'allergic_to' , 'additional1' , 'additional2' ,
                  'additional3' , 'remark' , 'panels')
    panels = ma.Nested(panels.PanelSchema, many = True)

class Patient_panelsSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Patient_panels
        fields = ('id', 'patient_id', 'panel_id', 'dna_results', 'blood_results',
                  'allergy_results', 'submitted_date', 'first_result', 'result_status',
                  'technician_status', 'technician_status_date', 'physician_note', 'include_note',
                  'physician_status', 'physician_status_date', 'second_result', 'send', 'send_date',
                  'print_and_issue', 'print_and_issue_date' , 'panel', 'patient')
        include_fk = True
        relationship= True
    panel = ma.Nested(panels.PanelSchema)
    patient = ma.Nested(PatientsSchema)


    
