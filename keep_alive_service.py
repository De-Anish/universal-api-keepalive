import requests
import time
import json
import logging
import threading
from datetime import datetime
from logging.handlers import RotatingFileHandler

class KeepAliveService:
    def __init__(self, config):
        """
        Initialize the keep-alive service with the provided configuration
        
        Args:
            config (dict): Configuration parameters for the service
        """
        self.url = config['url']
        self.headers = config['headers']
        self.data = config['data']
        self.interval = config['interval']
        self.running = False
        self.thread = None
        self.ping_history = []
        self.max_history = config.get('max_history', 100)
        
        # Setup logging
        self._setup_logging(config.get('log_level', logging.INFO), 
                           config.get('log_file', 'keep_alive.log'))
        
    def _setup_logging(self, log_level, log_file):
        """Set up the logging configuration"""
        self.logger = logging.getLogger("keep_alive")
        self.logger.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=5)
        file_handler.setLevel(log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def ping_server(self):
        """
        Send a ping request to the server and record the result
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {
            "timestamp": timestamp,
            "success": False,
            "status_code": None,
            "response": None,
            "error": None
        }
        
        try:
            self.logger.info(f"Pinging server at {self.url}")
            
            # Get HTTP method (default to POST for backward compatibility)
            method = getattr(self, 'method', 'POST').upper()
            
            # Prepare request data based on Content-Type and data format
            request_kwargs = {
                'url': self.url,
                'headers': self.headers,
                'timeout': 30
            }
            
            # Handle data based on method and data type
            if method != 'GET' and self.data is not None:
                content_type = self.headers.get('Content-Type', 'application/json')
                
                if isinstance(self.data, str):
                    # String data (form data or plain text)
                    request_kwargs['data'] = self.data
                elif isinstance(self.data, dict):
                    # Dictionary data
                    if 'application/json' in content_type:
                        request_kwargs['data'] = json.dumps(self.data)
                    elif 'application/x-www-form-urlencoded' in content_type:
                        request_kwargs['data'] = self.data  # requests will handle form encoding
                    else:
                        request_kwargs['data'] = json.dumps(self.data)  # Default to JSON
                else:
                    # Other data types
                    request_kwargs['data'] = str(self.data)
            
            # Make the request using the specified method
            response = requests.request(method, **request_kwargs)
            
            result["success"] = 200 <= response.status_code < 300
            result["status_code"] = response.status_code
            
            # Limit response content size to prevent memory issues
            response_text = response.text[:1000]
            if len(response.text) > 1000:
                response_text += "... (truncated)"
                
            result["response"] = response_text
            
            self.logger.info(f"Ping result: Status {response.status_code}")
            if not result["success"]:
                self.logger.warning(f"Unsuccessful response: {response_text}")
                
        except requests.exceptions.RequestException as e:
            result["error"] = str(e)
            self.logger.error(f"Error pinging server: {e}")
        
        # Add to history and maintain max size
        self.ping_history.append(result)
        if len(self.ping_history) > self.max_history:
            self.ping_history.pop(0)
            
        return result
    
    def _service_loop(self):
        """Main service loop that runs in a separate thread"""
        self.logger.info(f"Keep-alive service started. Interval: {self.interval} seconds")
        
        while self.running:
            try:
                self.ping_server()
                # Sleep in small intervals to allow for cleaner shutdown
                for _ in range(int(self.interval / 0.5)):
                    if not self.running:
                        break
                    time.sleep(0.5)
            except Exception as e:
                self.logger.error(f"Unexpected error in service loop: {e}")
                time.sleep(5)  # Short delay to prevent rapid error loops
    
    def start(self):
        """Start the keep-alive service in a background thread"""
        if self.running:
            self.logger.warning("Service is already running")
            return False
            
        self.running = True
        self.thread = threading.Thread(target=self._service_loop)
        self.thread.daemon = True  # Allow the program to exit even if the thread is running
        self.thread.start()
        return True
    
    def stop(self):
        """Stop the keep-alive service"""
        if not self.running:
            self.logger.warning("Service is not running")
            return False
            
        self.logger.info("Stopping keep-alive service")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=10)  # Wait for thread to terminate
            
        self.logger.info("Keep-alive service stopped")
        return True
    
    def is_running(self):
        """Check if the service is currently running"""
        return self.running and self.thread and self.thread.is_alive()
    
    def update_config(self, config):
        """Update service configuration"""
        if self.running:
            self.logger.warning("Cannot update configuration while service is running")
            return False
            
        self.url = config.get('url', self.url)
        self.headers = config.get('headers', self.headers)
        self.data = config.get('data', self.data)
        self.interval = config.get('interval', self.interval)
        self.max_history = config.get('max_history', self.max_history)
        
        self.logger.info("Configuration updated")
        return True
        
    def get_status(self):
        """Get the current status of the service"""
        return {
            "running": self.is_running(),
            "url": self.url,
            "interval": self.interval,
            "last_ping": self.ping_history[-1] if self.ping_history else None,
            "history_count": len(self.ping_history)
        }
