import os
import json

# Default configuration for the keep-alive service
DEFAULT_CONFIG = {
    "url": "https://minor-ats-api.onrender.com/evaluate-resume",
    "method": "POST",  # HTTP method: GET, POST, PUT, etc.
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

# Example configurations for different API types
EXAMPLE_CONFIGS = {
    # Simple GET health check
    "simple_get": {
        "url": "https://your-api.com/health",
        "method": "GET",
        "headers": {"User-Agent": "KeepAlive-Service"},
        "data": None
    },
    
    # Basic JSON ping
    "basic_json": {
        "url": "https://your-api.com/ping",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "data": {"ping": True, "service": "keepalive"}
    },
    
    # Form data submission
    "form_data": {
        "url": "https://your-api.com/keep-alive",
        "method": "POST",
        "headers": {"Content-Type": "application/x-www-form-urlencoded"},
        "data": "status=alive&source=keepalive"
    },
    
    # Authenticated API
    "with_auth": {
        "url": "https://your-api.com/endpoint",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer YOUR_TOKEN_HERE"
        },
        "data": {"action": "ping", "timestamp": "auto"}
    }
}

def get_config():
    """
    Load configuration from the environment or use defaults.
    Supports flexible request structure customization.
    """
    config = DEFAULT_CONFIG.copy()
    
    # Override settings from environment variables
    if os.environ.get('TARGET_URL'):
        config['url'] = os.environ.get('TARGET_URL')
    
    if os.environ.get('REQUEST_METHOD'):
        config['method'] = os.environ.get('REQUEST_METHOD').upper()
    
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
    
    # Custom headers support
    if os.environ.get('CUSTOM_HEADERS'):
        try:
            custom_headers = json.loads(os.environ.get('CUSTOM_HEADERS'))
            config['headers'].update(custom_headers)
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Custom payload/data support
    if os.environ.get('CUSTOM_PAYLOAD'):
        try:
            custom_data = json.loads(os.environ.get('CUSTOM_PAYLOAD'))
            config['data'] = custom_data
        except (json.JSONDecodeError, TypeError):
            # If JSON parsing fails, treat as string data for form submissions
            config['data'] = os.environ.get('CUSTOM_PAYLOAD')
    
    # Legacy support
    if os.environ.get('PING_URL'):
        config['url'] = os.environ.get('PING_URL')
    
    if os.environ.get('PING_DATA'):
        try:
            custom_data = json.loads(os.environ.get('PING_DATA'))
            config['data'] = custom_data
        except (json.JSONDecodeError, TypeError):
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
