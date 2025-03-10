from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# ✅ Pydantic Model for Input Data
class MacroInput(BaseModel):
    weight: float  # In pounds
    height: float  # In inches
    age: int       # In years
    gender: str    # "male" or "female"
    activity_level: str  # Sedentary, Light, Moderate, Active, Very Active

# ✅ Activity Level Multipliers
activity_multipliers = {
    "sedentary": 1.2,  
    "light": 1.375,  
    "moderate": 1.55,  
    "active": 1.725,  
    "very_active": 1.9  
}

# ✅ Macro Calculation Route (No Login Required)
@app.post("/calculate_macros")
def calculate_macros(data: MacroInput):
    # 🏋️ RMR (Resting Metabolic Rate) Calculation (Mifflin-St Jeor Equation)
    if data.gender.lower() == "male":
        rmr = 66 + (6.23 * data.weight) + (12.7 * data.height) - (6.8 * data.age)
    elif data.gender.lower() == "female":
        rmr = 655 + (4.35 * data.weight) + (4.7 * data.height) - (4.7 * data.age)
    else:
        raise HTTPException(status_code=400, detail="Invalid gender. Choose 'male' or 'female'.")

    # 🏃 Total Daily Energy Expenditure (TDEE)
    if data.activity_level not in activity_multipliers:
        raise HTTPException(status_code=400, detail="Invalid activity level. Choose from: sedentary, light, moderate, active, very_active.")

    tdee = rmr * activity_multipliers[data.activity_level]

    # 🍽️ Macro Calculation (Protein, Carbs, Fats)
    def calculate_macros_for_goal(calories):
        protein = data.weight * 1.0
        carbs = (calories * 0.4) / 4  # 40% of calories from carbs
        fats = (calories * 0.3) / 9   # 30% of calories from fats
        return {
            "calories": round(calories),
            "protein": round(protein),
            "carbs": round(carbs),
            "fats": round(fats),
        }

    return {
        "cutting": calculate_macros_for_goal(tdee - 500),
        "maintaining": calculate_macros_for_goal(tdee),
        "bulking": calculate_macros_for_goal(tdee + 500),
    }
