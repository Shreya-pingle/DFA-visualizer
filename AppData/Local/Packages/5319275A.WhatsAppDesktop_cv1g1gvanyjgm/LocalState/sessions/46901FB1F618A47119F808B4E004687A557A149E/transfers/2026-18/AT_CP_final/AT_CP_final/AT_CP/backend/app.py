"""
Flask REST API Server - DFA Animation Web Application
======================================================
This module creates the Flask web server that provides REST API endpoints
for DFA validation, simulation, and generation.

API Endpoints:
--------------
POST /api/validate      - Validate a DFA structure
POST /api/simulate      - Simulate DFA with input string
POST /api/generate-dfa  - Generate DFA for a pattern
GET  /                  - Serve the frontend application

The server acts as a bridge between the frontend UI and the backend logic,
receiving JSON requests and returning JSON responses.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# Add the backend directory to Python path so we can import our modules
# This allows us to use: from dfa_logic import ...
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our DFA logic modules
from dfa_logic import validate_dfa, simulate_dfa, get_dfa_info
from dfa_generator import generate_dfa

# Initialize Flask application
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Enable CORS (Cross-Origin Resource Sharing)
# This allows the frontend to make requests to the backend even if served from different origins
CORS(app)


@app.route('/')
def serve_frontend():
    """
    Serves the main frontend HTML file.
    
    When user visits http://localhost:5000/, this route returns index.html
    which contains the complete UI for the DFA application.
    
    Returns:
        HTML file: The frontend application
    """
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/validate', methods=['POST'])
def validate():
    """
    Validates a DFA structure.
    
    Request Body (JSON):
    {
        "states": ["q0", "q1"],
        "alphabet": ["0", "1"],
        "initial": "q0",
        "finals": ["q1"],
        "transitions": {...}
    }
    
    Response (JSON):
    {
        "valid": true/false,
        "errors": ["error message 1", "error message 2", ...]
    }
    
    This endpoint checks if the DFA follows the formal definition:
    - All required fields present
    - Initial state is valid
    - Final states are valid
    - All transitions are complete and deterministic
    """
    try:
        # Get DFA from request body
        dfa = request.get_json()
        
        if not dfa:
            return jsonify({
                "valid": False,
                "errors": ["No DFA data provided"]
            }), 400
        
        # Validate the DFA
        result = validate_dfa(dfa)
        
        return jsonify(result), 200
        
    except Exception as e:
        # Handle any unexpected errors
        return jsonify({
            "valid": False,
            "errors": [f"Server error: {str(e)}"]
        }), 500


@app.route('/api/simulate', methods=['POST'])
def simulate():
    """
    Simulates a DFA on a given input string.
    
    Request Body (JSON):
    {
        "dfa": {
            "states": [...],
            "alphabet": [...],
            "initial": "...",
            "finals": [...],
            "transitions": {...}
        },
        "input_string": "00110101"
    }
    
    Response (JSON):
    {
        "path": ["q0", "q1", "q0", ...],
        "final_state": "q1",
        "accepted": true/false,
        "error": null or "error message"
    }
    
    This endpoint runs the DFA simulation step-by-step:
    1. Start at initial state
    2. Process each character using transition function
    3. Track the complete path of states visited
    4. Check if final state is in accept states
    """
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "path": [],
                "final_state": None,
                "accepted": False,
                "error": "No data provided"
            }), 400
        
        dfa = data.get('dfa')
        input_string = data.get('input_string', '')
        
        if not dfa:
            return jsonify({
                "path": [],
                "final_state": None,
                "accepted": False,
                "error": "No DFA provided"
            }), 400
        
        # First validate the DFA
        validation = validate_dfa(dfa)
        if not validation['valid']:
            return jsonify({
                "path": [],
                "final_state": None,
                "accepted": False,
                "error": f"Invalid DFA: {', '.join(validation['errors'])}"
            }), 400
        
        # Simulate the DFA
        result = simulate_dfa(dfa, input_string)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "path": [],
            "final_state": None,
            "accepted": False,
            "error": f"Server error: {str(e)}"
        }), 500


@app.route('/api/generate-dfa', methods=['POST'])
def generate():
    """
    Generates a DFA for a specific pattern matching task.
    
    Request Body (JSON):
    {
        "mode": "starts" | "ends" | "substring",
        "pattern": "ab",
        "alphabet": ["a", "b"]
    }
    
    Response (JSON):
    {
        "dfa": {
            "states": [...],
            "alphabet": [...],
            "initial": "...",
            "finals": [...],
            "transitions": {...}
        },
        "info": {
            "num_states": 3,
            "num_symbols": 2,
            ...
        }
    }
    
    This endpoint automatically constructs a DFA based on the pattern type:
    - "starts": Strings starting with pattern
    - "ends": Strings ending with pattern
    - "substring": Strings containing pattern
    """
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No data provided"
            }), 400
        
        mode = data.get('mode')
        pattern = data.get('pattern')
        alphabet = data.get('alphabet')
        
        # Validate inputs
        if not mode or mode not in ['starts', 'ends', 'substring']:
            return jsonify({
                "error": "Mode must be 'starts', 'ends', or 'substring'"
            }), 400
        
        if not pattern:
            return jsonify({
                "error": "Pattern cannot be empty"
            }), 400
        
        if not alphabet or not isinstance(alphabet, list):
            return jsonify({
                "error": "Alphabet must be a non-empty list of symbols"
            }), 400
        
        # Generate the DFA
        dfa = generate_dfa(mode, pattern, alphabet)
        
        # Get additional info about the DFA
        info = get_dfa_info(dfa)
        
        return jsonify({
            "dfa": dfa,
            "info": info
        }), 200
        
    except ValueError as e:
        # Handle validation errors from the generator
        return jsonify({
            "error": str(e)
        }), 400
        
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500


@app.route('/api/dfa-info', methods=['POST'])
def dfa_info():
    """
    Returns formatted information about a DFA.
    
    Request Body (JSON):
    {
        "dfa": {...}
    }
    
    Response (JSON):
    {
        "states": [...],
        "alphabet": [...],
        "initial": "...",
        "finals": [...],
        "num_states": int,
        "num_symbols": int
    }
    
    This endpoint is useful for displaying the DFA 5-tuple in the UI.
    """
    try:
        data = request.get_json()
        
        if not data or 'dfa' not in data:
            return jsonify({
                "error": "No DFA provided"
            }), 400
        
        dfa = data['dfa']
        info = get_dfa_info(dfa)
        
        return jsonify(info), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500


# Main entry point - runs the Flask development server
if __name__ == '__main__':
    """
    When this script is run directly (python app.py),
    it starts the Flask development server.
    
    The server will be available at: http://localhost:5000
    
    Debug mode is enabled for development:
    - Auto-reload on code changes
    - Detailed error messages
    - Interactive debugger
    
    For production, disable debug mode and use a production WSGI server.
    """
    print("=" * 60)
    print("DFA Animation Web Application - Backend Server")
    print("=" * 60)
    print("Server starting at: http://localhost:5000")
    print("Frontend will be served automatically")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run the Flask app
    # debug=True enables auto-reload and detailed error messages
    app.run(debug=True, host='0.0.0.0', port=5000)
