from flask import Flask, request, jsonify
from main import load_data, create_reverse_dictionary, normalize_text, suggest_word
import os

app = Flask(__name__)

# Path to the JSON file
script_dir = os.path.dirname(__file__)
filepath = os.path.join(script_dir, '../data/dictionary.json')

# Load the data and create the reverse dictionary
data = load_data(filepath)
reverse_data = create_reverse_dictionary(data)

def lookup(word, data):
    normalized_word = normalize_text(word)

    # Check if the word is in English
    if normalized_word in data:
        entries = data[normalized_word]
        translations = []

        if isinstance(entries, list):
            for entry in entries:
                translations.append({
                    "translation": entry['translations'][0],
                    "example": entry['example']
                })
        else:
            translations.append({
                "translation": entries['translations'][0],
                "example": entries['example']
            })

        return {
            "word_in_english": word,
            "translations": translations
        }

    # Check if the word is in Arabic
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                translations = item['translations']
                for translation in translations:
                    if normalize_text(translation) == normalized_word:
                        return {
                            "word_in_arabic": key,
                            "word_in_english": translation,
                            "example": item['example']
                        }
        else:
            translations = value['translations']
            if normalize_text(translations[0]) == normalized_word:
                return {
                    "word_in_arabic": key,
                    "word_in_english": translations[0],
                    "example": value['example']
                }

    return None

@app.route('/translate', methods=['GET'])
def translate_word():
    word = request.args.get('word')

    if not word:
        return jsonify({"error": "Word not provided."}), 400

    # Search for the word in the dictionary
    result = lookup(word, data)

    if result:
        return jsonify(result)

    # If the word is not found, suggest alternatives
    suggestion, details = suggest_word(word, reverse_data)

    if suggestion:
        english_word, example = details
        return jsonify({
            "error": f"'{word}' not found in the dictionary. Maybe you mean '{suggestion}'",
            "suggestion": {
                "word": suggestion,
                "translation": english_word,
                "example": example
            }
        }), 404

    return jsonify({"error": "Word not found in the dictionary."}), 404

if __name__ == '__main__':
    app.run(debug=True)
