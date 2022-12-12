import datetime
import random

from bson import ObjectId
from flask import Flask, request, render_template, session, redirect
import pymongo
from Mail import send_email
my_collections = pymongo.MongoClient("mongodb://localhost:27017/")
my_db = my_collections['BloodBank']
Doctor_col = my_db['Doctor']
BloodBank_col = my_db['BloodBank']
donor_col = my_db['donor']
schedule_col = my_db['schedule']
campaign_col = my_db['campaign']
stock_col = my_db['stock']
DoctorRequest_col = my_db['Doctor_Request']

app = Flask(__name__)
app.secret_key = "abcdefg"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/alogin")
def alogin():
    return render_template("alogin.html")


@app.route("/alogin1", methods=['post'])
def alogin1():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'admin' and password == 'admin':
        session['role'] = 'Admin'
        return render_template("ahome.html")
    else:
        return render_template("msg.html", message="Invalid Login Details", color="bg-danger text-white")


@app.route("/dlogin")
def dlogin():
    return render_template("dlogin.html")


@app.route("/dlogin1", methods=['post'])
def dlogin1():
    email = request.form.get('email')
    password = request.form.get('password')
    query = {"email": email, "password": password}
    count = Doctor_col.count_documents(query)
    if count > 0:
        doctor = Doctor_col.find_one(query)
        if doctor["status"] == "Authorised":
            session['doctor_id'] = str(doctor['_id'])
            session['role'] = 'Doctor'
            return render_template("dhome.html")
        else:
            return render_template("msg.html", message="Doctor is Unauthorized", color="bg-danger text-white")
    else:
        return render_template("msg.html", message="Invalid Login Details", color="bg-danger text-white")


@app.route("/docRegister")
def docRegister():
    return render_template("docRegister.html")


@app.route("/docRegister1", methods=['post'])
def docRegister1():
    name = request.form.get('name')
    phoneno = request.form.get('phoneno')
    email = request.form.get('email')
    password = request.form.get('password')
    specialization = request.form.get('specialization')
    qualification = request.form.get('qualification')
    hospitalName = request.form.get('hospitalName')
    query = {"$or": [{"email": email}, {"phoneno": phoneno}]}
    count = Doctor_col.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Details", color="bg-danger text-white")
    else:
        query = {"name": name, "phoneno": phoneno, "email": email, "password": password, "specialization": specialization, "qualification": qualification, "hospitalName": hospitalName, "status": "Unauthorized"}
        Doctor_col.insert_one(query)
        return render_template("msg.html", message="Doctor Register Successfully", color="bg-success text-white")


@app.route("/ViewBloodBank")
def ViewBloodBank():
    bloodBanks = BloodBank_col.find()
    return render_template("ViewDoctorBloodBank.html", bloodBanks=bloodBanks)


@app.route("/doctorRequest")
def doctorRequest():
    bloodbank_id = ObjectId(request.args.get('bloodbank_id'))
    return render_template("doctorRequest.html", bloodbank_id=bloodbank_id)


@app.route("/doctorRequest1", methods=['post'])
def doctorRequest1():
    bloodbank_id = request.form.get('bloodbank_id')
    doctor_id = session['doctor_id']
    bloodGroup = request.form.get('bloodGroup')
    Number_Of_Units = request.form.get('Number_Of_Units')
    Requirement_before = request.form.get('Requirement_before')

    fromdate = datetime.datetime.today()
    Date_of_Request = fromdate.strftime('%Y-%m-%d')

    status = "Doctor Requested"
    query = {"bloodbank_id": ObjectId(bloodbank_id), "doctor_id": ObjectId(doctor_id), "bloodGroup": bloodGroup, "Number_Of_Units": Number_Of_Units, "Requirement_before": Requirement_before, "Date_of_Request": Date_of_Request, "status": status}
    print(query)
    DoctorRequest_col.insert_one(query)
    return render_template("msg.html", message="Blood Request Sended Successfully")


def get_doctor_Id(doctor_id):
    query = {'_id': doctor_id}
    Doctor = Doctor_col.find_one(query)
    return Doctor


@app.route("/viewBloodRequest")
def viewBloodRequest():
    doctor_id = session['doctor_id']
    type = request.args.get('type')
    print(type)
    query = {}
    if type == 'Processing':
        query = {"doctor_id": ObjectId(doctor_id), "status": "Doctor Requested"}
    elif type == 'Completed':
        query = {"doctor_id": ObjectId(doctor_id), "status": "Blood Units Assigned"}
    elif type == 'Suspended':
        query = {"doctor_id": ObjectId(doctor_id),
                 "$or": [{"status": "Doctor Cancelled"}, {"status": "BloodBank Rejected"}]}
    print(query)
    Requests = DoctorRequest_col.find(query)
    return render_template("viewBloodRequest.html", Requests=Requests, get_bloodbank_by_Id=get_bloodbank_by_Id,
                           get_doctor_Id=get_doctor_Id)


@app.route("/viewDoctor")
def viewDoctor():
    Doctors = Doctor_col.find()
    return render_template("viewDoctor.html", Doctors=Doctors)


@app.route("/authorisedDoctor")
def authorisedDoctor():
    doctor_id = request.args.get('doctor_id')
    query = {'_id': ObjectId(doctor_id)}
    query1 = {"$set": {"status": "Authorised"}}
    Doctor_col.update_one(query, query1)
    return redirect("/viewDoctor")


@app.route("/blogin")
def blogin():
    return render_template("blogin.html")


@app.route("/blogin1", methods=['post'])
def blogin1():
    email = request.form.get('email')
    password = request.form.get('password')
    query = {"email": email, "password": password}
    count = BloodBank_col.count_documents(query)
    if count > 0:
        bloodBank = BloodBank_col.find_one(query)
        if bloodBank["status"] == "Authorised":
            session['bloodBank_id'] = str(bloodBank['_id'])
            session['role'] = 'BloodBank'
            return render_template("bhome.html")
        else:
            return render_template("msg.html", message="Blood Bank is Unauthorised", color="bg-danger text-white")
    else:
        return render_template("msg.html", message="Invalid Login Details", color="bg-danger text-white")


@app.route("/bloodBankRegister")
def bloodBankRegister():
    return render_template("bloodBankRegister.html")


@app.route("/bloodBankRegister1", methods=['post'])
def bloodBankRegister1():
    name = request.form.get('name')
    phoneno = request.form.get('phoneno')
    email = request.form.get('email')
    password = request.form.get('password')
    location = request.form.get('location')
    address = request.form.get('address')
    query = {"$or": [{"email": email}, {"phoneno": phoneno}]}
    count = BloodBank_col.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Details", color="bg-danger text-white")
    else:
        query = {"name": name, "phoneno": phoneno, "email": email, "password": password, "location": location, "address": address,"status": "Unauthorised"}
        BloodBank_col.insert_one(query)
        return render_template("msg.html", message="Blood Bank Register Successfully", color="bg-success text-white")


@app.route("/viewBloodBank")
def viewBloodBank():
    BloodBank = BloodBank_col.find()
    return render_template("viewBloodBank.html", BloodBank=BloodBank)


@app.route("/authorisedBloodBank")
def authorisedBloodBank():
    bloodbank_id = request.args.get('bloodbank_id')
    query = {'_id': ObjectId(bloodbank_id)}
    query1 = {"$set": {"status": "Authorised"}}
    BloodBank_col.update_one(query, query1)
    return redirect("/viewBloodBank")


@app.route("/bloodRequest")
def bloodRequest():
    bloodBank_id = session['bloodBank_id']
    type = request.args.get('type')
    query = {}
    if type == 'Processing':
        query = {"bloodbank_id": ObjectId(bloodBank_id),"$or": [{"status": "Donor Requested"}, {"status": "Blood Bank Accepted"}]}
    elif type == 'Completed':
        query = {"bloodbank_id": ObjectId(bloodBank_id), "status": "Blood Donated"}
    elif type == 'Suspended':
        query = {"bloodbank_id": ObjectId(bloodBank_id),"$or": [{"status": "Donor Cancelled"}, {"status": "Blood Bank Rejected"}]}
    print(query)
    schedules = schedule_col.find(query)
    return render_template("bloodRequest.html", schedules=schedules, get_bloodbank_by_Id=get_bloodbank_by_Id, get_donor_Id=get_donor_Id)


@app.route("/acceptBloodRequest")
def acceptBloodRequest():
    schedule_id = request.args.get('schedule_id')
    query = {'_id': ObjectId(schedule_id)}
    query1 = {"$set": {"status": "Blood Bank Accepted"}}
    aa = schedule_col.update_one(query, query1)
    return redirect("/bloodRequest?type=Processing")


@app.route("/rejectBloodRequest")
def rejectBloodRequest():
    schedule_id = request.args.get('schedule_id')
    query = {'_id': ObjectId(schedule_id)}
    query1 = {"$set": {"status": "Blood Bank Rejected"}}
    schedule_col.update_one(query, query1)
    return redirect("/bloodRequest?type=Suspended")


@app.route("/bloodDonated")
def bloodDonated():
    schedule_id = request.args.get('schedule_id')
    return render_template("bloodDonated.html", schedule_id=schedule_id)


@app.route("/bloodDonated1", methods=['post'])
def bloodDonated1():
    schedule_id = request.form.get('schedule_id')
    blood_Unit_Number = request.form.get('blood_Unit_Number')
    query = {"blood_Unit_Number": blood_Unit_Number}
    count = schedule_col.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Blood Unit Number")
    query1 = {'_id': ObjectId(schedule_id)}
    query2 = {"$set": {"status": "Blood Donated", "blood_Unit_Number": blood_Unit_Number}}
    schedule_col.update_one(query1, query2)
    query3 = {'_id': ObjectId(schedule_id)}
    schedule = schedule_col.find_one(query3)
    bloodbank_id = schedule["bloodbank_id"]
    donor_id = schedule["donor_id"]
    bloodGroup = schedule["bloodGroup"]
    status = "Available"
    query4 = {"bloodbank_id":ObjectId(bloodbank_id), "donor_id": ObjectId(donor_id),"bloodGroup": bloodGroup, "blood_Unit_Number": blood_Unit_Number,"status": status}
    stock_col.insert_one(query4)
    return render_template("msg.html", message="Blood Donated Successfully")


@app.route("/bloodStock")
def bloodStock():
    bloodbank_id = session['bloodBank_id']
    query = {'bloodbank_id': ObjectId(bloodbank_id)}
    stocks = stock_col.find(query)
    return render_template("bloodStock.html", stocks=stocks, get_bloodbank_by_Id=get_bloodbank_by_Id, get_donor_Id=get_donor_Id)


@app.route("/viewDoctorRequest")
def viewDoctorRequest():
    bloodbank_id = session['bloodBank_id']
    type = request.args.get('type')
    print(type)
    query = {}
    if type == 'Processing':
        query = {"bloodbank_id": ObjectId(bloodbank_id), "status": "Doctor Requested"}
    elif type == 'Completed':
        query = {"bloodbank_id": ObjectId(bloodbank_id), "status": "Blood Units Assigned"}
    elif type == 'Suspended':
        query = {"bloodbank_id": ObjectId(bloodbank_id),
                 "$or": [{"status": "Doctor Cancelled"}, {"status": "BloodBank Rejected"}]}
    print(query)
    Requests = DoctorRequest_col.find(query)
    return render_template("viewDoctorRequest.html", Requests=Requests, get_bloodbank_by_Id=get_bloodbank_by_Id, get_doctor_Id=get_doctor_Id)


@app.route("/assignBlood")
def assignBlood():
    Doctor_Request_id = request.args.get('Doctor_Request_id')
    bloodGroup = request.args.get('bloodGroup')
    bloodbank_id = session['bloodBank_id']
    query = {"bloodbank_id": ObjectId(bloodbank_id), "bloodGroup": bloodGroup, "status": "Available"}
    print(query)
    stocks = stock_col.find(query)
    return render_template("assignBlood.html", stocks=stocks, Doctor_Request_id=Doctor_Request_id, bloodGroup=bloodGroup, get_bloodbank_by_Id=get_bloodbank_by_Id, get_donor_Id=get_donor_Id)


@app.route("/assignedBlood2")
def assignedBlood2():
    stock_id = request.args.get('stock_id')
    Doctor_Request_id = request.args.get('Doctor_Request_id')
    bloodGroup = request.args.get('bloodGroup')
    query = {"_id": ObjectId(stock_id)}
    query1 = {"$set": {"status": "Sold"}}
    stock_col.update_one(query, query1)

    query = {"_id": ObjectId(Doctor_Request_id)}
    query1 = {"$push": {"stock_ids": ObjectId(stock_id)}}
    print(query)
    print(query1)
    DoctorRequest_col.update_one(query, query1)

    query = {"_id": ObjectId(Doctor_Request_id)}
    Doctor_Request = DoctorRequest_col.find_one(query)

    if int(Doctor_Request["Number_Of_Units"]) > len(Doctor_Request["stock_ids"]):
        return redirect("assignBlood?Doctor_Request_id=" + str(Doctor_Request_id)+"&bloodGroup=" + str(bloodGroup))
    else:
        query = {"_id": ObjectId(Doctor_Request_id)}
        query1 = {"$set": {"status": "Blood Units Assigned"}}
        DoctorRequest_col.update_one(query, query1)
        return render_template("msg.html", message="Stock Assigned Successfully")


@app.route("/rejectDoctorRequest")
def rejectDoctorRequest():
    Doctor_Request_id = request.args.get('Doctor_Request_id')
    query = {'_id': ObjectId(Doctor_Request_id)}
    query1 = {"$set": {"status": "BloodBank Rejected"}}
    DoctorRequest_col.update_one(query, query1)
    return render_template("msg.html", message="Doctor BloodRequest Rejected")


@app.route("/doctorCancelled")
def doctorCancelled():
    Doctor_Request_id = request.args.get('Doctor_Request_id')
    query = {'_id': ObjectId(Doctor_Request_id)}
    query1 = {"$set": {"status": "Doctor Cancelled"}}
    DoctorRequest_col.update_one(query, query1)
    return render_template("msg.html", message="Doctor Cancelled the Request")



@app.route("/donorlogin")
def donorlogin():
    return render_template("donorlogin.html")


@app.route("/donorlogin1", methods=['post'])
def donorlogin1():
    email = request.form.get('email')
    otp = random.randint(1000, 10000)
    send_email("Login Verification for Blood Donation System", " Hello Use this OTP "+str(otp)+" to Access your Account",email)
    return render_template("donorlogin1.html", email=email, otp=otp)


@app.route("/donorlogin2", methods=['post'])
def donorlogin2():
    email = request.form.get('email')
    otp = request.form.get('otp')
    otp2 = request.form.get('otp2')
    query = {"email": email}
    if otp == otp2:
        donor = donor_col.find_one(query)
        if donor == None:
            return render_template("donorReg.html", email=email)
        else:
            query = {"email": email}
            donor = donor_col.find_one(query)
            session['donor_id'] = str(donor['_id'])
            session['role'] = 'Donor'
            return render_template("donorhome.html")
    else:
        return render_template("msg.html", message="Invalid OTP")


@app.route("/donorReg1", methods=['post'])
def donorReg1():
    donorname = request.form.get('donorname')
    phoneno = request.form.get('phoneno')
    email = request.form.get('email')
    bloodGroup = request.form.get('bloodGroup')
    query = {"donorname": donorname, "phoneno": phoneno,"email": email, "bloodGroup": bloodGroup}
    donor_col.insert_one(query)
    query2 = {"email": email}
    donor = donor_col.find_one(query2)
    session['donor_id'] = str(donor['_id'])
    session['role'] = 'Donor'
    return render_template("donorhome.html")


@app.route("/donateBlood")
def donateBlood():
    bloodBanks = BloodBank_col.find()
    return render_template("donateBlood.html", bloodBanks=bloodBanks, can_donor_donate=can_donor_donate)


def can_donor_donate(donor_id):
    query = {"donor_id": ObjectId(donor_id), "$or": [{"status": "Donor Requested"}, {"status": "Blood Bank Accepted"}, {"status":"Blood Donated"}]}
    print(query)
    schedules = schedule_col.find(query)
    for schedule in schedules:
        datee = schedule["appointment_date"]
        datee = datee.replace('T', ' ')
        datee = datetime.datetime.strptime(datee, "%Y-%m-%d %H:%M")
        days_diff = None
        print(datee, datetime.datetime.now())
        if datee > datetime.datetime.now():
            days_diff = datee - datetime.datetime.now()
        else:
            days_diff = datetime.datetime.now() - datee

        days = days_diff.days
        print(days)
        print(type(days))
        if days < 60:
            return False

    return True


@app.route("/appointment")
def appointment():
    bloodbank_id = ObjectId(request.args.get('bloodbank_id'))
    return render_template("appointment.html", bloodbank_id=bloodbank_id)


@app.route("/appointment1", methods=['post'])
def appointment1():
    bloodbank_id = request.form.get('bloodbank_id')
    appointment_date = request.form.get('appointment_date')
    donor_id = session['donor_id']
    query = {"_id": ObjectId(donor_id)}
    donor = donor_col.find_one(query)
    bloodGroup = donor['bloodGroup']
    status = "Donor Requested"
    query1 = {"bloodbank_id": ObjectId(bloodbank_id), "appointment_date": appointment_date, "donor_id": ObjectId(donor_id), "bloodGroup": bloodGroup, "status": status}
    schedule_col.insert_one(query1)
    return render_template("msg.html", message="Appointment Booked Successfully")


def get_bloodbank_by_Id(bloodbank_id):
    query = {'_id': bloodbank_id}
    bloodBank = BloodBank_col.find_one(query)
    return bloodBank


def get_donor_Id(donor_id):
    query = {'_id': donor_id}
    donor = donor_col.find_one(query)
    return donor


@app.route("/viewBloodDonations")
def viewBloodDonations():
    donor_id = session['donor_id']
    query = {"donor_id": ObjectId(donor_id)}
    print(query)
    schedules = schedule_col.find(query)
    return render_template("viewBloodDonations.html", schedules=schedules, get_bloodbank_by_Id=get_bloodbank_by_Id, get_donor_Id=get_donor_Id)


@app.route("/requestCancelled")
def requestCancelled():
    schedule_id = request.args.get('schedule_id')
    query = {'_id': ObjectId(schedule_id)}
    query1 = {"$set": {"status": "Donor Cancelled"}}
    schedule_col.update_one(query, query1)
    return redirect("/viewBloodDonations")


@app.route("/addBloodCamp")
def addBloodCamp():
    return render_template("addBloodCamp.html")


@app.route("/addBloodCamp1", methods=['post'])
def addBloodCamp1():
    bloodbank_id = session['bloodBank_id']
    title = request.form.get('title')
    address = request.form.get('address')
    dateTime = request.form.get('dateTime')
    about = request.form.get('about')
    status = "Campaign Publishment"
    query ={"bloodbank_id": ObjectId(bloodbank_id), "title": title, "address": address, "dateTime": dateTime, "about":about, "status": status}
    campaign_col.insert_one(query)
    return render_template("addBloodCamp.html")


@app.route("/viewBloodCamp")
def viewBloodCamp():
    bloodbank_id = session['bloodBank_id']
    query = {"bloodbank_id": ObjectId(bloodbank_id)}
    campaigns = campaign_col.find(query)
    return render_template("viewBloodCamp.html", campaigns=campaigns, get_bloodbank_by_Id=get_bloodbank_by_Id)


@app.route("/addDonor")
def addDonor():
    campaign_id = request.args.get('campaign_id')
    return render_template("addDonor.html", campaign_id=campaign_id)


@app.route("/addDonor1", methods=['post'])
def addDonor1():
    campaign_id = request.form.get('campaign_id')
    donorname = request.form.get('donorname')
    phoneno = request.form.get('phoneno')
    email = request.form.get('email')
    bloodGroup = request.form.get('bloodGroup')
    blood_Unit_Number = request.form.get('blood_Unit_Number')
    query = {"blood_Unit_Number": blood_Unit_Number}
    count = schedule_col.count_documents(query)
    if count > 0:
        return render_template("msg.html", message="Duplicate Blood Unit Number")
    else:
        donor_id = None
        query = {"email": email}
        count = donor_col.count_documents(query)
        if count > 0:
            donor = donor_col.find_one(query)
            donor_id = donor['_id']
        else:
            query = {"donorname": donorname, "phoneno": phoneno, "email": email, "bloodGroup": bloodGroup, "blood_Unit_Number": blood_Unit_Number}
            result = donor_col.insert_one(query)
            donor_id = result.inserted_id
        bloodbank_id = session['bloodBank_id']
        appointment_date = datetime.datetime.now()
        status = "Blood Donated"
        query1 = {"bloodbank_id": ObjectId(bloodbank_id), "donor_id": ObjectId(donor_id), "campaign_id": ObjectId(campaign_id),"appointment_date": appointment_date, "bloodGroup": bloodGroup,"blood_Unit_Number": blood_Unit_Number, "status": status}
        schedule_col.insert_one(query1)
        status = "Available"
        query2 = {"bloodbank_id": ObjectId(bloodbank_id), "donor_id": ObjectId(donor_id), "bloodGroup": bloodGroup,"blood_Unit_Number": blood_Unit_Number, "status": status}
        stock_col.insert_one(query2)
        return render_template("msg.html", message="Blood Donated Successfully",  color="bg-success text-white")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")


app.run(debug=True)