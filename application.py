import joblib
import numpy as np
import os
import logging
from flask import Flask, render_template, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from config.paths_config import MODEL_OUTPUT_PATH

app = Flask(__name__)

# Load Model - this happens AFTER Docker build
try:
    logger.info(f"Loading model from: {MODEL_OUTPUT_PATH}")
    loaded_model = joblib.load(MODEL_OUTPUT_PATH)
    logger.info("Model loaded successfully!")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    loaded_model = None

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Cloud Run"""
    if loaded_model is not None:
        return {'status': 'healthy', 'model': 'loaded'}, 200
    return {'status': 'unhealthy', 'model': 'not_loaded'}, 503

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    error = None

    if request.method == 'POST':
        try:
            if loaded_model is None:
                raise Exception("Model not loaded. Please try again later.")

            lead_time = int(request.form['lead_time'])
            no_of_special_request = int(request.form['no_of_special_request'])
            avg_price_per_room = float(request.form['avg_price_per_room'])
            arrival_month = int(request.form['arrival_month'])
            arrival_date = int(request.form['arrival_date'])
            market_segment_type = int(request.form['market_segment_type'])
            no_of_week_nights = int(request.form['no_of_week_nights'])
            no_of_weekend_nights = int(request.form['no_of_weekend_nights'])
            type_of_meal_plan = int(request.form['type_of_meal_plan'])
            room_type_reserved = int(request.form['room_type_reserved'])

            features = np.array([[
                lead_time,
                no_of_special_request,
                avg_price_per_room,
                arrival_month,
                arrival_date,
                market_segment_type,
                no_of_week_nights,
                no_of_weekend_nights,
                type_of_meal_plan,
                room_type_reserved
            ]])

            prediction = loaded_model.predict(features)[0]
            logger.info(f"Prediction made: {prediction}")

        except Exception as e:
            error = f"Error occurred: {str(e)}"
            logger.error(error)

    return render_template('index.html', prediction=prediction, error=error)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    # Use gunicorn in production, Flask dev server for local testing
    if os.environ.get('FLASK_ENV') == 'development':
        app.run(debug=False, host='0.0.0.0', port=port)
    else:
        # This won't run in production because CMD uses gunicorn
        app.run(debug=False, host='0.0.0.0', port=port)
