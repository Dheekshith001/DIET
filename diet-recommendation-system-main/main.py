from flask import Flask, render_template, request
import pickle
import pandas as pd
import csv

app = Flask(__name__)

# Load ML model
with open('food_model.pickle', 'rb') as file:
    model = pickle.load(file)

# Load dataset
food_data = pd.read_csv('done_food_data.csv')

# Utility to read and sort CSV
def read_csv(file_path, sort_by='Descrip'):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
        sorted_rows = sorted(rows, key=lambda x: x[sort_by])
        return sorted_rows

@app.route("/")
def index():
    return render_template("mainpage.html")

@app.route("/predict", methods=['POST'])
def predict():
    try:
        input_1 = float(request.form['input_1'])
        input_2 = float(request.form['input_2'])
        input_3 = float(request.form['input_3'])

        inputs = [[input_1, input_2, input_3]]
        prediction = model.predict(inputs)

        if prediction[0] == 'Muscle_Gain':
            result = 'Muscle Gain'
        elif prediction[0] == 'Weight_Gain':
            result = 'Weight Gain'
        elif prediction[0] == 'Weight_Loss':
            result = 'Weight Loss'
        else:
            result = 'General food'
    except Exception as e:
        result = f"Error in prediction: {e}"

    return render_template("mainpage.html", result=result)

@app.route("/musclegain", methods=['POST'])
def musclegain():
    vegetarian = request.form.getlist('vegetarian')
    iron = request.form.getlist('iron')
    calcium = request.form.getlist('calcium')

    muscle_gain_data = food_data[food_data['category'] == 'Muscle_Gain']

    if 'iron' in iron:
        muscle_gain_data = muscle_gain_data[muscle_gain_data['Iron_mg'] > 6]
    if 'calcium' in calcium:
        muscle_gain_data = muscle_gain_data[muscle_gain_data['Calcium_mg'] > 150]
    if 'vegetarian' in vegetarian:
        exclude_keywords = ['Egg','Fish','meat','beef','Chicken','Beef','Deer','lamb','crab','pork','Frog legs',
                            'Pork','Turkey','flesh','Ostrich','Emu','cuttelfish','Seaweed','crayfish','shrimp','Octopus']
        muscle_gain_data = muscle_gain_data[~muscle_gain_data['Descrip'].str.contains('|'.join(exclude_keywords), case=False)]

    musclegainfoods = muscle_gain_data['Descrip'].sample(n=5).to_list()
    return render_template("mainpage.html", musclegainfoods=musclegainfoods)

@app.route("/weightgain", methods=['POST'])
def weightgain():
    vegetarian = request.form.getlist('vegetarian')
    iron = request.form.getlist('iron')
    calcium = request.form.getlist('calcium')

    weight_gain_data = food_data[food_data['category'] == 'Weight_Gain']

    if 'iron' in iron:
        weight_gain_data = weight_gain_data[weight_gain_data['Iron_mg'] > 6]
    if 'calcium' in calcium:
        weight_gain_data = weight_gain_data[weight_gain_data['Calcium_mg'] > 150]
    if 'vegetarian' in vegetarian:
        exclude_keywords = ['Egg','Fish','meat','beef','Chicken','Beef','Deer','lamb','crab','pork','turkey','flesh']
        weight_gain_data = weight_gain_data[~weight_gain_data['Descrip'].str.contains('|'.join(exclude_keywords), case=False)]

    weightgainfoods = weight_gain_data['Descrip'].sample(n=5).to_list()
    return render_template("mainpage.html", weightgainfoods=weightgainfoods)

@app.route("/weightloss", methods=['POST'])
def weightloss():
    vegetarian = request.form.getlist('vegetarian')
    iron = request.form.getlist('iron')
    calcium = request.form.getlist('calcium')

    weight_loss_data = food_data[food_data['category'] == 'Weight_Loss']

    if 'iron' in iron:
        weight_loss_data = weight_loss_data[weight_loss_data['Iron_mg'] > 6]
    if 'calcium' in calcium:
        weight_loss_data = weight_loss_data[weight_loss_data['Calcium_mg'] > 150]
    if 'vegetarian' in vegetarian:
        exclude_keywords = ['Egg','Fish','meat','beef','Chicken','Beef','Deer','lamb','crab','pork','turkey','flesh']
        weight_loss_data = weight_loss_data[~weight_loss_data['Descrip'].str.contains('|'.join(exclude_keywords), case=False)]

    weightlossfoods = weight_loss_data['Descrip'].sample(n=5).to_list()
    return render_template("mainpage.html", weightlossfoods=weightlossfoods)

@app.route("/search", methods=['POST'])
def search():
    sort_by = request.form.get('sort_by', 'Descrip')
    rows = read_csv('done_food_data.csv', sort_by)
    return render_template('search.html', rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
