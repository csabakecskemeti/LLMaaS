import sys
import json
import re
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Check for help argument before initializing Flask
if "--help" in sys.argv or "-h" in sys.argv:
    print("""
Flask LLM Proxy Server
----------------------
This script runs a proxy server that forwards requests to a local LLM (e.g., llama3.1).
It enables any HTML page to use the local LLM while enforcing security measures like 
rate limiting, prompt validation, and execution prevention.

Usage:
    python proxy.py [LLM_SERVER_URL] [MODEL_NAME] [RATE_LIMIT]

Arguments:
    LLM_SERVER_URL  (optional) The URL of the local LLM server. Default: http://localhost:11434/api/generate
    MODEL_NAME      (optional) The model name to use for requests. Default: llama3.1
    RATE_LIMIT      (optional) Maximum number of requests per minute (default: 5)

Example:
    python proxy.py http://localhost:12345/api/generate my_custom_model 10

Additional Endpoints:
    - /help         Displays API usage and security information.
    - /api/generate Forwards prompt requests to the LLM server with security protections.
    
Security Measures:
    - Rate limiting (user-defined, default: 5 requests per minute per IP)
    - Only accepts JSON requests
    - Prompt validation to prevent injection attacks
    - Enforced timeout to prevent resource exhaustion
    """)
    sys.exit(0)

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Default values
DEFAULT_LLM_SERVER_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL_NAME = "llama3.1"
DEFAULT_RATE_LIMIT = 5  # Default: 5 requests per minute

# Get arguments from CLI
LLM_SERVER_URL = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LLM_SERVER_URL
MODEL_NAME = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL_NAME
try:
    RATE_LIMIT = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_RATE_LIMIT
    if RATE_LIMIT <= 0:
        raise ValueError("Rate limit must be a positive integer.")
except ValueError:
    print("Invalid rate limit. Please provide a positive integer.")
    sys.exit(1)

# Rate limiter (configurable via argument)
limiter = Limiter(get_remote_address, app=app, default_limits=[f"{RATE_LIMIT} per minute"])

# Allow only safe characters in the prompt (basic injection mitigation)
SAFE_PROMPT_PATTERN = re.compile(r'^[a-zA-Z0-9\s.,!?;:()\-<>\'"/]+$', re.UNICODE)


@app.route('/help', methods=['GET'])
def help():
    """ Provides usage information for the proxy server """
    help_text = {
        "description": "This is a Flask-based proxy for forwarding requests to a local LLM server.",
        "endpoints": {
            "/api/generate": {
                "method": "POST",
                "description": "Forwards a request to the local LLM server.",
                "request_format": {
                    "model": "Automatically set to the configured model (e.g., 'llama3.1').",
                    "prompt": "User input (validated for safe characters).",
                    "stream": "Always set to True for efficient processing."
                },
                "rate_limit": f"{RATE_LIMIT} requests per minute per IP.",
                "content_type": "Only 'application/json' is allowed.",
                "response_format": "Streaming text response."
            },
            "/help": {
                "method": "GET",
                "description": "Displays this help information."
            }
        },
        "security": {
            "rate_limiting": f"{RATE_LIMIT} requests per minute per IP.",
            "prompt_validation": "Only allows alphanumeric characters and basic punctuation.",
            "content_type": "Rejects non-JSON requests.",
            "timeout": "Requests to LLM server have a 10-second timeout."
        }
    }
    return jsonify(help_text)


@app.route('/api/generate', methods=['POST'])
@limiter.limit(f"{RATE_LIMIT} per minute")  # Restrict dynamically based on CLI input
def generate():
    # Enforce content type
    if request.content_type != 'application/json':
        return jsonify({"error": "Invalid content type. Only application/json is allowed."}), 400

    payload = request.json
    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid request format"}), 400

    # Log the incoming payload safely
    print(f"Received request payload: {json.dumps(payload, indent=2)}")

    # Validate and sanitize prompt
    prompt = payload.get("prompt", "")
    if not isinstance(prompt, str) or not SAFE_PROMPT_PATTERN.match(prompt):
        return jsonify({"error": "Invalid prompt format"}), 400

    # Override the model in the payload with the model name from the command-line argument
    payload["model"] = MODEL_NAME

    # Ensure 'stream' flag is True to prevent excessive resource usage
    payload["stream"] = True

    # Forward the request to the LLM server
    try:
        response = requests.post(LLM_SERVER_URL, json=payload, stream=True, timeout=10)

        # Check if the response is successful
        if response.status_code == 200:
            def generate_stream():
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk.decode('utf-8')

            return Response(generate_stream(), content_type='text/plain; charset=utf-8')
        else:
            return jsonify({"error": "LLM server response error"}), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return jsonify({"error": "LLM server unreachable"}), 503
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

