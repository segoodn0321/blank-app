import pandas as pd
import numpy as np

class MacroCalculator:
    def __init__(self, weight, bf_percent, goal, activity_level=1.2):
        """
        Initializes the macro calculator with user details.
        weight: User's weight in lbs
        bf_percent: Body fat percentage
        goal: "cut", "maintain", or "bulk"
        activity_level: Multiplier for total daily energy expenditure (TDEE)
        """
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
        """Calculates lean body mass (LBM)."""
        return self.weight * (1 - (self.bf_percent / 100))

    def calculate_bmr(self):
        """Calculates Basal Metabolic Rate (BMR) using the Katch-McArdle formula."""
        return 370 + (21.6 * self.lean_mass)

    def adjust_calories(self):
        """Adjusts calories based on the goal (cut, maintain, bulk)."""
        if self.goal == "cut":
            self.calories = self.tdee - 500  # 500 kcal deficit for fat loss
        elif self.goal == "bulk":
            self.calories = self.tdee + 300  # 300 kcal surplus for muscle gain
        else:
            self.calories = self.tdee  # Maintenance

    def calculate_macros(self):
        """Calculates macronutrient distribution based on goal."""
        # Protein: 1g per lb of lean mass
        self.protein = self.lean_mass * 1.0  
        self.fat = self.weight * 0.3  # Fat: 0.3g per lb of body weight
        remaining_calories = self.calories - (self.protein * 4 + self.fat * 9)
        self.carbs = remaining_calories / 4  # Remaining calories to carbs

    def update_weight(self, new_weight):
        """Updates weight, recalculates lean mass, BMR, TDEE, and macros."""
        self.daily_weights.append(new_weight)
        self.weight = new_weight
        self.lean_mass = self.calculate_lean_mass()
        self.bmr = self.calculate_bmr()
        self.tdee = self.bmr * 1.2  # Keeping activity level fixed at 1.2 for now
        self.adjust_calories()
        self.calculate_macros()

    def get_macros(self):
        """Returns the current macro distribution."""
        return {
            "Calories": round(self.calories),
            "Protein (g)": round(self.protein),
            "Fats (g)": round(self.fat),
            "Carbs (g)": round(self.carbs),
        }

    def get_weight_trend(self):
        """Analyzes weight trend over time (basic moving average)."""
        if len(self.daily_weights) < 5:
            return "Not enough data for trend analysis."
        avg_weight_change = np.mean(np.diff(self.daily_weights))
        if avg_weight_change < -0.2:
            return "Losing weight."
        elif avg_weight_change > 0.2:
            return "Gaining weight."
        else:
            return "Stable weight."

# Example Usage
if __name__ == "__main__":
    weight = float(input("Enter your weight (lbs): "))
    bf_percent = float(input("Enter your body fat percentage: "))
    goal = input("Enter your goal (cut/maintain/bulk): ")

    user = MacroCalculator(weight, bf_percent, goal)

    print("\nYour Initial Macros:")
    print(user.get_macros())

    while True:
        update = input("\nEnter new weight (or type 'exit' to stop): ")
        if update.lower() == "exit":
            break
        user.update_weight(float(update))
        print("Updated Macros:", user.get_macros())
        print("Weight Trend:", user.get_weight_trend())
