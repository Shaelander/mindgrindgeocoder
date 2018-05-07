from flask import Flask,render_template,request,send_file
from werkzeug import secure_filename
import geopy
from geopy.geocoders import Nominatim
import pandas
import logging

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/sucess",methods = ['POST'])
def sucess():
    global file

    nom = Nominatim(timeout=3,scheme='http')
    if request.method == 'POST':
        file = request.files["file"]
        #secure_filename is used so that no one can add file like "..\.\" which
        #will point to server root and do some thing malicious or hack
        file.save(secure_filename("uploaded"+ file.filename))
        #a stands for append mode which will add something in file
        with open ("uploaded"+ file.filename,"r+") as f:
            try:
                df= pandas.read_csv(f)


                #df["Address"] =df["Address"] + "," + df["City"] + "," + df["State"] + "," +df["Country"]
                df["Coordintates"] = df["Address"].apply(nom.geocode)
                df["Latitude"] = df["Coordintates"].apply(lambda x : x.latitude if x  != None else None)
                df["Logitude"] = df["Coordintates"].apply(lambda x : x.longitude if x !=None else None)
                df = df.drop("Coordintates",1)
                f.seek(0)
                f.truncate()
                f.write(str(df.to_csv(index= None)))
                return render_template("home.html", btn="download.html",text= df.to_html(index = None))
            except KeyError:
                return render_template("home.html",text ="No Address column found!.Kindly fix the .csv file by adding Address column and put all addresses under 'Address' column.")

@app.route("/download/")
def download():
    return send_file("uploaded"+ file.filename, attachment_filename="longlatfile.csv", as_attachment=True)


if __name__ == '__main__':
    app.debug = True
    app.run()
