import streamlit as st
import numpy as np
import pandas as pd

class MacroCalculator:
    def __init__(self, weight, bf_percent, goal, activity_level=1.2):
        self.weight = weight
        self.bf_percent = bf_percent
        self.lean_mass = self.calculate_lean_mass()
        self.bmr = self.calculate_bmr()
        self.tdee = self.bmr * activity_level
        self.goal = goal.lower()
        self.daily_weights = []

        self.adjust_calories()
        self.calculate_macros()

    def calculate_lean_mass(self):
        return self.weight * (1 - (self.bf_percent / 100))

    def calculate_bmr(self):
        return 370 + (21.6 * self.lean_mass)

    def adjust_calories(self):
        if self.goal == "cut":
            self.calories = self.tdee - 500
        elif self.goal == "bulk":
            self.calories = self.tdee + 300
        else:
            self.calories = self.tdee

    def calculate_macros(self):
        self.protein = self.lean_mass * 1.0  
        self.fat = self.weight * 0.3
        remaining_calories = self.calories - (self.protein * 4 + self.fat * 9)
        self.carbs = remaining_calories / 4

    def update_weight(self, new_weight):
        self.daily_weights.append(new_weight)
        self.weight = new_weight
        self.lean_mass = self.calculate_lean_mass()
        self.bmr = self.calculate_bmr()
        self.tdee = self.bmr * 1.2
        self.adjust_calories()
        self.calculate_macros()

    def get_macros(self):
        return {
            "Calories": round(self.calories),
            "Protein (g)": round(self.protein),
            "Fats (g)": round(self.fat),
            "Carbs (g)": round(self.carbs),
        }

# Streamlit App
st.title("Macro Calculator")

weight = st.number_input("Enter your weight (lbs)", min_value=50.0, max_value=500.0, step=1.0)
bf_percent = st.number_input("Enter your body fat percentage", min_value=1.0, max_value=60.0, step=0.5)
goal = st.selectbox("Select your goal", ["Cut", "Maintain", "Bulk"])

if st.button("Calculate Macros"):
    calculator = MacroCalculator(weight, bf_percent, goal)
    macros = calculator.get_macros()
    st.write(f"### Recommended Daily Macros:")
    st.write(f"**Calories:** {macros['Calories']}")
    st.write(f"**Protein:** {macros['Protein (g)']}g")
    st.write(f"**Fats:** {macros['Fats (g)']}g")
    st.write(f"**Carbs:** {macros['Carbs (g)']}g")

# Weight Tracking
new_weight = st.number_input("Enter today's weight (optional)", min_value=50.0, max_value=500.0, step=0.1)
if st.button("Update Weight"):
    calculator.update_weight(new_weight)
    st.write("Weight updated! Recalculated Macros:")
    st.write(calculator.get_macros())
