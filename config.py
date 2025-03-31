import os
import json

# Default configuration for the keep-alive service
DEFAULT_CONFIG = {
    "url": "https://minor-ats-api.onrender.com/evaluate-resume",
    "headers": {"Content-Type": "application/json"},
    "data": {
        "job_description": "Software Engineer with Python, AI, and Data Science skills",
        "resume_data": {
            "education": {"degree": "B.Tech in Computer Science", "university": "XYZ University"},
            "experience": [
                {"role": "Data Analyst", "organization": "TechCorp", "responsibilities": ["Analyzed data", "Built dashboards"]}
            ],
            "projects": [{"name": "AI Chatbot", "description": ["Built a chatbot using GPT"]}],
            "technical_skills": {"Programming": ["Python", "JavaScript"], "Data Science": ["Pandas", "NumPy"]}
        }
    },
    "interval": 180,  # Ping interval in seconds (3 minutes)
    "max_history": 100,  # Maximum number of ping history entries to keep
    "log_level": "INFO",
    "log_file": "keep_alive.log"
}

def get_config():
    """
    Load configuration from the environment or use defaults.
    """
    config = DEFAULT_CONFIG.copy()
    
    # Override settings from environment variables
    if os.environ.get('PING_URL'):
        config['url'] = os.environ.get('PING_URL')
    
    if os.environ.get('PING_INTERVAL'):
        try:
            interval = int(os.environ.get('PING_INTERVAL'))
            # Ensure the interval is at least 60 seconds to prevent excessive requests
            config['interval'] = max(60, interval)
        except ValueError:
            pass
    
    if os.environ.get('MAX_HISTORY'):
        try:
            config['max_history'] = int(os.environ.get('MAX_HISTORY'))
        except ValueError:
            pass
    
    if os.environ.get('LOG_LEVEL'):
        config['log_level'] = os.environ.get('LOG_LEVEL')
    
    if os.environ.get('LOG_FILE'):
        config['log_file'] = os.environ.get('LOG_FILE')
        
    if os.environ.get('PING_DATA'):
        try:
            custom_data = json.loads(os.environ.get('PING_DATA'))
            config['data'] = custom_data
        except (json.JSONDecodeError, TypeError):
            # If JSON parsing fails, keep the default data
            pass
            
    return config

def save_config(config):
    """
    Save configuration to environment variables (in-memory only)
    """
    os.environ['PING_URL'] = config['url']
    os.environ['PING_INTERVAL'] = str(config['interval'])
    os.environ['MAX_HISTORY'] = str(config['max_history'])
    os.environ['LOG_LEVEL'] = config['log_level']
    os.environ['LOG_FILE'] = config['log_file']
    
    # Only save data if it's different from default
    if config['data'] != DEFAULT_CONFIG['data']:
        os.environ['PING_DATA'] = json.dumps(config['data'])
