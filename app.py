from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from flask_cors import CORS

from openai import OpenAI


app = Flask(__name__)
CORS(app)
client = OpenAI()

def generate_outline(outline_prompt, target_keyword):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Generate content for the following prompt: {outline_prompt} using the keyword: {target_keyword}"},
            {"role": "user", "content": f"{outline_prompt}, {target_keyword}"},
        ]
    )
    
    return response.choices[0].message.content

def categorize_keywords(categorize_prompt, outline, keywords):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        
        messages=[
            {"role": "system", "content": f"Categorize the following {keywords} into the appropriate sections of the {outline} according to the {categorize_prompt} and dont repeat the words"},
            {"role": "user", "content": f"{categorize_prompt}{outline}\n\nKeywords: {', '.join(keywords)}"},
        ]
    )
    return response.choices[0].message.content

def generate_content(content_prompt, categorized_keywords):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Write detailed content for for the following prompt: {content_prompt} using the keyword: {categorized_keywords}"},
            {"role": "user", "content": f"{content_prompt}{categorized_keywords}"},
        ]
    )
    return response.choices[0].message.content

def quality_assurance(qa_prompt, content, keywords):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        
        max_tokens=1024,
        messages=[
            {"role": "user", "content": f"Check if the following content includes all these keywords: {', '.join(keywords)}. According to the {qa_prompt}If any keywords are missing, add those keywords in the content.\n\nContent:\n{content}"},
            {"role": "user", "content": f"{qa_prompt}\n\nKeywords: {', '.join(keywords)}{content}"}
        ]
    )
    return response.choices[0].message.content



@app.route('/')
def index():
    return render_template('index.html')




@app.route('/generate-outline', methods=['POST'])
def generate_outline_endpoint():
    data = request.json
    target_keyword = data.get('target_keyword')
    outline_prompt = data.get('outline_prompt')
    if not target_keyword or not outline_prompt:
        return jsonify({"error": "Outline prompt and target keyword are required"}), 400
    try:
        outline = generate_outline(outline_prompt=outline_prompt, target_keyword=target_keyword)
        return jsonify({"outline": outline})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/categorize-keywords', methods=['POST'])
def categorize_keywords_endpoint():
    data = request.json
    outline = data.get('outline')
    keywords = data.get('keywords')
    categorize_prompt = data.get('categorize_prompt')
    if not outline or not keywords:
        return jsonify({"error": "Outline and keywords are required"}), 400
    try:
        categorized_keywords = categorize_keywords(categorize_prompt, outline, keywords)
        return jsonify( {"categorized_keywords":categorized_keywords})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-content', methods=['POST'])
def generate_content_endpoint():
    data = request.json
    categorized_keywords = data.get('categorized_keywords')
    content_prompt = data.get('content_prompt')
    if not categorized_keywords:
        return jsonify({"error": "categorized keywords are required"}), 400
    try:
        content = generate_content(content_prompt, categorized_keywords)
        return jsonify({"content":content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/quality-assurance', methods=['POST'])
def quality_assurance_endpoint():
    data = request.json
    content = data['content']
    keywords = data['keywords']
    qa_prompt = data.get('qa_prompt')
    try:
        qa_result = quality_assurance(qa_prompt, content, keywords)
        return jsonify({"qa_result":qa_result})
    except Exception as e:
         return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)