from flask import Flask, render_template, request
import os
import numpy as np
import pickle
import cv2
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import uuid

# Constants
UPLOAD_FOLDER = 'static/uploads'
BRAIN_MODEL_PATH = 'brain_tumor_detection_model.keras'

# Initialize Flask app
app = Flask(__name__)

# Load the model
brain_model = load_model(BRAIN_MODEL_PATH)

# Function to save the uploaded file with a unique filename
def save_uploaded_file(file):
    """Saves the uploaded file with a unique filename."""
    unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[-1]
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)
    return file_path

# Function to preprocess the image
def preprocess_image(file_path):
    """Loads and processes the image for prediction."""
    img = load_img(file_path, target_size=(150, 150))
    img_array = img_to_array(img) / 255.0  # Normalize pixel values
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

# Function to make predictions using the brain tumor model
def predict_brain_tumor(img_array):
    """Performs prediction using the brain tumor model."""
    prediction = brain_model.predict(img_array)[0][0]
    accuracy = round(prediction * 100, 2) if prediction > 0.5 else round((1 - prediction) * 100, 2)
    damage_percentage = round((1 - prediction) * 100, 2) if prediction > 0.5 else round(prediction * 100, 2)
    health_status = "Affected" if prediction > 0.5 else "Healthy"

    recommendations = [
        "Consult a neurologist for further evaluation.",
        "Maintain a healthy diet and lifestyle.",
        "Avoid stress and get adequate sleep."
    ]
    
    precautions = [
        "Avoid smoking and alcohol consumption.",
        "Follow up with regular medical checkups.",
        "Take prescribed medications as directed."
    ]

    return {
        "accuracy": accuracy,
        "damage_percentage": damage_percentage,
        "health_status": health_status,
        "recommendations": recommendations,
        "precautions": precautions,
        "message": "Yes" if prediction > 0.5 else "No"
    }

# Flask routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_image():
    if 'file' not in request.files:
        return render_template('index.html', prediction='No file found')

    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', prediction='No file selected')

    try:
        # Save the uploaded file and get its path
        file_path = save_uploaded_file(file)
        
        # Preprocess the image
        img_array = preprocess_image(file_path)
        
        # Make prediction using the brain tumor detection model
        result = predict_brain_tumor(img_array)
        
        # Display the result
        message = result["message"]
        
        
        return render_template('index.html', 
                               prediction=f'{message}')

    except Exception as e:
        return render_template('index.html', prediction=f'Error occurred: {e}')

if __name__ == '__main__':
    app.run(debug=True)
