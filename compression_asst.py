import openai
import nltk
import os
import json
import datetime
from nltk.translate.bleu_score import sentence_bleu
from rouge import Rouge
import time

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

openai.api_key = open_file('orig_text.txt')

data = {
        "original_text": open_file('originals/orig_text.txt'),
        "compressor_prompt_candidate": open_file('orig_compression_prompt.txt'),
        "decompressor_prompt_candidate": open_file('orig_decompression_prompt.txt'),
        "reflection_prompt_candidate": open_file('orig_reflection_prompt.txt'),
        "compressor_model": "text-davinci-002",
        "decompressor_model": "text-davinci-002",
        "assistant_model": "text-davinci-003",
        "completion_config": {
            "temperature": 0.5,
            "max_tokens": 1000,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        },
        "bleu_score_target": 0.5,
        "gpt_score_target": 0.95,
        "rouge_score_target": 0.8
}

def evaluate_bleu_score(decompressed_text, original_text=data["original_text"]):
    original_tokens = nltk.word_tokenize(original_text.lower())
    decompressed_tokens = nltk.word_tokenize(decompressed_text.lower())

    bleu_score = sentence_bleu([original_tokens], decompressed_tokens)

    return bleu_score


def evaluate_rouge_score(decompressed_text, original_text=data["original_text"]):
    rouge = Rouge()
    scores = rouge.get_scores(decompressed_text, original_text)

    return scores[0]['rouge-l']['f']

def gpt_response(model, prompt, completion_config):
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=completion_config["temperature"],
        max_tokens=completion_config["max_tokens"],
        top_p=completion_config["top_p"],
        frequency_penalty=completion_config["frequency_penalty"],
        presence_penalty=completion_config["presence_penalty"]
    )
    return response

def calc_compression_ratio(original_text=data["original_text"], compressed_text=""):
    wrd_cnt_orig = len(original_text.split())
    wrd_cnt_comp = len(compressed_text.split())
    ratio = wrd_cnt_comp / wrd_cnt_orig
    return round(ratio, 3)


def main():
    iterator = 0
    while True:
        print("\n\n------- Hit ctrl-c to end the program ------- \n\nYou will find the results for each iteration under prompts/\n\n")
        iterator = iterator+1
        run(data, iterator)
        input("\n\n--------- Press Enter to continue ---------\n\n")
        print("\n\n------- Moving on to next iteration -------\n\n")

def run(input, iterator):
    data = input
    compressor_prompt_candidate = data["compressor_prompt_candidate"]
    decompressor_prompt_candidate = data["decompressor_prompt_candidate"]
    reflection_prompt_candidate = data["reflection_prompt_candidate"]
    original_text = data["original_text"]
    pretty_reflection_response = {}
    bleu_score = 0
    rouge_score = 0
    style_preservation_score = 0
    semantic_preservation_score
    subFolder = f"{datetime.datetime.now()}"

    try:
        # Compress the text
        compressor_prompt = f"{compressor_prompt_candidate}\n\n{original_text}\n\nCompressor Output:"
        compressed_text = gpt_response(data["compressor_model"], compressor_prompt, data["completion_config"]).choices[0].text.strip()
        compression_ratio = calc_compression_ratio(original_text, compressed_text)

        # Decompress the text
        decompressor_prompt = f"{decompressor_prompt_candidate}\n\n{compressed_text}\n\nOutput:"
        decompressed_text = gpt_response(data["decompressor_model"], decompressor_prompt, data["completion_config"]).choices[0].text.strip()

        # Evaluate BLEU and ROUGE scores
        bleu_score = evaluate_bleu_score(decompressed_text)
        rouge_score = evaluate_rouge_score(decompressed_text)

        print(f"iteration {iterator} compression ratio: {compression_ratio}")
        print(f"iteration {iterator} BLEU score: {bleu_score}")
        print(f"iteration {iterator} ROUGE Score: {rouge_score}")

        # Reflect on the results and suggest improvements
        reflection_prompt = (
            f"{reflection_prompt_candidate}\n\nOutput ONLY a JSON consisting of the following properties, 'analysis', 'suggested_improvements', 'new_compressor_prompt_candidate', 'new_decompressor_prompt_candidate', 'semantic_preservation_score, style_preservation_score'.\n\n"
            f"Original Text: {original_text}\n\n"
            f"Compressor Prompt: {compressor_prompt_candidate}\n\n"
            f"Compressed Text: {compressed_text}\n\n"
            f"Decompressor Prompt: {decompressor_prompt_candidate}\n\n"
            f"Decompressed Text: {decompressed_text}\n\n"
            f"Compression Ratio: {compression_ratio}\n\n"
            f"JSON:"
        )
        
        reflection_response = gpt_response(
            data['assistant_model'], reflection_prompt, data["completion_config"])
        reflection_response_json = json.loads(
            reflection_response.choices[0].text.strip())
        semantic_preservation_score = reflection_response_json["semantic_preservation_score"]
        style_preservation_score = reflection_response_json["style_preservation_score"]
        gpt_score = reflection_response_json["gpt_score"]
        print(f"iteration {iterator} Semantic Score: {semantic_preservation_score}")
        print(f"iteration {iterator} Style Score: {style_preservation_score}\n\n")
        print(f"iteration {iterator} GPT Score: {gpt_score}\n\n")

        pretty_reflection_response = json.dumps(
            reflection_response_json, indent=2)
        
        print(pretty_reflection_response["analysis"])
        print(pretty_reflection_response["suggested_improvements"])
        print(pretty_reflection_response["new_compressor_prompt_candidate"])
        print(pretty_reflection_response["new_decompressor_prompt_candidate"])
        
        iteration_data = {
            "iteration": iterator,
            "bleu_score": bleu_score,
            "rouge_score": rouge_score,
            "semantic_preservation_score": semantic_preservation_score,
            "style_preservation_score": style_preservation_score,
            "gpt_score": gpt_score,
            "compression_ratio": compression_ratio,
            "original_text": original_text,
            "compressor_prompt_candidate": compressor_prompt_candidate,
            "compressed_text": compressed_text,
            "decompressor_prompt_candidate": decompressor_prompt_candidate,
            "decompressed_text": decompressed_text,
            "reflection_response": pretty_reflection_response,
            "assistant_model": data['compressor_model'],
            "assistant_model": data['decompressor_model'],
            "assistant_model": data['assistant_model'],
            "completion_config": data['completion_config'],
            "token_info": reflection_response["usage"]
        }

        iteration_file_name = f"{iterator}".zfill(3)
        iteration_file = os.path.join(
            "prompts", subFolder, f"{iteration_file_name}.json")
        os.makedirs(os.path.dirname(iteration_file), exist_ok=True)
        with open(iteration_file, "w") as f:
            json.dump(iteration_data, f, indent=2)

        compressor_prompt_candidate = ""
        decompressor_prompt_candidate = ""

        compressor_prompt_candidate = reflection_response_json["new_compressor_prompt_candidate"]
        decompressor_prompt_candidate = reflection_response_json["new_decompressor_prompt_candidate"]

        return iteration_data

    except Exception as e:
        print("\n\n ------- An Exception Occurred ------- \n\n")
        print(f"\nException: {e}\n")
        print(pretty_reflection_response)
        current_state = {
            "iteration": iterator,
            "most_recent_compressor_prompt": compressor_prompt_candidate,
            "compressed_text": compressed_text,
            "most_recent_decompressor_prompt": decompressor_prompt_candidate,
            "reflection_response": pretty_reflection_response,
            "exception": e
        }
        pretty_current_state = json.dumps(current_state, indent=2)
        print(pretty_current_state)
        print("\n\n ------------------------------------- \n\n")


if __name__ == "__main__":
    main()


