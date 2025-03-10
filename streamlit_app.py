import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

class MacroCalculator:
    def __init__(self, user_id, weight, height, age, activity_level, goal):
        """
        Initializes the macro calculator.
        :param user_id: Unique identifier for each user
        :param weight: User's weight in lbs
        :param height: User's height in inches
        :param age: User's age in years
        :param activity_level: User's selected activity multiplier
        :param goal: "cut", "maintain", or "bulk"
        """
        self.user_id = user_id
        self.weight = weight
        self.height = height
        self.age = age
        self.activity_level = activity_level
        self.goal = goal.lower()

        # Convert weight (lbs) to kg and height (inches) to cm
        weight_kg = self.weight * 0.453592
        height_cm = self.height * 2.54

        # Calculate Resting Metabolic Rate (RMR)
        self.rmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * self.age) + 5

        # Convert RMR to TDEE using activity level
        self.tdee = self.rmr * self.activity_level

        self.adjust_calories()
        self.calculate_macros()
        self.save_weight_history()

    def adjust_calories(self):
        """Adjusts calories based on the goal (cut, maintain, bulk)."""
        if self.goal == "cut":
            self.calories = self.tdee - 500  # 500 kcal deficit
        elif self.goal == "bulk":
            self.calories = self.tdee + 300  # 300 kcal surplus
        else:
            self.calories = self.tdee  # Maintenance

    def calculate_macros(self):
        """Calculates macros using 40% protein, 30% carbs, 30% fat split."""
        self.protein = (0.40 * self.calories) / 4  # Protein: 40% of total calories (4 kcal/g)
        self.carbs = (0.30 * self.calories) / 4    # Carbs: 30% of total calories (4 kcal/g)
        self.fat = (0.30 * self.calories) / 9      # Fat: 30% of total calories (9 kcal/g)

    def get_macros(self):
        """Returns the current macro distribution."""
        return {
            "TDEE (Adjusted Calories)": round(self.tdee),
            "Calories (Adjusted for Goal)": round(self.calories),
            "Protein (g)": round(self.protein),
            "Carbs (g)": round(self.carbs),
            "Fats (g)": round(self.fat),
        }

    def save_weight_history(self):
        """Save weight history to a CSV file for tracking trends."""
        file_name = f"{self.user_id}_weight_history.csv"

        # Load existing weight history if the file exists
        if os.path.exists(file_name):
            df = pd.read_csv(file_name)
        else:
            df = pd.DataFrame(columns=["Date", "Weight"])

        # Add new entry
        new_data = pd.DataFrame({"Date": [pd.Timestamp.today().date()], "Weight": [self.weight]})
        df = pd.concat([df, new_data], ignore_index=True)

        # Save updated file
        df.to_csv(file_name, index=False)

    def load_weight_history(self):
        """Load historical weight data for trend analysis."""
        file_name = f"{self.user_id}_weight_history.csv"
        if os.path.exists(file_name):
            return pd.read_csv(file_name)
        else:
            return pd.DataFrame(columns=["Date", "Weight"])


# Streamlit App
st.title("Macro Calculator with Weight Tracking")

# User ID input (for unique tracking)
user_id = st.text_input("Enter your User ID (e.g., email or username)")

if user_id:
    weight = st.number_input("Enter your weight (lbs)", min_value=50.0, max_value=500.0, step=1.0)
    height = st.number_input("Enter your height (inches)", min_value=48.0, max_value=84.0, step=1.0)
    age = st.number_input("Enter your age", min_value=15, max_value=80, step=1)
    goal = st.selectbox("Select your goal", ["Cut", "Maintain", "Bulk"])

    # Activity Level Selection
    activity_options = {
        "Sedentary (little to no exercise)": 1.2,
        "Lightly Active (1-3 days/week)": 1.375,
        "Moderately Active (3-5 days/week)": 1.55,
        "Very Active (6-7 days/week)": 1.725,
        "Super Active (intense daily exercise)": 1.9
    }
    activity_selection = st.selectbox("Select your activity level", list(activity_options.keys()))
    activity_level = activity_options[activity_selection]

    if st.button("Calculate Macros"):
        calculator = MacroCalculator(user_id, weight, height, age, activity_level, goal)
        macros = calculator.get_macros()

        st.write(f"### Recommended Daily Macros:")
        st.write(f"**TDEE (Total Calories Burned Per Day):** {macros['TDEE (Adjusted Calories)']}")
        st.write(f"**Adjusted Calories for Goal:** {macros['Calories (Adjusted for Goal)']}")
        st.write(f"**Protein:** {macros['Protein (g)']}g")
        st.write(f"**Carbs:** {macros['Carbs (g)']}g")
        st.write(f"**Fats:** {macros['Fats (g)']}g")

    # Show weight history & plot graph
    if st.button("View Weight History"):
        calculator = MacroCalculator(user_id, weight, height, age, activity_level, goal)
        weight_data = calculator.load_weight_history()

        if not weight_data.empty:
            st.write(weight_data)

            # Convert Date column to datetime for plotting
            weight_data["Date"] = pd.to_datetime(weight_data["Date"])

            # Plot weight trend graph
            fig, ax = plt.subplots()
            ax.plot(weight_data["Date"], weight_data["Weight"], marker="o", linestyle="-", color="blue")
            ax.set_title("Weight Trend Over Time")
            ax.set_xlabel("Date")
            ax.set_ylabel("Weight (lbs)")
            ax.grid(True)
            st.pyplot(fig)
        else:
            st.write("No weight history found.")
