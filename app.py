from flask import Flask, render_template, request, jsonify
from compression_asst import run
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = {
        "original_text": request.form['original_text'],
        "compressor_prompt_candidate": request.form['compressor_prompt_candidate'],
        "decompressor_prompt_candidate": request.form['decompressor_prompt_candidate'],
        "reflection_prompt_candidate": request.form['reflection_prompt_candidate'],
        "compressor_model": request.form['compressor_model'],
        "decompressor_model": request.form['decompressor_model'],
        "assistant_model": request.form['assistant_model'],
        "completion_config": {
            "temperature": float(request.form['temperature']),
            "max_tokens": int(request.form['max_tokens']),
            "top_p": float(request.form['top_p']),
            "frequency_penalty": float(request.form['frequency_penalty']),
            "presence_penalty": float(request.form['presence_penalty']),
        },
        "style_preservation_score_target": float(request.form['style_preservation_score_target']),
        "semantic_preservation_score_target": float(request.form['semantic_preservation_score_target']),
        "gpt_score_target": float(request.form['gpt_score_target']),
        "bleu_score_target": float(request.form['gpt_score_target']),
        "rouge_score_target": float(request.form['gpt_score_target']),
    }

    # print(data)
    
    # print("\n\nDATA:\n\n")
    # pretty_data = json.dumps(data, indent=2)
    # print(pretty_data)
    # print("\n\n\n\n")

    result = run(data, 0)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
