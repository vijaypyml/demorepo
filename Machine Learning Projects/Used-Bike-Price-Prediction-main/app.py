from flask import Flask,request,render_template
import pandas as pd 
import pickle

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

app=Flask(__name__)
model=pickle.load(open('used_bike.pkl','rb'))
print(type(model))
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about.html")
def about():
    return render_template("about.html")

@app.route("/home.html")
def return_home():
    return render_template("home.html")

@app.route("/predict", methods = ['GET','POST'])
def predict():
    if request.method == "POST":
        #Bike Model
        Bike_Model=0
        bike_model = request.form["bike_model"]
        h = pd.read_excel('Dictionary.xlsx', sheet_name='Model sorted')
        Bike_Model=int(h[h.bike == bike_model].encoding)
        print('Bike_Model',Bike_Model)
        print('type Bike_Model',type(Bike_Model))

        # if bike_model == 'TVS Star':
	    #     Bike_Model = 102

        
        #Cubic Capacity
        Cubic_Capacity=0
        cc = request.form["cubic_capacity"]
        Cubic_Capacity=int(cc)
        print('Cubic_Capacity',Cubic_Capacity)
        print('type Cubic_Capacity',type(Cubic_Capacity))
        # if cc == '110':
        #     Cubic_Capacity = 110


        #Year
        
        Year=int(request.form['year'])
        print('Year',Year)
        print('type Year',type(Year))
        

        #Location
        Location=0
        place=request.form['location']
        l = pd.read_excel('Dictionary.xlsx', sheet_name='Location sorted')
        Location=int(l.loc[l.state == place].encoding)
        print('Location',Location)
        print('type Location',type(Location))
        # if place == 'Gujarat':
        # 	Location= 1166


        #Running
        
        Running=int(request.form.get('distance'))
        print('Running',Running)
        print('type Running',type(Running))
        
        
        #Owner
        Second_owner=0
        Third_owner=0
        Fourth_owner_or_more=0
        
        owner=request.form['owner']
        if owner=='Second owner':
            Second_owner=1
        elif owner=='Third owner':
            Third_owner=1
        elif owner=='Fourth Owner Or More':
            Fourth_owner_or_more=1

        
        input_variables = pd.DataFrame([[Running,Cubic_Capacity,Year,Fourth_owner_or_more,Second_owner,Third_owner,Bike_Model,Location]],
        columns=['Running','cc','Year','Fourth Owner Or More','Second Owner','Third Owner','bike_model','Location'],
        dtype=float)
        

        #prediction=model.predict([[Cubic_Capacity,year,running,Second_owner,Third_owner,Fourth_owner_or_more,Bike_Model,location]])
        prediction=model.predict(input_variables)
        output=round(prediction[0])

        # return render_template('home.html',prediction_text="Your Bike price is Rs. {}".format(output))
        return render_template('results.html',prediction_text="Your Bike price is Rs. {}".format(output))
        # return render_template('top.html', top=top_str, pop=pop_str)


    return render_template("home.html")
        
if __name__ == "__main__":
    app.run(debug=True)