import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import matplotlib.pyplot as plt

# Database Setup
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    password TEXT,
    weight REAL,
    height REAL,
    age INTEGER,
    goal TEXT,
    activity_level REAL
)
""")
conn.commit()

# Create weight history table
cursor.execute("""
CREATE TABLE IF NOT EXISTS weight_history (
    user_id TEXT,
    date TEXT,
    weight REAL,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
)
""")
conn.commit()

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to register a new user
def register_user(user_id, password, weight, height, age, goal, activity_level):
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (user_id, hashed_password, weight, height, age, goal, activity_level))
    conn.commit()

# Function to authenticate user
def authenticate_user(user_id, password):
    cursor.execute("SELECT password FROM users WHERE user_id=?", (user_id,))
    stored_password = cursor.fetchone()
    if stored_password and stored_password[0] == hash_password(password):
        return True
    return False

# Function to save weight history
def save_weight_history(user_id, weight):
    cursor.execute("INSERT INTO weight_history (user_id, date, weight) VALUES (?, DATE('now'), ?)", (user_id, weight))
    conn.commit()

# Function to get user data
def get_user_data(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

# Function to get weight history
def get_weight_history(user_id):
    cursor.execute("SELECT date, weight FROM weight_history WHERE user_id=?", (user_id,))
    return cursor.fetchall()

# Streamlit App
st.title("Macro Calculator with User Registration & Login")

# Login or Register
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

if menu == "Register":
    st.subheader("Create an Account")
    new_user = st.text_input("Username or Email")
    new_pass = st.text_input("Password", type="password")
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

    if st.button("Register"):
        try:
            register_user(new_user, new_pass, weight, height, age, goal, activity_level)
            st.success("Account created successfully! Please log in.")
        except:
            st.error("Username already exists. Try a different one.")

elif menu == "Login":
    st.subheader("Login to Your Account")
    user_id = st.text_input("Username or Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate_user(user_id, password):
            st.session_state["user_id"] = user_id  # Store user session
            st.success(f"Welcome {user_id}!")
        else:
            st.error("Invalid username or password.")

# If logged in, show Macro Calculator
if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]
    user_data = get_user_data(user_id)

    if user_data:
        _, _, weight, height, age, goal, activity_level = user_data
        st.subheader("Macro Calculation & Tracking")
        
        if st.button("Recalculate Macros"):
            weight_kg = weight * 0.453592
            height_cm = height * 2.54
            rmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
            tdee = rmr * activity_level

            calories = tdee - 500 if goal == "Cut" else tdee + 300 if goal == "Bulk" else tdee
            protein = (0.40 * calories) / 4
            carbs = (0.30 * calories) / 4
            fats = (0.30 * calories) / 9

            st.write(f"### Recommended Daily Macros:")
            st.write(f"**TDEE:** {round(tdee)} kcal")
            st.write(f"**Calories (Adjusted for Goal):** {round(calories)} kcal")
            st.write(f"**Protein:** {round(protein)}g")
            st.write(f"**Carbs:** {round(carbs)}g")
            st.write(f"**Fats:** {round(fats)}g")

        # Weight tracking
        new_weight = st.number_input("Enter today's weight", min_value=50.0, max_value=500.0, step=0.1)
        if st.button("Save Weight Entry"):
            save_weight_history(user_id, new_weight)
            st.success("Weight entry saved!")

        # Show weight history
        if st.button("View Weight History"):
            history = get_weight_history(user_id)
            if history:
                df = pd.DataFrame(history, columns=["Date", "Weight"])
                st.write(df)

                # Plot weight trend
                df["Date"] = pd.to_datetime(df["Date"])
                fig, ax = plt.subplots()
                ax.plot(df["Date"], df["Weight"], marker="o", linestyle="-", color="blue")
                ax.set_title("Weight Trend Over Time")
                ax.set_xlabel("Date")
                ax.set_ylabel("Weight (lbs)")
                ax.grid(True)
                st.pyplot(fig)
            else:
                st.write("No weight history found.")
                
