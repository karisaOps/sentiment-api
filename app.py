from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# Load a model that supports NEUTRAL sentiment
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    tokenizer="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

# Map model labels to readable strings
label_map = {
    "LABEL_0": "NEGATIVE",
    "LABEL_1": "NEUTRAL",
    "LABEL_2": "POSITIVE"
}

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    result = sentiment_pipeline(text)[0]
    sentiment = label_map.get(result['label'], result['label'])
    return jsonify({
        'text': text,
        'sentiment': sentiment,
        'confidence': result['score']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)