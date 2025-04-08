from flask import Flask, render_template, request
import pickle
import pandas as pd
import csv
import os

app = Flask(__name__)

# Load ML model
model = None
try:
    with open('food_model.pickle', 'rb') as file:
        model = pickle.load(file)
except FileNotFoundError:
    print("❌ Error: 'food_model.pickle' file not found.")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# Load dataset
food_data = pd.DataFrame()
try:
    food_data = pd.read_csv('done_food_data.csv')
except FileNotFoundError:
    print("❌ Error: 'done_food_data.csv' file not found.")
except Exception as e:
    print(f"❌ Error loading food data: {e}")

# Utility to read and sort CSV
def read_csv(file_path, sort_by='Descrip'):
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = [row for row in reader]
            sorted_rows = sorted(rows, key=lambda x: x[sort_by])
            return sorted_rows
    except Exception as e:
        print(f"CSV read error: {e}")
        return []

@app.route("/")
def index():
    return render_template("mainpage.html")

@app.route("/predict", methods=['POST'])
def predict():
    if model is None:
        return "Model not loaded. Please check the server logs.", 500

    try:
        input_1 = float(request.form['input_1'])
        input_2 = float(request.form['input_2'])
        input_3 = float(request.form['input_3'])

        inputs = [[input_1, input_2, input_3]]
        prediction = model.predict(inputs)

        category_map = {
            'Muscle_Gain': 'Muscle Gain',
            'Weight_Gain': 'Weight Gain',
            'Weight_Loss': 'Weight Loss'
        }
        result = category_map.get(prediction[0], 'General food')
    except Exception as e:
        result = f"Error in prediction: {e}"

    return render_template("mainpage.html", result=result)

# Helper function to filter data
def filter_food_data(data, vegetarian, iron, calcium):
    if 'iron' in iron:
        data = data[data['Iron_mg'] > 6]
    if 'calcium' in calcium:
        data = data[data['Calcium_mg'] > 150]
    if 'vegetarian' in vegetarian:
        exclude_keywords = ['Egg', 'Fish', 'meat', 'beef', 'Chicken', 'Beef', 'Deer', 'lamb',
                            'crab', 'pork', 'turkey', 'flesh', 'Frog legs', 'Pork', 'Turkey',
                            'Ostrich', 'Emu', 'cuttelfish', 'Seaweed', 'crayfish', 'shrimp', 'Octopus']
        data = data[~data['Descrip'].str.contains('|'.join(exclude_keywords), case=False)]
    return data

@app.route("/musclegain", methods=['POST'])
def musclegain():
    if food_data.empty:
        return "Data not available. Please check the server logs.", 500

    vegetarian = request.form.getlist('vegetarian')
    iron = request.form.getlist('iron')
    calcium = request.form.getlist('calcium')

    muscle_gain_data = food_data[food_data['category'] == 'Muscle_Gain']
    muscle_gain_data = filter_food_data(muscle_gain_data, vegetarian, iron, calcium)

    sample_size = min(5, len(muscle_gain_data))
    musclegainfoods = muscle_gain_data['Descrip'].sample(n=sample_size).to_list()

    return render_template("mainpage.html", musclegainfoods=musclegainfoods)

@app.route("/weightgain", methods=['POST'])
def weightgain():
    if food_data.empty:
        return "Data not available. Please check the server logs.", 500

    vegetarian = request.form.getlist('vegetarian')
    iron = request.form.getlist('iron')
    calcium = request.form.getlist('calcium')

    weight_gain_data = food_data[food_data['category'] == 'Weight_Gain']
    weight_gain_data = filter_food_data(weight_gain_data, vegetarian, iron, calcium)

    sample_size = min(5, len(weight_gain_data))
    weightgainfoods = weight_gain_data['Descrip'].sample(n=sample_size).to_list()

    return render_template("mainpage.html", weightgainfoods=weightgainfoods)

@app.route("/weightloss", methods=['POST'])
def weightloss():
    if food_data.empty:
        return "Data not available. Please check the server logs.", 500

    vegetarian = request.form.getlist('vegetarian')
    iron = request.form.getlist('iron')
    calcium = request.form.getlist('calcium')

    weight_loss_data = food_data[food_data['category'] == 'Weight_Loss']
    weight_loss_data = filter_food_data(weight_loss_data, vegetarian, iron, calcium)

    sample_size = min(5, len(weight_loss_data))
    weightlossfoods = weight_loss_data['Descrip'].sample(n=sample_size).to_list()

    return render_template("mainpage.html", weightlossfoods=weightlossfoods)

@app.route("/search", methods=['POST'])
def search():
    rows = read_csv('done_food_data.csv', request.form.get('sort_by', 'Descrip'))
    return render_template('search.html', rows=rows)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
