# Resume API Keep-Alive Service

## Overview

This is a Flask-based web application that provides a keep-alive service for maintaining API uptime on hosting platforms like Render. The application continuously pings a target Resume API endpoint to prevent it from going to sleep due to inactivity. It features a web dashboard for monitoring and configuration, along with standalone keep-alive functionality.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templating
- **UI Framework**: Bootstrap 5 with dark theme
- **Styling**: Custom CSS with responsive design
- **Icons**: Font Awesome 6.0

### Backend Architecture
- **Web Framework**: Flask (Python)
- **Production Server**: Gunicorn with process management
- **Keep-Alive Service**: Custom threading-based service class
- **Configuration Management**: Environment variable override system

### Data Storage Solutions
- **Logging**: File-based rotating logs with console output
- **History Storage**: In-memory list with configurable size limits
- **Configuration**: Python dictionaries with environment variable overrides

## Key Components

### Core Services
1. **KeepAliveService Class** (`keep_alive_service.py`)
   - Threaded background service for continuous API pinging
   - Configurable ping intervals and history management
   - Real-time status monitoring and statistics

2. **Flask Web Application** (`main.py`)
   - Dashboard interface for service monitoring
   - Manual ping functionality
   - Service start/stop controls

3. **Standalone Keep-Alive Script** (`keep_alive.py`)
   - Independent ping service that can run without the web interface
   - Backup service for maximum uptime assurance

4. **Service Runner** (`run_services.py`)
   - Process manager for running both web app and keep-alive service
   - Signal handling for graceful shutdowns

### Configuration System
- **Default Configuration** (`config.py`)
  - Predefined target URL, headers, and sample data
  - Environment variable override capabilities
  - Validation for critical parameters like ping intervals

### User Interface
- **Dashboard** (`templates/index.html`)
  - Real-time service status display
  - Ping history with success/failure statistics
  - Manual control buttons for service management

## Data Flow

1. **Configuration Loading**: System loads default configuration and applies environment variable overrides
2. **Service Initialization**: KeepAliveService starts with threaded background worker
3. **Ping Execution**: Regular HTTP POST requests sent to target API endpoint with resume evaluation data
4. **Status Tracking**: Response times, success/failure status stored in memory
5. **Dashboard Updates**: Web interface displays real-time statistics and history
6. **Log Management**: Rotating file logs capture all activities with configurable levels

## External Dependencies

### Target API
- **Endpoint**: `https://minor-ats-api.onrender.com/evaluate-resume`
- **Method**: POST with JSON payload containing resume evaluation data
- **Purpose**: Resume screening and evaluation service

### Python Libraries
- **Flask**: Web framework for dashboard interface
- **Requests**: HTTP client for API pinging
- **Threading**: Background service execution
- **Logging**: Comprehensive logging with rotation
- **Gunicorn**: Production WSGI server

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome**: Icon library
- **Custom CSS**: Responsive design enhancements

## Deployment Strategy

### Production Deployment
- **Server**: Gunicorn WSGI server on port 5000
- **Process Management**: Dual-service architecture (web + keep-alive)
- **Logging**: File-based logs with rotation to prevent disk space issues
- **Configuration**: Environment variable-based configuration for different environments

### Scalability Considerations
- **Memory Management**: Configurable history limits prevent memory growth
- **Rate Limiting**: Minimum 60-second ping intervals to prevent service abuse
- **Process Isolation**: Separate processes for web interface and keep-alive service

### Monitoring and Reliability
- **Health Checks**: Built-in status monitoring and statistics
- **Error Handling**: Comprehensive exception handling with detailed logging
- **Graceful Shutdowns**: Signal handling for clean service termination

## Changelog

- July 06, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.