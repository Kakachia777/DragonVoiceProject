#!/usr/bin/env python3
"""
DragonVoiceProject - Chatbot Launcher Utility

This utility launches multiple Chrome windows with different titles for testing.
It creates empty Chrome windows with titles matching the configured chatbots,
allowing you to test the DragonVoiceProject without actually having access to
all the medical AI chatbots.

Usage:
    python launch_chatbots.py [--count NUMBER]

Options:
    --count NUMBER    Number of chatbots to launch (default: all)

Requirements:
    - webbrowser
    - subprocess
"""

import os
import sys
import time
import argparse
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DragonVoiceProject')

# List of all supported chatbots
CHATBOTS = [
    "Grok",
    "HealthUniverse", 
    "OpenEvidence",
    "Coral AI",
    "GlassHelp",
    "Bearly",
    "RobertLab",
    "Dr. Oracle",
    "DougallGPT",
    "ClinicalKey",
    "Pathway"
]

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DragonVoiceProject Chatbot Launcher")
    
    parser.add_argument("--count", type=int, default=len(CHATBOTS),
                        help=f"Number of chatbots to launch (default: {len(CHATBOTS)})")
    
    args = parser.parse_args()
    
    # Make sure count is within range
    if args.count < 1:
        args.count = 1
    elif args.count > len(CHATBOTS):
        args.count = len(CHATBOTS)
    
    return args

def launch_chrome_with_title(title):
    """
    Launch Chrome with a specific window title.
    
    Args:
        title: Title for the Chrome window
    """
    try:
        # Create a dummy HTML file with the chatbot title
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title} - Medical AI Chatbot Simulator</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background-color: #4285f4;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                }}
                .content {{
                    flex: 1;
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                }}
                .chat-area {{
                    flex: 1;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    padding: 20px;
                    margin-bottom: 20px;
                    overflow-y: auto;
                }}
                .input-area {{
                    display: flex;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    padding: 10px;
                }}
                .input-field {{
                    flex: 1;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 16px;
                }}
                .send-button {{
                    padding: 10px 20px;
                    margin-left: 10px;
                    background-color: #4285f4;
                    border: none;
                    border-radius: 4px;
                    color: white;
                    font-size: 16px;
                    cursor: pointer;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                {title} - Medical AI Chatbot Simulator
            </div>
            <div class="content">
                <div class="chat-area" id="chatArea">
                    <p><strong>System:</strong> Welcome to the {title} simulation window. This is a test window for the DragonVoiceProject.</p>
                </div>
                <div class="input-area">
                    <input type="text" class="input-field" id="inputField" placeholder="Type your message here...">
                    <button class="send-button" id="sendButton">Send</button>
                </div>
            </div>
            <script>
                document.getElementById('sendButton').addEventListener('click', function() {{
                    const inputField = document.getElementById('inputField');
                    const chatArea = document.getElementById('chatArea');
                    
                    if (inputField.value.trim() !== '') {{
                        // Add user message
                        const userMessage = document.createElement('p');
                        userMessage.innerHTML = '<strong>You:</strong> ' + inputField.value;
                        chatArea.appendChild(userMessage);
                        
                        // Add AI response
                        setTimeout(function() {{
                            const aiMessage = document.createElement('p');
                            aiMessage.innerHTML = '<strong>{title}:</strong> This is a simulated response. In a real chatbot, you would receive a medical AI response here.';
                            chatArea.appendChild(aiMessage);
                            
                            // Scroll to bottom
                            chatArea.scrollTop = chatArea.scrollHeight;
                        }}, 1000);
                        
                        // Clear input
                        inputField.value = '';
                    }}
                }});
                
                // Allow pressing Enter to send
                document.getElementById('inputField').addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter') {{
                        document.getElementById('sendButton').click();
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        # Create a temporary HTML file
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        html_file = os.path.join(temp_dir, f"{title.lower().replace(' ', '_')}.html")
        
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        # Launch Chrome with the HTML file
        file_url = f"file:///{os.path.abspath(html_file).replace(os.sep, '/')}"
        
        if sys.platform.startswith('win'):
            chrome_path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
            if not os.path.exists(chrome_path):
                chrome_path = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
            
            subprocess.Popen([chrome_path, f"--app={file_url}"])
        elif sys.platform.startswith('darwin'):  # macOS
            subprocess.Popen(['open', '-a', 'Google Chrome', file_url])
        else:  # Linux
            subprocess.Popen(['google-chrome', '--app=' + file_url])
        
        logger.info(f"Launched Chrome window for {title}")
        return True
    
    except Exception as e:
        logger.error(f"Error launching Chrome for {title}: {e}")
        return False

def main():
    """Main function to run the chatbot launcher."""
    args = parse_arguments()
    
    print("\n" + "=" * 60)
    print("DragonVoiceProject - Chatbot Launcher Utility")
    print("=" * 60)
    
    print(f"\nLaunching {args.count} chatbot windows for testing...")
    
    # Select chatbots to launch
    chatbots_to_launch = CHATBOTS[:args.count]
    
    launched_count = 0
    
    for chatbot in chatbots_to_launch:
        if launch_chrome_with_title(chatbot):
            launched_count += 1
            time.sleep(1)  # Short delay between launches
    
    print("\n" + "=" * 60)
    print(f"Launch complete. Launched {launched_count}/{args.count} chatbot windows.")
    print("=" * 60)
    
    print("\nYou can now use these windows to test the DragonVoiceProject.")
    print("To test with real queries, run:")
    print("python src/quick_test.py")
    
    # Keep the script running to maintain the HTML files
    print("\nPress Ctrl+C to close the script (HTML files will remain accessible)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting launcher. Chrome windows will remain open.")
        sys.exit(0)

if __name__ == "__main__":
    main() 