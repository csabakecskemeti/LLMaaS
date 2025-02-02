import sys
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Default values for LLM server URL and model name
DEFAULT_LLM_SERVER_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL_NAME = "llama3.1"

# Get the LLM server URL and model name from command-line arguments, or use defaults
LLM_SERVER_URL = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LLM_SERVER_URL
MODEL_NAME = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL_NAME

# Define the endpoint that the HTML will call
@app.route('/api/generate', methods=['POST'])
def generate():
    payload = request.json

    # Log the incoming payload
    print(f"Received request payload: {payload}")

    # Override the model in the payload with the model name from the command-line argument
    payload["model"] = MODEL_NAME

    # Ensure we're passing the 'stream' flag as True to the LLM server
    payload["stream"] = True

    # Make a request to the LLM server with the same payload
    try:
        response = requests.post(LLM_SERVER_URL, json=payload, stream=True)

        # Check if the response is successful
        if response.status_code == 200:
            def generate_stream():
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk.decode('utf-8')

            return Response(generate_stream(), content_type='text/plain; charset=utf-8')
        else:
            return jsonify({"error": "LLM server response error"}), response.status_code
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Running on local machine, port 5000

