# Testing Instructions for DragonVoiceProject

## Phase 1: Testing Basic Browser Automation

These instructions will help you test the basic browser automation functionality on your system without Dragon Medical One integration yet.

### Prerequisites

1. Make sure you have Python 3.x installed on your computer
2. Install the required Python packages:
   ```
   pip install pyautogui pygetwindow
   ```

### Testing Steps

1. **Prepare Your Browser Environment**:
   - Open Google Chrome on your computer
   - Open 3 separate Chrome windows (one for each screen)
   - Navigate each window to a search page (Google, Bing, etc.)
   - Make sure the search bar is visible in each window

2. **Run the Test Script**:
   - Open Command Prompt or PowerShell
   - Navigate to the DragonVoiceProject/src directory:
     ```
     cd path\to\DragonVoiceProject\src
     ```
   - Run the quick_test.py script:
     ```
     python quick_test.py
     ```
   - When prompted, enter a test search query (e.g., "test query for dragon voice project")
   - Confirm execution when asked
   - **IMPORTANT**: Don't touch your mouse or keyboard during the test!

3. **What Should Happen**:
   - The script will find all open Chrome windows
   - It will activate each window one by one
   - For each window, it will:
     - Clear any existing text in the search bar
     - Type your test query
     - Press Enter to execute the search
   - If successful, you should see your search query executed in each Chrome window

4. **If There Are Issues**:
   - Check if all Chrome windows have "Chrome" in their title
   - Make sure the search bars are active/focused in each window
   - Try adjusting the typing delay if the script is typing too fast:
     - Open quick_test.py in a text editor
     - Find the line `TYPING_DELAY = 0.05` and change it to a higher value (e.g., 0.1)
     - Save and try again

## Next Steps After Successful Testing

If the quick_test.py script works correctly, we can proceed with:

1. Setting up the Dragon Medical One integration methods
2. Creating a more user-friendly interface
3. Adding configuration options for your specific needs

Please report your test results, especially noting:
- How many Chrome windows were detected
- Whether typing worked correctly in each window
- Any error messages or unexpected behavior 