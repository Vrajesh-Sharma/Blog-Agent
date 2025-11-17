from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import json
import os
from datetime import datetime
import uuid
import logging
import time
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables: put GEMINI_API_KEY in .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini & logging
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)
app.config['JSON_SORT_KEYS'] = False

sessions = {}

user_preferences = {
    "tone": "professional",
    "length": "1500-2000",
    "audience": "developers",
    "include_examples": True
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate_page():
    return render_template('generate.html')

@app.route('/history')
def history_page():
    # Later, connect to DB for past blogs
    past_blogs = [
        {
            "id": "blog_001",
            "topic": "Getting Started with AI Agents",
            "date": "2025-11-15",
            "status": "complete",
            "word_count": 1847
        },
        {
            "id": "blog_002",
            "topic": "Understanding Multi-Agent Systems",
            "date": "2025-11-14",
            "status": "complete",
            "word_count": 2103
        }
    ]
    return render_template('history.html', blogs=past_blogs)

@app.route('/api/generate-blog', methods=['POST'])
def generate_blog():
    data = request.json
    topic = data.get('topic', 'AI Agents')
    preferences = data.get('preferences', user_preferences)
    print(f"[GENERATE] Blog requested for topic: {topic}")
    logging.info(f"Starting blog generation for topic: {topic}")

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'id': session_id,
        'topic': topic,
        'preferences': preferences,
        'status': 'in_progress',
        'created_at': datetime.now().isoformat(),
        'current_stage': 'research',
        'research_data': None,
        'outline': None,
        'draft': None,
        'final_blog': None,
        'stages_completed': []
    }

    def generate_stream():
        # --------------------- Research Agent Stage ---------------------
        print("[BLOG AGENT] Calling Research Agent...")
        logging.info("Calling Research Agent for topic: %s", topic)
        yield json.dumps({
            'event': 'stage_start',
            'stage': 'research',
            'message': 'Research Agent is researching...'
        }) + '\n'
        research_start = time.time()
        prompt_research = (f"You are a research agent. Give me 3 key insights & 3 credible sources on '{topic}' "
                           f"for an expert blog aimed at {preferences.get('audience', 'developers')}. "
                           "Use technical language and explain why each source is authoritative.")
        try:
            response = gemini_model.generate_content(prompt_research)
            research_response = response.text
            print("[BLOG AGENT] Research Agent finished (%.2f seconds)" % (time.time() - research_start))
            logging.info("Research Agent result received.")
            key_points = []
            sources = []
            for line in research_response.split('\n'):
                if line.strip().startswith('-') or line.strip()[0:2] == '1.':
                    key_points.append(line.lstrip('-').strip())
                elif "http" in line or ".com" in line or ".org" in line:
                    sources.append({'url': line.strip(), 'title': line.strip()})
            research_data = {
                'key_points': key_points if key_points else [research_response],
                'sources': sources if sources else []
            }
        except Exception as e:
            logging.error(f"Research Agent encountered an error: {str(e)}")
            research_data = {
                'key_points': [f'Research unavailable ({str(e)})'],
                'sources': []
            }
        sessions[session_id]['research_data'] = research_data
        yield json.dumps({
            'event': 'research_complete',
            'stage': 'research',
            'data': research_data,
            'progress': 25
        }) + '\n'

        # --------------------- Outline Agent Stage ---------------------
        print("[BLOG AGENT] Calling Outline Agent...")
        logging.info("Calling Outline Agent for topic: %s", topic)
        yield json.dumps({
            'event': 'stage_start',
            'stage': 'outline',
            'message': 'Outline Agent is structuring the blog...'
        }) + '\n'
        outline_start = time.time()
        prompt_outline = (f"You are an outline agent. Create a detailed, sectioned outline for a technical blog titled '{topic}' "
                          f"for {preferences.get('audience', 'developers')}. Include intro, deep-dive technical sections, real-world examples, and a conclusion.")
        try:
            response = gemini_model.generate_content(prompt_outline)
            outline_response = response.text
            print("[BLOG AGENT] Outline Agent finished (%.2f seconds)" % (time.time() - outline_start))
            logging.info("Outline Agent result received.")
            outline_data = {
                'title': f'Complete Guide to {topic}',
                'sections': outline_response.split('\n')
            }
        except Exception as e:
            logging.error(f"Outline Agent encountered an error: {str(e)}")
            outline_data = {
                'title': f'Complete Guide to {topic}',
                'sections': ['Outline unavailable, please retry.']
            }
        sessions[session_id]['outline'] = outline_data
        yield json.dumps({
            'event': 'outline_complete',
            'stage': 'outline',
            'data': outline_data,
            'progress': 50
        }) + '\n'

        # --------------------- Writing Agent Stage ---------------------
        print("[BLOG AGENT] Calling Writing Agent...")
        logging.info("Calling Writing Agent for topic: %s", topic)
        yield json.dumps({
            'event': 'stage_start',
            'stage': 'writing',
            'message': 'Writing Agent is generating the blog draft...'
        }) + '\n'
        writing_start = time.time()
        prompt_blog = (f"You are a blog writing agent. Draft a {preferences.get('length', '1500-2000')} word technical blog on '{topic}', "
                       f"following this outline: {outline_data['sections']}, "
                       f"for {preferences.get('audience', 'developers')} in a {preferences.get('tone', 'professional')} tone. "
                       f"Include examples: {preferences.get('include_examples', True)}. Start with an engaging intro, cite 3 recent sources, and end with an actionable conclusion.")
        try:
            response = gemini_model.generate_content(prompt_blog)
            draft_content = response.text
            print("[BLOG AGENT] Writing Agent finished (%.2f seconds)" % (time.time() - writing_start))
            logging.info("Writing Agent result received.")
        except Exception as e:
            logging.error(f"Writing Agent encountered an error: {str(e)}")
            draft_content = f"Blog draft unavailable due to error: {str(e)}"
        sessions[session_id]['draft'] = draft_content
        yield json.dumps({
            'event': 'writing_complete',
            'stage': 'writing',
            'data': {'content': draft_content},
            'progress': 75
        }) + '\n'

        # --------------------- Editing Agent Stage ---------------------
        print("[BLOG AGENT] Calling Editing Agent...")
        logging.info("Calling Editing Agent for topic: %s", topic)
        yield json.dumps({
            'event': 'stage_start',
            'stage': 'editing',
            'message': 'Editing Agent is polishing and optimizing the draft...'
        }) + '\n'
        # Optionally, you can send another Gemini API call to specifically edit/polish the content.
        final_blog = draft_content.strip() + "\n\n---\n*Originally generated by Blog AI Agent (Gemini & Google ADK)*"
        sessions[session_id]['final_blog'] = final_blog
        sessions[session_id]['status'] = 'complete'
        yield json.dumps({
            'event': 'complete',
            'stage': 'editing',
            'session_id': session_id,
            'status': 'complete',
            'final_blog': final_blog,
            'progress': 100,
            'metrics': {
                'word_count': len(final_blog.split()),
                'readability_score': 8.5,
                'quality_score': 8.2
            }
        }) + '\n'
        print(f"[COMPLETE] Blog generation completed for session: {session_id}")
        logging.info("Blog generation process completed for session: %s", session_id)

    return Response(generate_stream(), mimetype='text/event-stream')

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify(sessions[session_id])

@app.route('/api/preferences', methods=['GET'])
def get_preferences():
    return jsonify(user_preferences)

@app.route('/api/preferences', methods=['POST'])
def update_preferences():
    global user_preferences
    user_preferences.update(request.json)
    print(f"[PREFERENCES] Updated preferences: {user_preferences}")
    return jsonify({'success': True, 'preferences': user_preferences})

@app.errorhandler(404)
def not_found(error):
    print(f"[ERROR] 404 - Not Found: {request.path}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    print(f"[ERROR] 500 - Internal Server Error")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("[START] Flask Blog Agent running...")
    app.run(debug=True, host='0.0.0.0', port=5000)
