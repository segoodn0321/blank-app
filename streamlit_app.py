import streamlit as st
import numpy as np
import pandas as pd

class MacroCalculator:
    def __init__(self, weight, bf_percent, goal, activity_level=1.2):
        self.weight = weight
        self.bf_percent = bf_percent
        self.lean_mass = self.calculate_lean_mass()
        self.rmr = self.calculate_rmr()  # Using RMR instead of TDEE
        self.goal = goal.lower()
        self.daily_weights = []

        self.adjust_calories()
        self.calculate_macros()

    def calculate_lean_mass(self):
        """Calculates lean body mass (LBM)."""
        return self.weight * (1 - (self.bf_percent / 100))

    def calculate_rmr(self):
        """Calculates Resting Metabolic Rate (RMR) using the Katch-McArdle formula."""
        return 370 + (21.6 * self.lean_mass)

    def adjust_calories(self):
        """Adjusts calories based on the goal (cut, maintain, bulk)."""
        if self.goal == "cut":
            self.calories = self.rmr - 500  # 500 kcal deficit
        elif self.goal == "bulk":
            self.calories = self.rmr + 300  # 300 kcal surplus
        else:
            self.calories = self.rmr  # Maintenance

    def calculate_macros(self):
        """Calculates macros using 40% protein, 30% carbs, 30% fat split."""
        self.protein = (0.40 * self.calories) / 4  # Protein: 40% of total calories (4 kcal/g)
        self.carbs = (0.30 * self.calories) / 4    # Carbs: 30% of total calories (4 kcal/g)
        self.fat = (0.30 * self.calories) / 9      # Fat: 30% of total calories (9 kcal/g)

    def update_weight(self, new_weight):
        """Updates weight, recalculates lean mass, RMR, and macros."""
        self.daily_weights.append(new_weight)
        self.weight = new_weight
        self.lean_mass = self.calculate_lean_mass()
        self.rmr = self.calculate_rmr()
        self.adjust_calories()
        self.calculate_macros()

    def get_macros(self):
        """Returns the current macro distribution."""
        return {
            "Calories": round(self.calories),
            "Protein (g)": round(self.protein),
            "Carbs (g)": round(self.carbs),
            "Fats (g)": round(self.fat),
        }

# Streamlit App
st.title("Macro Calculator (Cutting Focus)")

weight = st.number_input("Enter your weight (lbs)", min_value=50.0, max_value=500.0, step=1.0)
bf_percent = st.number_input("Enter your body fat percentage", min_value=1.0, max_value=60.0, step=0.5)
goal = st.selectbox("Select your goal", ["Cut", "Maintain", "Bulk"])

if st.button("Calculate Macros"):
    calculator = MacroCalculator(weight, bf_percent, goal)
    macros = calculator.get_macros()
    st.write(f"### Recommended Daily Macros:")
    st.write(f"**Calories:** {macros['Calories']}")
    st.write(f"**Protein:** {macros['Protein (g)']}g")
    st.write(f"**Carbs:** {macros['Carbs (g)']}g")
    st.write(f"**Fats:** {macros['Fats (g)']}g")

# Weight Tracking
new_weight = st.number_input("Enter today's weight (optional)", min_value=50.0, max_value=500.0, step=0.1)
if st.button("Update Weight"):
    calculator.update_weight(new_weight)
    st.write("Weight updated! Recalculated Macros:")
    st.write(calculator.get_macros())
