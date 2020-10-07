from flask import Flask,request,render_template,request,redirect,url_for,session
from pymongo import MongoClient
from flask_mail import Mail, Message
import smtplib
from random import randint
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SECRET_KEY'] = 'b58f1ad3ab27a913c64246143682ebf5'
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sathvik435teenz@gmail.com'
app.config['MAIL_PASSWORD'] = 'Vs@8106809666'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


global User_data_retrived,Admin_data_retrived,User_data,Admin_data,db_mongo
connect_link = "mongodb+srv://sathvik123:Systemtest123@cluster0.r6rot.mongodb.net/Indobytes-test?retryWrites=true&w=majority"
cluster = MongoClient(connect_link)
db_mongo= cluster["Indobytes-Test"]
Admin_data = db_mongo['Indobytes-Test']
Admin_data_retrived = Admin_data.find({})

User_data = db_mongo['Indobytes-Users']
User_data_retrived = User_data.find({})

global Admin_ID,Admin_password,fetch_data,send_mail


def send_mail(to_mail):
    global OTP
    print(to_mail)
    msg = Message('IndoBytes SystemTest Demo', sender = 'sathvik435@gmail.com', recipients = [to_mail])
    OTP = randint(100000,999999)
    msg.body = "This is regarding confirmation of the Successfull Registration in the IndoBytes Website\n\n Your OTP is "+ str(OTP)
    mail.send(msg)
    print("Mail sent")
    print("OTP = ",OTP)
    return "Sent"
    
    
    
    
    
def fetch_data():
    global siid_arr,name_arr,email_arr,username_arr,password_arr,state_arr,index
    User_data = db_mongo['Indobytes-Users']
    User_data_retrived = User_data.find({})
    siid_arr = []
    name_arr = []
    email_arr = []
    username_arr = []
    password_arr = []
    state_arr = []
    index = 0
    for user in User_data_retrived:
        siid_arr.append(user['siid'])
        name_arr.append(user['name'])
        email_arr.append(user['Email'])
        username_arr.append(user['username'])
        password_arr.append(user['password'])
        state_arr.append(user['state'])
        index=index+1
        
    


@app.route('/Userprofile', methods=['GET', 'POST'])
def Userprofile():
    
    if "user" in session:
        Logged_User = session["user"]
        Logged_user_name = session["username"]
    
        findmyquery_E = { "state": {"$regex":"Enable" } }
        Enabled_count =  User_data.find(findmyquery_E).count()
        print(Enabled_count)

        findmyquery_D = { "state": {"$regex":"Disable" } }
        Disabled_count =  User_data.find(findmyquery_D).count()
        print(Disabled_count)

        
        Full_count = User_data.find().count()
        
        
        return render_template("UserProfile.html",Logged_User = Logged_User,Logged_user_name=Logged_user_name,Enabled_count=Enabled_count,
                            Disabled_count=Disabled_count,Full_count=Full_count)
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def login():
    if "user" in session:
        return redirect(url_for('Userprofile'))
        
    global Logged_User,Logged_user_name
    Logged_User = ""
    Logged_user_name = ""
    fetch_data()
    if request.method == 'POST':
        username = str(request.form['username'])
        password = str(request.form['password'])
        password_check_usr = False
        password_check_email = False
        Personlogindata_usr = User_data.find_one({"username": username})
        Personlogindata_email = User_data.find_one({"Email": username})
        
        if (Personlogindata_usr!=None):
            password_check_usr = check_password_hash(Personlogindata_usr["password"],password)
            
        if (Personlogindata_email!=None):
            password_check_email = check_password_hash(Personlogindata_email["password"],password)

        if (Personlogindata_usr!=None and password_check_usr==True  ) :
            if Personlogindata_usr["state"] == "Disable":
                return render_template("login.html",status_login = "Disable")
            else:
                Logged_User = Personlogindata_usr["username"] 
                Logged_user_name =  Personlogindata_usr["name"]
                session["user"] = Logged_User
                session["username"] = Logged_user_name
                return redirect(url_for('Userprofile'))
            
            
        elif  (Personlogindata_email!=None and password_check_email==True) : 
            if Personlogindata_email["state"] == "Disable":
                return render_template("login.html",status_login = "Disable")
            else:
                Logged_User = Personlogindata_email["username"] 
                Logged_user_name =  Personlogindata_email["name"]
                session["user"] = Logged_User
                session["username"] = Logged_user_name
                return redirect(url_for('Userprofile'))
      
      
        
        return render_template("login.html",status_login = "Error")
                
    return render_template("login.html",status_login = "Entry")




@app.route('/register', methods=['GET', 'POST'])
def register():
    
    
    if request.method == 'POST':
        new_username = str(request.form['username'])
        new_username = new_username.replace("@","")
        PersonREGdata_usr = User_data.find_one({"username": new_username})
        if (PersonREGdata_usr!=None):
            return render_template("register.html",Register_login = "Exists")
        
        new_name = str(request.form['first_name'])
        new_Email = str(request.form['email'])
        new_password = str(request.form['password'])
        
        
        Full_count = User_data.find().count()
        Reg_Dict = { "siid":Full_count+1,
                    "name":new_name,
                    "Email":new_Email,
                    "username":new_username,
                    "password":generate_password_hash(new_password),
                    "state":"Enable"}
        User_data.insert_one(Reg_Dict)
        send_mail(new_Email)
        return render_template("register.html",Register_login = "Success")
        
        
        
    
    
    
    
    return render_template("register.html",Register_login = "Entry")

@app.route('/adminpost', methods=['GET'])
def adminpost():
    fetch_data()
    return render_template("admin.html",status = "Authenticated",siid=siid_arr,name=name_arr,
                    email=email_arr,username=username_arr,state=state_arr,max_number = index)
        


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    Admin_pass_check = False
    fetch_data()
    Admin_data = db_mongo['Indobytes-Test']
    Admin_data_retrived = Admin_data.find({})
    for item in Admin_data_retrived:
        Admin_ID = item['adminID']
        Admin_password = item['password']
    print (Admin_password)
    
    if request.method == 'POST':
        Name = str(request.form['AdminID'])
        Admin_pass = str(request.form['Password'])
        
        Admin_pass_check = check_password_hash(Admin_password,Admin_pass)
        
        
        if Name == Admin_ID and Admin_pass_check == True:
            print("Admin Authenticated..... ")
            return redirect(url_for('adminpost'))
        else:
            print("Admin Not Authenticated..... ")
            return render_template("adminlogin.html", status = "Modal")
    return render_template("adminlogin.html",status = "Entry")





@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        username_person = str(request.form['username'])
        password1 = str(request.form['password1'])
        password2 = str(request.form['password2'])
        if password1 != password2 :
            return render_template("forgotpassword.html",status_login = "Error")
        else:
            Personlogindata_usr = User_data.find_one({"username": username_person})
            if (Personlogindata_usr!=None ):
                if Personlogindata_usr["state"] == "Disable":
                    return render_template("forgotpassword.html",status_login = "Disable")
                else:
                    User_data.update_one({"username":username_person},{"$set":{"password": generate_password_hash(password1)}})
                    if "user" in session:
                        Logged_user_name = session["username"]
                        print(Logged_user_name)
                    return render_template("forgotpassword.html",status_login = "Success")
                    
            else:
                return render_template("forgotpassword.html",status_login = "Error")    
            
            
            # return render_template("forgotpassword.html",status_login = "Success")
               
    return render_template("forgotpassword.html",status_login = "Entry")

@app.route('/delete/<string:del_username>', methods=['GET', 'POST'])
def delete(del_username):
    print(del_username)
    myquery = { "username": {"$regex":del_username } }
    x = User_data.delete_many(myquery)
    print(x.deleted_count, " documents deleted.")
    return redirect(url_for('adminpost'))

@app.route('/Alter/<string:dis_username>/<string:flag>', methods=['GET', 'POST'])
def disable(dis_username,flag):
    print(dis_username)
    print(flag)
    User_data.update_one({"username":dis_username},{"$set":{"state":flag }})
    return redirect(url_for('adminpost'))



@app.route('/Edit', methods=['GET', 'POST'])
def Edit_post():
    if request.method == 'GET':
        person_record = User_data.find_one({"username": edit_username_gl})
        print(person_record)
        edit_name = person_record["name"]
        edit_email = person_record["Email"]
        edit_username = person_record["username"]
        edit_password = person_record["password"]
        return render_template("Edit.html",status_login = "Entry",edit_name=edit_name,
                              edit_email=edit_email,edit_username=edit_username,edit_password=(edit_password) )
    if request.method == 'POST':
        updtd_username = str(request.form['username'])
        updtd_firstname = str(request.form['first_name'])
        updtd_email = str(request.form['email'])
        updtd_password = str(request.form['password'])
        User_data.update_one({"username":edit_username_gl},{"$set":{"name":updtd_firstname,
                                                                    "Email":updtd_email,
                                                                    "username":updtd_username,
                                                                    "password":generate_password_hash(updtd_password),
                                                                    "state":"Enable"}})
        
        return redirect(url_for('adminpost'))
    return redirect(url_for('adminpost'))
    

@app.route('/Edit/<string:edit_username>/', methods=['GET', 'POST'])
def Edit(edit_username):
    global edit_username_gl
    edit_username_gl = (edit_username)
    return redirect(url_for('Edit_post'))

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop("user",None)
    session.pop("username",None)
   
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

