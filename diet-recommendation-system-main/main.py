import streamlit as st
import pickle
import pandas as pd
import random

# Load model
model = None
try:
    with open('food_model.pickle', 'rb') as file:
        model = pickle.load(file)
except Exception as e:
    st.error("Model could not be loaded. Please check the file and try again.")

# Load data
food_data = pd.DataFrame()
try:
    food_data = pd.read_csv('done_food_data.csv')
except Exception as e:
    st.error("Data file could not be loaded. Please check the file and try again.")

# Title
st.title("🍽️ Personalized Diet Recommendation System")

st.header("🔮 Predict Your Goal")
input_1 = st.number_input("Enter Feature 1", min_value=0.0)
input_2 = st.number_input("Enter Feature 2", min_value=0.0)
input_3 = st.number_input("Enter Feature 3", min_value=0.0)

if st.button("Predict Goal"):
    if model is not None:
        prediction = model.predict([[input_1, input_2, input_3]])[0]
        goal = {
            'Muscle_Gain': '💪 Muscle Gain',
            'Weight_Gain': '📈 Weight Gain',
            'Weight_Loss': '📉 Weight Loss'
        }.get(prediction, '🍽️ General')
        st.success(f"Recommended goal: {goal}")
    else:
        st.error("Model not available.")

# Filters
st.header("🥗 Filter Your Food Plan")
goal_option = st.selectbox("Choose your goal", ["Muscle_Gain", "Weight_Gain", "Weight_Loss"])
vegetarian = st.checkbox("Vegetarian Only")
filter_iron = st.checkbox("High in Iron")
filter_calcium = st.checkbox("High in Calcium")

if st.button("Show Food Recommendations"):
    if food_data.empty:
        st.error("Food data is not available.")
    else:
        df = food_data[food_data['category'] == goal_option]

        if filter_iron:
            df = df[df['Iron_mg'] > 6]
        if filter_calcium:
            df = df[df['Calcium_mg'] > 150]
        if vegetarian:
            exclude = ['Egg','Fish','meat','beef','Chicken','Beef','Deer','lamb','crab',
                       'pork','turkey','flesh','Ostrich','Emu','Seaweed','shrimp','Octopus']
            df = df[~df['Descrip'].str.contains('|'.join(exclude), case=False, na=False)]

        if df.empty:
            st.warning("No matching foods found.")
        else:
            foods = df['Descrip'].sample(n=min(5, len(df))).to_list()
            st.subheader("🍛 Recommended Foods:")
            for food in foods:
                st.write(f"• {food}")
