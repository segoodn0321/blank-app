import streamlit as st

class MacroCalculator:
    def __init__(self, weight, height, age, goal, activity_level=1.2):
        """
        Initializes the macro calculator.
        :param weight: User's weight in lbs
        :param height: User's height in inches
        :param age: User's age in years
        :param goal: "cut", "maintain", or "bulk"
        :param activity_level: Activity multiplier for calorie calculation
        """
        self.weight = weight
        self.height = height
        self.age = age
        self.goal = goal.lower()
        self.daily_weights = []

        # Convert weight (lbs) to kg and height (inches) to cm
        weight_kg = self.weight * 0.453592
        height_cm = self.height * 2.54

        # Calculate Resting Metabolic Rate (RMR) using Mifflin-St Jeor Equation
        self.rmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * self.age) + 5

        self.adjust_calories()
        self.calculate_macros()

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
        """Updates weight and recalculates RMR and macros."""
        self.daily_weights.append(new_weight)
        self.weight = new_weight

        weight_kg = self.weight * 0.453592
        height_cm = self.height * 2.54

        # Recalculate RMR with updated weight
        self.rmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * self.age) + 5

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
height = st.number_input("Enter your height (inches)", min_value=48.0, max_value=84.0, step=1.0)
age = st.number_input("Enter your age", min_value=15, max_value=80, step=1)
goal = st.selectbox("Select your goal", ["Cut", "Maintain", "Bulk"])

if st.button("Calculate Macros"):
    calculator = MacroCalculator(weight, height, age, goal)
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
