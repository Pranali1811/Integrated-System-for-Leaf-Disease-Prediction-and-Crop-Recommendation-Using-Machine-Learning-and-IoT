from keras.models import load_model
from PIL import Image
import numpy as np
from keras.preprocessing.image import img_to_array
import joblib
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


# Terminal app
def leaf_disease_prediction():
    # Prompt the user to upload an image
    image_path = input("Enter the path of the image file (JPG format) for disease detection: ")
    
    if os.path.exists(image_path):
        image = Image.open(image_path)
        img = preprocess_image(image)

        # Make prediction
        try:
            prediction = model.predict(img)
            predicted_class = np.argmax(prediction, axis=1)[0]
            print(f'Predicted Disease: {class_names[predicted_class]}')
        except Exception as e:
            print(f"Error during prediction: {e}")
    else:
        print("Invalid image path.")


def crop_recommendation():
    print("Enter the features to recommend a crop:")
    
    try:
        nitrogen = float(input('Nitrogen: '))
        phosphorus = float(input('Phosphorus: '))
        potassium = float(input('Potassium: '))
        temperature = float(input('Temperature: '))
        humidity = float(input('Humidity: '))
        pH_value = float(input('pH Value: '))
        rainfall = float(input('Rainfall: '))

        features = [nitrogen, phosphorus, potassium, temperature, humidity, pH_value, rainfall]
        recommended_crop = recommend_crop(features)
        print(f'The recommended crop is: {recommended_crop}')
    except Exception as e:
        print(f"Error during recommendation: {e}")


# Main menu
def main():
    while True:
        print("\nOptions:")
        print("1. Leaf Disease Prediction")
        print("2. Crop Recommendation")
        print("3. Exit")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            leaf_disease_prediction()
        elif choice == '2':
            crop_recommendation()
        elif choice == '3':
            print("Exiting the application.")
            break
        else:
            print("Invalid option. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
