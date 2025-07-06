import os
import json
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from keep_alive_service import KeepAliveService
from config import get_config, save_config

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Initialize the keep-alive service with default configuration
service_config = get_config()
keep_alive_service = KeepAliveService(service_config)

@app.route('/')
def index():
    """Render the dashboard"""
    status = keep_alive_service.get_status()
    history = keep_alive_service.ping_history
    
    # Reverse the list to display newest entries first
    history = list(reversed(history))
    
    # Calculate some basic statistics
    success_count = sum(1 for entry in keep_alive_service.ping_history if entry.get('success'))
    failure_count = len(keep_alive_service.ping_history) - success_count
    
    if keep_alive_service.ping_history:
        success_rate = (success_count / len(keep_alive_service.ping_history)) * 100
    else:
        success_rate = 0
    
    return render_template('index.html', 
                          status=status, 
                          history=history, 
                          config=service_config,
                          stats={
                              'success_count': success_count,
                              'failure_count': failure_count,
                              'success_rate': success_rate
                          })

@app.route('/api/ping', methods=['POST'])
def manual_ping():
    """Manually trigger a ping to the server"""
    result = keep_alive_service.ping_server()
    return jsonify(result)

@app.route('/api/service/start', methods=['POST'])
def start_service():
    """Start the keep-alive service"""
    result = keep_alive_service.start()
    if result:
        flash('Service started successfully', 'success')
    else:
        flash('Service is already running', 'warning')
    return redirect(url_for('index'))

@app.route('/api/service/stop', methods=['POST'])
def stop_service():
    """Stop the keep-alive service"""
    result = keep_alive_service.stop()
    if result:
        flash('Service stopped successfully', 'success')
    else:
        flash('Service is not running', 'warning')
    return redirect(url_for('index'))

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update the service configuration"""
    # Stop the service before updating config
    was_running = keep_alive_service.is_running()
    if was_running:
        keep_alive_service.stop()
    
    # Get the form data
    try:
        new_config = service_config.copy()
        new_config['url'] = request.form.get('url', service_config['url'])
        new_config['interval'] = int(request.form.get('interval', service_config['interval']))
        
        # Handle HTTP method
        new_config['method'] = request.form.get('method', service_config.get('method', 'POST')).upper()
        
        # Handle custom headers
        headers_json = request.form.get('headers', '{}')
        try:
            custom_headers = json.loads(headers_json) if headers_json.strip() else {}
            # Merge with default headers
            merged_headers = service_config.get('headers', {}).copy()
            merged_headers.update(custom_headers)
            new_config['headers'] = merged_headers
        except json.JSONDecodeError:
            flash('Invalid JSON in headers field. Using default headers.', 'warning')
            new_config['headers'] = service_config.get('headers', {})
        
        # Handle payload based on type
        payload_type = request.form.get('payload_type', 'json')
        payload_content = request.form.get('payload', '')
        
        if payload_type == 'none' or not payload_content.strip():
            new_config['data'] = None
        elif payload_type == 'json':
            try:
                new_config['data'] = json.loads(payload_content) if payload_content.strip() else None
            except json.JSONDecodeError:
                flash('Invalid JSON in payload field. Using default payload.', 'warning')
                new_config['data'] = service_config.get('data')
        elif payload_type == 'form':
            # Keep as string for form data
            new_config['data'] = payload_content.strip() if payload_content.strip() else None
        else:
            # Default to existing data
            new_config['data'] = service_config.get('data')
        
        # Ensure interval is at least 60 seconds
        if new_config['interval'] < 60:
            new_config['interval'] = 60
            flash('Interval set to minimum value of 60 seconds', 'warning')
        
        # Update the service config
        keep_alive_service.update_config(new_config)
        
        # Save the configuration
        save_config(new_config)
        
        # Restart if it was running before
        if was_running:
            keep_alive_service.start()
            
        flash('Configuration updated successfully', 'success')
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        flash(f'Error updating configuration: {e}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """Clear the ping history"""
    keep_alive_service.ping_history = []
    flash('Ping history cleared', 'success')
    return redirect(url_for('index'))

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the current service status"""
    status = keep_alive_service.get_status()
    return jsonify(status)

# Flag to track if service has been started
service_started = False

# Set up an initialization function to start the service on first request
@app.before_request
def start_service_on_startup():
    global service_started
    if not service_started and not keep_alive_service.is_running():
        keep_alive_service.start()
        service_started = True
        logger.info("Keep-alive service started automatically on application startup")

if __name__ == "__main__":
    # Start the service before starting the web server
    if not keep_alive_service.is_running():
        keep_alive_service.start()
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
