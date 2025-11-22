import streamlit as st
from keras.models import load_model
from PIL import Image
import numpy as np
from keras.preprocessing.image import img_to_array
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
import joblib
import json
import os

# Load the trained leaf disease model
model = load_model('Leaf_Disease/Leaf-Diseade-Prediction.h5')  # Replace with your model file

# Define the class names for leaf disease (adjust accordingly)
class_names = ['Healthy', 'Early Blight', 'Late Blight']  # Adjust according to your model's classes

# Load crop recommendation model and scaler
knn_loaded = joblib.load('Crop-Recomedation/knn_crop_recommender.pkl')
scaler_loaded = joblib.load('Crop-Recomedation/scaler.pkl')

# Define crop labels corresponding to numeric values
crop_labels = [
    'Rice', 'Maize', 'ChickPea', 'KidneyBeans', 'PigeonPeas', 'MothBeans',
    'MungBean', 'Blackgram', 'Lentil', 'Pomegranate', 'Banana', 'Mango',
    'Grapes', 'Watermelon', 'Muskmelon', 'Apple', 'Orange', 'Papaya',
    'Coconut', 'Cotton', 'Jute', 'Coffee'
]

# Function to preprocess the image
def preprocess_image(image):
    img = image.resize((256, 256))  # Resize to match model's expected input size
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    img = img / 255.0  # Normalize pixel values
    return img

# Function for crop recommendation
def recommend_crop(features):
    features_scaled = scaler_loaded.transform([features])
    prediction = knn_loaded.predict(features_scaled)
    
    # Ensure the prediction is within the valid range
    if prediction[0] < len(crop_labels):
        return crop_labels[prediction[0]]
    else:
        return "Unknown Crop"  # Fallback in case of an out-of-range index


# Streamlit app
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", ["Leaf Disease Prediction", "Crop Recommendation"])

if selection == "Leaf Disease Prediction":
    st.title('Plant Disease Detection')
    st.write("Upload an image to check for plant diseases")

    # Upload image
    uploaded_file = st.file_uploader("Choose an image...", type="jpg")

    if uploaded_file is not None:
        # Open and display the image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        st.write("")
        st.write("Classifying...")

        # Preprocess the image
        img = preprocess_image(image)

        # Make prediction
        try:
            prediction = model.predict(img)
            predicted_class = np.argmax(prediction, axis=1)[0]

            # Display the result
            st.write(f'Predicted Disease: **{class_names[predicted_class]}**')
        except Exception as e:
            st.error(f"Error during prediction: {e}")
elif selection == "Crop Recommendation":
    st.title('Crop Recommendation System')
    st.write("Fetch sensor data and enter rainfall to get crop recommendation")

    if os.path.exists("shared_sensor_data.json"):
        try:
            with open("shared_sensor_data.json", "r") as f:
                sensor = json.load(f)

            st.success("Sensor data loaded successfully!")

            # Display fetched sensor values
            st.subheader("Fetched Sensor Values")
            st.json(sensor)

            # Manually enter rainfall value
            st.subheader("Enter Rainfall")
            rainfall_input = st.number_input("Rainfall (mm)", min_value=0.0, step=1.0, value=0.0)

            if st.button("Recommend Crop"):
                features = [
                    sensor["nitrogen"],
                    sensor["phosphorus"],
                    sensor["potassium"],
                    sensor["temperature"],
                    sensor["humidity"],
                    sensor["ph"],
                    rainfall_input  # Manual rainfall input
                ]

                recommended_crop = recommend_crop(features)
                st.success(f"The recommended crop is: **{recommended_crop}**")

                # Display final input data used
                st.subheader("Data Used for Recommendation")
                st.json({**sensor, "rainfall": rainfall_input})

        except Exception as e:
            st.error(f"Failed to load or process sensor data: {e}")
    else:
        st.warning("Sensor data not available. Please ensure the MQTT dashboard is running.")
