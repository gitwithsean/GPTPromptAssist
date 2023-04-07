## GPTPromptAssist

Currently only really working for creating better compression prompts, more features will be coming

## Requirements
### For cli

* openai
* nltk
* rouge
* an openai api key

### For web ui

* same as above
* flask

## Quick Start
### For cli
* put an orig_text.txt that you want to test the compression algorithm with in originals/
* create a .env file and store your open ai api key there
* If you have access to the gpt 4 api, or want to try different models, find these lines in compression_asst.py and edit them
```        
"compressor_model": "text-davinci-002",
"decompressor_model": "text-davinci-002",
"assistant_model": "text-davinci-003",
```
* `python compression_asst.py`
* It will start the first iteration, provide you with the results, store those results (and more) in a timestamped directory under `prompts`, and provide you with the option to hit return to go through the process again using the new compression/decompression prompts it created.
* It does not edit the original files, nor will it notice changes to those files (yet) unless it is restarted.

### For web
* create a .env file and store your open ai api key in it
* `flask run`
* open a browser and go to `http://127.0.0.1:5000`