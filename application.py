import joblib
import numpy as np
import os
import logging
import sys
from flask import Flask, render_template, request, jsonify

# Configure logging - logs to stdout for Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

from config.paths_config import MODEL_OUTPUT_PATH

app = Flask(__name__)

# Global model variable
loaded_model = None
model_load_error = None

def load_model():
    """Load model on startup"""
    global loaded_model, model_load_error
    try:
        logger.info(f"Loading model from: {MODEL_OUTPUT_PATH}")
        if not os.path.exists(MODEL_OUTPUT_PATH):
            raise FileNotFoundError(f"Model file not found: {MODEL_OUTPUT_PATH}")
        
        loaded_model = joblib.load(MODEL_OUTPUT_PATH)
        logger.info("✓ Model loaded successfully!")
        return True
    except Exception as e:
        error_msg = f"✗ Failed to load model: {str(e)}"
        logger.error(error_msg)
        model_load_error = error_msg
        return False

# Load model when app starts
logger.info("=== Application Starting ===")
logger.info(f"PORT: {os.environ.get('PORT', 8080)}")
logger.info(f"MODEL_OUTPUT_PATH: {MODEL_OUTPUT_PATH}")
model_loaded_successfully = load_model()

@app.route('/health', methods=['GET'])
def health():
    """Cloud Run health check endpoint"""
    try:
        if loaded_model is not None:
            logger.debug("Health check: OK - model loaded")
            return jsonify({'status': 'healthy', 'model': 'loaded', 'ready': True}), 200
        else:
            logger.warning("Health check: WARN - model not loaded yet")
            return jsonify({
                'status': 'starting',
                'model': 'loading',
                'error': model_load_error,
                'ready': False
            }), 503
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main prediction endpoint"""
    prediction = None
    error = None

    if request.method == 'POST':
        try:
            if loaded_model is None:
                raise Exception(f"Model not ready. Error: {model_load_error}")

            # Parse form inputs
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

            prediction = int(loaded_model.predict(features)[0])
            logger.info(f"✓ Prediction made: {prediction}")

        except KeyError as e:
            error = f"Missing form field: {str(e)}"
            logger.error(error)
        except ValueError as e:
            error = f"Invalid input value: {str(e)}"
            logger.error(error)
        except Exception as e:
            error = f"Prediction error: {str(e)}"
            logger.error(error)

    return render_template('index.html', prediction=prediction, error=error)

@app.route('/ready', methods=['GET'])
def ready():
    """Readiness probe - for Kubernetes/Cloud Run startup checks"""
    if loaded_model is not None:
        return jsonify({'ready': True, 'message': 'Application is ready'}), 200
    else:
        return jsonify({'ready': False, 'message': 'Application is starting...'}), 503

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 - Not found: {request.path}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"500 - Server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting Flask app on port {port}")
    
    # Use development server only if explicitly set
    if os.environ.get('FLASK_ENV') == 'development':
        logger.warning("Running in DEVELOPMENT mode!")
        app.run(debug=False, host='0.0.0.0', port=port)
    else:
        # In production, Dockerfile uses Gunicorn via CMD
        logger.info("Production mode - use Gunicorn (defined in Dockerfile)")
        app.run(debug=False, host='0.0.0.0', port=port)
