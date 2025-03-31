#!/usr/bin/env python3
"""
Standalone keep-alive script that can be run independently of the Flask application.
This script continuously pings the Render server to keep it active.
"""

import requests
import time
import json
import logging
import os
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("keep_alive_standalone.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("keep_alive_standalone")

# Configuration
URL = "https://minor-ats-api.onrender.com/evaluate-resume"
HEADERS = {"Content-Type": "application/json"}
DATA = {
    "job_description": "Software Engineer with Python, AI, and Data Science skills",
    "resume_data": {
        "education": {"degree": "B.Tech in Computer Science", "university": "XYZ University"},
        "experience": [
            {"role": "Data Analyst", "organization": "TechCorp", "responsibilities": ["Analyzed data", "Built dashboards"]}
        ],
        "projects": [{"name": "AI Chatbot", "description": ["Built a chatbot using GPT"]}],
        "technical_skills": {"Programming": ["Python", "JavaScript"], "Data Science": ["Pandas", "NumPy"]}
    }
}
INTERVAL = int(os.environ.get('PING_INTERVAL', 180))  # Default: 3 minutes

def ping_server():
    """Send a ping request to the server"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{timestamp}] Pinging server at {URL}")
    
    try:
        response = requests.post(
            URL, 
            headers=HEADERS, 
            data=json.dumps(DATA),
            timeout=30
        )
        
        success = 200 <= response.status_code < 300
        if success:
            logger.info(f"[{timestamp}] Ping successful! Status code: {response.status_code}")
        else:
            logger.warning(f"[{timestamp}] Ping failed. Status code: {response.status_code}")
            
        # Only log the first 200 characters of the response to avoid huge logs
        response_text = response.text[:200]
        if len(response.text) > 200:
            response_text += "... (truncated)"
            
        logger.debug(f"Response: {response_text}")
        
        return success
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[{timestamp}] Error pinging server: {e}")
        return False

if __name__ == "__main__":
    logger.info(f"Starting standalone keep-alive script with interval of {INTERVAL} seconds")
    
    try:
        while True:
            ping_server()
            # Sleep in smaller chunks so it can be interrupted more gracefully
            for _ in range(int(INTERVAL / 10)):
                time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Keep-alive script stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")