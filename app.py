from flask import Flask,request,render_template,request
from pymongo import MongoClient


app = Flask(__name__)
app.config['SECRET_KEY'] = 'b58f1ad3ab27a913c64246143682ebf5'

global User_data_retrived,Admin_data_retrived,User_data,Admin_data,db_mongo
connect_link = "mongodb+srv://sathvik123:Systemtest123@cluster0.r6rot.mongodb.net/Indobytes-test?retryWrites=true&w=majority"
cluster = MongoClient(connect_link)
db_mongo= cluster["Indobytes-Test"]
Admin_data = db_mongo['Indobytes-Test']
Admin_data_retrived = Admin_data.find({})

User_data = db_mongo['Indobytes-Users']
User_data_retrived = User_data.find({})

global Admin_ID,Admin_password,fetch_data


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
        
    return siid_arr,name_arr,email_arr,username_arr,password_arr,state_arr,index




@app.route('/', methods=['GET', 'POST'])
def login():
    siid_arr,name_arr,email_arr,username_arr,password_arr,state_arr,index = fetch_data()
    if request.method == 'POST':
        username = str(request.form['username'])
        password = str(request.form['password'])

        for i in range(0,index):
            if username_arr[i]==username and password_arr[i]==password:
                print("User Authenticated.. ")
                return render_template("login.html",status_login = "Success")
            elif email_arr[i]==username and password_arr[i]==password:
                print("User Authenticated.. ")
                return render_template("login.html",status_login = "Success")
            
        return render_template("login.html",status_login = "Error")
                
    return render_template("login.html",status_login = "Entry")




@app.route('/register', methods=['GET', 'POST'])
def register():
    
    
    if request.method == 'POST':
        new_username = str(request.form['username'])
        User_data = db_mongo['Indobytes-Users']
        User_data_retrived = User_data.find({})
        count = 0 
        for person_number in User_data_retrived:
            count = count+1
            if new_username == person_number['username']:
                return render_template("register.html",Register_login = "Exists")

        
        new_name = str(request.form['first_name'])
        new_Email = str(request.form['email'])
        
        new_password = str(request.form['password'])
        
        
        
        Reg_Dict = { "siid":count,
                    "name":new_name,
                    "Email":new_Email,
                    "username":new_username,
                    "password":new_password,
                    "state":"active"}
        User_data.insert_one(Reg_Dict)
        return render_template("register.html",Register_login = "Success")
        
        
        
    
    
    
    
    return render_template("register.html",Register_login = "Entry")




@app.route('/admin', methods=['GET', 'POST'])
def admin():
    siid_arr,name_arr,email_arr,username_arr,password_arr,state_arr,index = fetch_data()
    Admin_data = db_mongo['Indobytes-Test']
    Admin_data_retrived = Admin_data.find({})
    for item in Admin_data_retrived:
        Admin_ID = item['adminID']
        Admin_password = item['password']
    
    if request.method == 'POST':
        Name = str(request.form['AdminID'])
        Admin_pass = str(request.form['Password'])
        if Name == Admin_ID and Admin_pass == Admin_password:
            print("Admin Authenticated..... ")
            return render_template("admin.html",status = "Authenticated",siid=siid_arr,name=name_arr,
                           email=email_arr,username=username_arr,state=state_arr,max_number = index)
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
            User_data.update_one({"username":username_person},{"$set":{"password":password1}})
            return render_template("forgotpassword.html",status_login = "Success")
                    
    return render_template("forgotpassword.html",status_login = "Entry")



if __name__ == '__main__':
    app.run(debug=True)

