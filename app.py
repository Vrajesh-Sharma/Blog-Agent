import os, uuid, json
from datetime import datetime
from threading import Lock

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai # Import official SDK

# --- Modular imports ---
from agents.research_agent import create_research_agent
from agents.outline_agent import create_outline_agent
from agents.writing_agent import create_writing_agent
from agents.editing_agent import create_editing_agent

# (Tool imports are now handled inside the agent files, or passed here if you prefer)
from services.session_service import SessionManager
from services.memory_service import MemoryManager

load_dotenv()

# --- Configuration ---
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash") # Use a standard model name
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

app = Flask(__name__)
CORS(app)
app.config['JSON_SORT_KEYS'] = False

# --- Services ---
session_manager = SessionManager()
memory_manager = MemoryManager()
sessions = {}
sessions_lock = Lock()

user_preferences = {
    "tone": "professional",
    "length": "1500-2000",
    "audience": "developers",
    "include_examples": True
}

# --- Agent Initialization ---
# Note: We don't need a global tool_registry anymore. 
# Tools are passed specifically to the agents that need them.

research_agent = create_research_agent(GEMINI_MODEL)
outline_agent = create_outline_agent(GEMINI_MODEL)
writing_agent = create_writing_agent(GEMINI_MODEL)
editing_agent = create_editing_agent(GEMINI_MODEL)

# Helper for SSE
def sse_packet(payload: dict, event: str = None):
    s = ""
    if event:
        s += f"event: {event}\n"
    s += f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
    return s

# --- Routes (Keep your existing routes mostly as is) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate_page():
    return render_template('generate.html')

@app.route('/history')
def history_page():
    with sessions_lock:
        all_sessions = list(sessions.values())
    all_sessions = sorted(all_sessions, key=lambda s: s.get('created_at', ''), reverse=True)
    return render_template('history.html', blogs=all_sessions)

@app.route('/api/generate-blog', methods=['POST'])
def generate_blog():
    data = request.json or {}
    topic = data.get('topic', 'AI Agents')
    preferences = data.get('preferences', user_preferences)

    session_id = str(uuid.uuid4())
    user_id = f"user_{session_id[:8]}"
    session_obj = {
        'id': session_id,
        'topic': topic,
        'preferences': preferences,
        'status': 'in_progress',
        'created_at': datetime.utcnow().isoformat(),
        'trace_id': f"trace_{session_id}",
        'stages': [],
        'research': None,
        'outline': None,
        'draft': None,
        'final_blog': None
    }
    with sessions_lock:
        sessions[session_id] = session_obj

    session_ref = session_manager.create_session(user_id=user_id, session_id=session_id)
    memory_ref = memory_manager.get_memory(session_id)

    def generate_stream():
        # Stage 1: Research
        yield sse_packet({'event': 'stage_start', 'stage': 'research', 'message': 'Researching...'}, event='stage_start')
        try:
            # .act() now accepts the dict and creates the prompt string internally
            research_result = research_agent.act({
                "topic": topic,
                "audience": preferences.get("audience")
            }, session_ref, memory_ref)
            
            sessions[session_id]['research'] = research_result
            sessions[session_id]['stages'].append('research')
            yield sse_packet({'event': 'research_complete', 'stage': 'research', 'data': research_result, 'progress': 25}, event='research_complete')
        except Exception as e:
            yield sse_packet({'event': 'error', 'stage': 'research', 'error': str(e)}, event='error')
            return # Stop stream on error

        # Stage 2: Outline
        yield sse_packet({'event': 'stage_start', 'stage': 'outline', 'message': 'Outlining...'}, event='stage_start')
        try:
            # research_result should be a dict now because of response_mime_type="application/json"
            key_points = sessions[session_id]['research'].get("key_points", []) if isinstance(sessions[session_id]['research'], dict) else []
            
            outline_result = outline_agent.act({
                "research_key_points": key_points,
                "topic": topic,
                "audience": preferences.get("audience")
            }, session_ref, memory_ref)
            
            sessions[session_id]['outline'] = outline_result
            sessions[session_id]['stages'].append('outline')
            yield sse_packet({'event': 'outline_complete', 'stage': 'outline', 'data': outline_result, 'progress': 50}, event='outline_complete')
        except Exception as e:
            yield sse_packet({'event': 'error', 'stage': 'outline', 'error': str(e)}, event='error')
            return

        # Stage 3: Writing
        yield sse_packet({'event': 'stage_start', 'stage': 'writing', 'message': 'Writing...'}, event='stage_start')
        try:
            writing_result = writing_agent.act({
                "outline": sessions[session_id]['outline'],
                "topic": topic,
                "preferences": preferences
            }, session_ref, memory_ref)
            
            sessions[session_id]['draft'] = writing_result
            sessions[session_id]['stages'].append('writing')
            yield sse_packet({'event': 'writing_complete', 'stage': 'writing', 'data': {'content_preview': str(writing_result)[:800]}, 'progress': 75}, event='writing_complete')
        except Exception as e:
            yield sse_packet({'event': 'error', 'stage': 'writing', 'error': str(e)}, event='error')
            return

        # Stage 4: Editing
        yield sse_packet({'event': 'stage_start', 'stage': 'editing', 'message': 'Editing...'}, event='stage_start')
        try:
            editing_result = editing_agent.act({
                "draft": sessions[session_id]['draft'],
                "preferences": preferences
            }, session_ref, memory_ref)
            
            sessions[session_id]['final_blog'] = editing_result
            sessions[session_id]['status'] = 'complete'
            sessions[session_id]['stages'].append('editing')
            
            metrics = {
                'word_count': len(str(editing_result).split()),
                'stages_completed': sessions[session_id]['stages'],
                'duration_seconds': (datetime.utcnow() - datetime.fromisoformat(sessions[session_id]['created_at'])).total_seconds()
            }
            yield sse_packet({'event': 'complete', 'stage': 'editing', 'session_id': session_id, 'status': 'complete', 'final_blog_preview': str(editing_result)[:2000], 'progress': 100, 'metrics': metrics}, event='complete')
        except Exception as e:
            yield sse_packet({'event': 'error', 'stage': 'editing', 'error': str(e)}, event='error')

    return Response(generate_stream(), mimetype='text/event-stream')

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    with sessions_lock:
        if session_id not in sessions:
            return jsonify({'error': 'Session not found'}), 404
        return jsonify(sessions[session_id])

@app.route('/api/preferences', methods=['GET'])
def get_preferences():
    return jsonify(user_preferences)

@app.route('/api/preferences', methods=['POST'])
def update_preferences():
    global user_preferences
    user_preferences.update(request.json or {})
    return jsonify({'success': True, 'preferences': user_preferences})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
