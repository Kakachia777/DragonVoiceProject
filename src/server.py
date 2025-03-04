#!/usr/bin/env python3
"""
DragonVoiceProject - Server Component (Phase 2)

This script implements a Flask server that receives search queries and distributes
them to client machines. It provides endpoints for sending and retrieving queries.

Usage:
    python server.py [--port PORT] [--host HOST]

Options:
    --port PORT     Port to run the server on (default: 5000)
    --host HOST     Host to bind the server to (default: 0.0.0.0)

API Endpoints:
    POST /send_query        Receive a new search query
    GET  /get_query         Retrieve the most recent query
    GET  /check_dragon_file Scan for Dragon Medical One output (Phase 3)
    GET  /check_clipboard   Check clipboard for Dragon output (Phase 3)

Requirements:
    - Flask
    - pyperclip (for Phase 3)
"""

import os
import sys
import time
import json
import argparse
import logging
from datetime import datetime
try:
    from flask import Flask, request, jsonify
except ImportError:
    print("Error: Flask package not found.")
    print("Please install Flask using: pip install flask")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('dragon_server')

# Initialize Flask app
app = Flask(__name__)

# Global variables
last_query = None
last_query_timestamp = None
last_dragon_file_content = None

# Configuration (defaults, can be overridden via command line args)
config = {
    "host": "0.0.0.0",
    "port": 5000,
    "dragon_file_path": "C:/dragon_query.txt",
    "dragon_file_check_interval": 1.0,  # seconds
}

class QueryManager:
    """Manages query storage and retrieval."""
    
    @staticmethod
    def store_query(query_text, source="api"):
        """Store a new query."""
        global last_query, last_query_timestamp
        
        if not query_text or not isinstance(query_text, str):
            logger.error(f"Invalid query: {query_text}")
            return False
        
        # Store query with metadata
        last_query = query_text.strip()
        last_query_timestamp = datetime.now()
        
        logger.info(f"New query stored: '{last_query}' (source: {source})")
        return True
    
    @staticmethod
    def get_latest_query():
        """Retrieve the latest query with metadata."""
        if last_query is None:
            return None
        
        return {
            "query": last_query,
            "timestamp": last_query_timestamp.isoformat() if last_query_timestamp else None
        }


# API Endpoints
@app.route('/send_query', methods=['POST'])
def send_query():
    """
    Endpoint to receive a new search query.
    
    Accepts form data with 'query' parameter containing the search text.
    """
    try:
        # Extract query from request
        if request.is_json:
            data = request.get_json()
            query = data.get('query', '')
        else:
            query = request.form.get('query', '')
        
        if not query:
            return jsonify({"error": "Missing query parameter"}), 400
        
        # Store the query
        if QueryManager.store_query(query, source="api"):
            return jsonify({
                "status": "success", 
                "message": "Query received", 
                "query": query
            })
        else:
            return jsonify({"error": "Failed to store query"}), 500
            
    except Exception as e:
        logger.error(f"Error in send_query: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/get_query', methods=['GET'])
def get_query():
    """
    Endpoint to retrieve the most recent query.
    
    Returns the query text along with its timestamp.
    """
    try:
        query_data = QueryManager.get_latest_query()
        
        if query_data is None:
            return jsonify({"message": "No query available"}), 204
        
        return jsonify(query_data)
            
    except Exception as e:
        logger.error(f"Error in get_query: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/check_dragon_file', methods=['GET'])
def check_dragon_file():
    """
    Endpoint to check for Dragon Medical One output in a text file.
    This is a placeholder for Phase 3 functionality.
    """
    global last_dragon_file_content
    
    try:
        # Check if the Dragon output file exists
        if not os.path.exists(config["dragon_file_path"]):
            return jsonify({
                "status": "error",
                "message": f"Dragon output file not found at {config['dragon_file_path']}"
            }), 404
        
        # Read the file content
        with open(config["dragon_file_path"], 'r') as f:
            content = f.read().strip()
        
        # Check if content has changed since last check
        if content and content != last_dragon_file_content:
            last_dragon_file_content = content
            
            # Store the new query from the file
            QueryManager.store_query(content, source="dragon_file")
            
            return jsonify({
                "status": "success",
                "message": "New Dragon query detected",
                "query": content
            })
        
        return jsonify({
            "status": "success",
            "message": "No new Dragon query detected"
        })
            
    except Exception as e:
        logger.error(f"Error in check_dragon_file: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/check_clipboard', methods=['GET'])
def check_clipboard():
    """
    Endpoint to check for Dragon Medical One output in the clipboard.
    This is a placeholder for Phase 3 functionality.
    """
    try:
        # In Phase 3, we would import pyperclip and check the clipboard
        return jsonify({
            "status": "not_implemented",
            "message": "Clipboard checking will be implemented in Phase 3"
        }), 501
            
    except Exception as e:
        logger.error(f"Error in check_clipboard: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """
    Endpoint to check server status.
    """
    return jsonify({
        "status": "running",
        "version": "1.0",
        "query_count": 1 if last_query else 0,
        "uptime": "N/A"  # Would be implemented in a production version
    })


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Dragon Voice Project Server')
    
    parser.add_argument('--port', type=int, default=config['port'],
                        help=f'Port to run the server on (default: {config["port"]})')
    
    parser.add_argument('--host', type=str, default=config['host'],
                        help=f'Host to bind the server to (default: {config["host"]})')
    
    parser.add_argument('--dragon-file', type=str, default=config['dragon_file_path'],
                        help=f'Path to Dragon output file (default: {config["dragon_file_path"]})')
    
    return parser.parse_args()


def main():
    """Main function."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Update configuration from arguments
    config['port'] = args.port
    config['host'] = args.host
    config['dragon_file_path'] = args.dragon_file
    
    # Print startup banner
    print("\n" + "=" * 60)
    print("DragonVoiceProject - Server (Query Distribution)")
    print("=" * 60)
    print(f"\nStarting server on {config['host']}:{config['port']}")
    print(f"Dragon file path: {config['dragon_file_path']}")
    print("\nAPI Endpoints:")
    print("  POST /send_query        - Send a new query")
    print("  GET  /get_query         - Retrieve the latest query")
    print("  GET  /check_dragon_file - Check Dragon output file (Phase 3)")
    print("  GET  /check_clipboard   - Check clipboard (Phase 3)")
    print("  GET  /status            - Check server status")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the Flask server
    app.run(host=config['host'], port=config['port'], debug=False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped by user (Ctrl+C).")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1) 