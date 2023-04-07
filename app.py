from flask import Flask, render_template, request, jsonify
import json
from compression_asst import main

app = Flask(__name__)

# Import other necessary functions from your script
# from your_script import ...

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    # Receive data from the front-end (e.g., original_text, compressor_prompt_candidate, decompressor_prompt_candidate)
    data = request.get_json()

    # Call your main function with the input data and get the results
    results = main(data)

    # Return the results to the front-end
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)