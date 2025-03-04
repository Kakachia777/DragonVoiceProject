# Dragon Medical One Multi-Computer Voice Control Project - Quick & Easy Guide

**Version:** 1.0 (Simplified Structure + Project Management Info)
**Date:** March 4, 2025

---

**Quick Navigation**

*   [⚡️ Quick Start - Your FASTEST Path to Testing](#quick-start---your-fastest-path-to-testing)
*   [🎯 Project Goal - What's This For?](#11-project-goal---what-s-this-for)
*   [📂 Project Files - What's in Each File?](#2-project-files---what-s-in-each-file)
*   [🛠️ Software You NEED - Install These First](#3-software-you-need---install-these-first)
*   [⚙️ Setup - Step-by-Step - Get it Working](#4-setup---step-by-step---get-it-working)
*   [✅ Testing - Quick Checks - Is it GO?](#5-testing---quick-checks---is-it-go)
*   [📊 Project Management Information](#6-project-management-information) **(NEW SECTION)**
*   [⚠️ Troubleshooting - Fix Common Problems](#7-troubleshooting---fix-common-problems)
*   [🚀 Tips - Get the BEST Results](#14-tips---get-the-best-results)
*   [❓ FAQ - Quick Answers to Your Questions](#15-frequently-asked-questions-faq---quick-answers)
*   [👨‍💻 Push to GitHub - For Programmers](#push-to-github---for-programmers)

---

## ⚡️ Quick Start - Your FASTEST Path to Testing

**Okay, let's get you started *right now*. Here's what you should do first:**

1.  **Go to "Software You Need" section below.**
    *   **Install Python 3.x** on your main computer (where you'll run `server.py`).  Make sure to check "Add to PATH"!
    *   **Install Python 3.x** on **one other computer** (for now, just one client to test).  Again, check "Add to PATH"!

2.  **Go to "Setup - Step-by-Step" section below.**
    *   Follow **Step A "Configure Client Computers"** but only do it for that **one client computer** you set up in step 1.  You'll need to find the IP address of your main computer (Dragon PC) and put it in `src/client.py` on the client computer.
    *   Follow **Step B "Run the Server (Dragon PC)"** on your main computer.  Start `src/server.py` in Command Prompt/Terminal.
    *   Follow **Step C "Run Clients (Each Client Computer)"** but only do it for that **one client computer**. Start `src/client.py` in Command Prompt/Terminal.

3.  **Go to "Testing - Quick Checks" section below.**
    *   Perform **"Phase 1 Test (One Computer Typing)"** on your main computer.  Does `src/quick_test.py` type into Chrome on that computer?  If YES, great! If NO, check "Troubleshooting".
    *   Perform **"Phase 2 Test (Network Search - Multiple Computers)"**.  Use the "online POST request sender" method to send a test query to your main computer's IP address.
    *   **Check:** Does the test query get typed into Chrome on that **one client computer** you set up?  If YES, awesome!  If NO, check "Troubleshooting".

**If you get Phase 2 test working with one client computer, you've made great progress!  Then you can:**

*   Set up `src/client.py` on your *other* client computers (repeat "Configure Client Computers" and "Run Clients" for each).
*   Test again with *multiple* client computers using "Phase 2 Test".

**This "Quick Start" is just to get you going with the basics.  For more details and troubleshooting, use the rest of this guide!**

---

## 🎯 1. Project Overview - What's This For?

### 1.1. Project Goal: Voice-Controlled Multi-Browser Query System - Research Efficiency Unleashed!

Imagine this: You are conducting research and need to search for the same information across multiple online databases and search engines simultaneously.  Instead of tediously typing or copy-pasting your search query into each website, one by one, what if you could simply **speak your query once**, and have it instantly appear and be searched across all your research computers?

That's the power of the **Dragon Medical One Multi-Computer Voice Control Project!**  Our goal is to create a system that will:

*   **Transform your voice into a powerful command center for research.**
*   **Eliminate repetitive manual work and save you countless hours.**
*   **Boost your research efficiency and speed to a whole new level.**

Specifically, this system will enable you to:

*   **Dictate a research query ONCE using Dragon Medical One** (or similar voice recognition software) on a designated "server" computer - your voice becomes the input!
*   **Automatically distribute this dictated query as text over your local network to multiple "client" computers** - your query travels instantly!
*   **On each "client" computer, automatically populate the query into the search bars of multiple open Chrome browser windows** - browsers are ready to search!
*   **Initiate the search (press "Enter") in all those browser windows simultaneously** - searches start with a single voice command!

This automation will replace the slow and error-prone manual process of typing or copy-pasting the same search query into multiple browsers across multiple machines, significantly enhancing research efficiency and speed, especially for tasks requiring cross-referencing information across numerous online resources.

### 1.2. Project Status: In Progress - Building the Networked Voice Query Revolution!

As of {{ Date: March 3, 2025 }}, the Dragon Medical One Multi-Computer Voice Control Project is actively **in progress**.  We are building this system step-by-step, phase by phase:

*   **Phase 1: Single Computer Demo - Browser Automation Core (✅ Completed):** We have successfully built and tested the core browser automation functionality.  The `src/quick_test.py` script demonstrates that we can reliably control Chrome browsers and type text into search bars on a single computer.  This is the foundation!
*   **Phase 2: Networked Query Distribution - Connecting the Computers (🚧 In Progress):** We are currently focused on implementing and testing the network communication and query distribution system.  The `src/server.py` and `src/client.py` scripts are being developed to enable the server to send queries over the network and clients to receive and act upon them.  Basic network communication and browser automation on client computers are being actively worked on and tested.  We are in the heart of making the multi-computer magic happen!
*   **Phase 3: Dragon Medical One Integration - Voice Control Unleashed (Planned):**  The next exciting phase will be to integrate Dragon Medical One.  We will connect Dragon Medical One to our system so that your voice dictation can directly trigger the query distribution process.  This is where the voice control truly comes to life!
*   **Phase 4: Testing, Refinement, and Polish - Making it Robust and User-Friendly (Planned):**  The final phase will be dedicated to rigorous testing in real-world scenarios, making the system robust and reliable, handling errors gracefully, and potentially adding user interface enhancements to make it even easier to use.  We will polish and refine the system to ensure it's a truly valuable and user-friendly tool.

## 📂 2. Project Files - What's in Each File?

Let's take a closer look at the files that make up the Dragon Medical One Multi-Computer Voice Control Project.  Understanding the purpose of each file will help you navigate the project and understand how it all works together:

*   **`src/quick_test.py` - Phase 1: Single Computer Browser Automation Tester:**
    *   **(Think of it as: The "Single Computer Typing Test Script")**
    *   **Purpose:**  This Python script is your **single-computer testing tool**.  It's designed to quickly verify if the fundamental browser automation - the ability to type into Chrome windows - is working correctly on your local machine.  It's like a mini-experiment to test the core typing mechanism before we involve the network.
    *   **Functionality:**
        *   **Simulated Voice Input:**  It doesn't actually use voice. Instead, it simply asks you to **type a search query directly into the Command Prompt/Terminal window** when you run the script.  This is just for testing purposes.
        *   **Chrome Window Detection:** It uses the `pygetwindow` library to automatically find all currently open **Google Chrome browser windows** on your computer.
        *   **Automated Typing:**  It uses the `pyautogui` library to simulate keyboard input.  It will automatically:
            *   **Activate each Chrome window** one by one, bringing it to the front.
            *   **Clear any existing text** in the search bar of each window (by pressing Ctrl+A and Delete).
            *   **Type the search query** that you entered in the Command Prompt/Terminal into the search bar.
            *   **Press the "Enter" key** in each window to initiate the search.
        *   **Output:** It prints a message to the Command Prompt/Terminal indicating how many Chrome windows it found.
        *   **No Network Involved:**  This script runs entirely on a single computer and does not involve any network communication.
        *   **Example Usage Scenario:** You would use `src/quick_test.py` when you want to:
            *   **Initially test if browser automation is working on your computer at all.**
            *   **Troubleshoot browser automation issues on a single machine before involving the network complexity.**
            *   **Demonstrate the basic typing functionality without needing multiple computers.**
    *   **Usage:**  You will run `src/quick_test.py` **on any computer** where you have set up the project files.  It's your first step to make sure the basic typing automation is working before you move to network testing.  See Section 5.1 "Phase 1 Testing: Single Computer Browser Typing (`src/quick_test.py`)" for detailed testing instructions.

*   **`src/server.py` - Phase 2: Networked Query Distribution - The Central Server "Brain":**
    *   **(Think of it as: The "Query Distribution Server" or the "Central Brain")**
    *   **Purpose:**  This Python script is the **server-side component** of the project.  It's the "brain" of the system, responsible for receiving your voice query and distributing it to all the client computers over the network.  You will run this script on the designated **SERVER COMPUTER**, which is intended to be the computer where you use Dragon Medical One.
    *   **Functionality:**
        *   **Web Server (Powered by Flask):**  It uses the **Flask** library, a lightweight and easy-to-use Python web framework, to create a simple **web server application**.  Think of it as setting up a mini-website that runs on your server computer, but it's designed for programs to talk to, not for humans to browse in a web browser.
        *   **Receives Queries (Endpoint `/send_query`):**  It creates a special "address" or **endpoint** on this mini-website called `/send_query`.  This endpoint is designed to **receive search queries** from other computers or tools.  It's like a mailbox where queries can be sent *to* the server.  It's set up to receive queries using **`POST` requests**, which is a standard way for computers to send data to web servers.
            *   **Analogy: Think of a Post Office:** The `/send_query` endpoint is like the "Incoming Mail" window at a post office.  Other computers (or tools) can "mail" their search queries to this address.
        *   **Stores the Last Query (Variable `last_query`):** When the server receives a query at the `/send_query` endpoint, it **stores the query text** in a temporary storage location - a Python variable named `last_query`.  It only remembers the *most recent* query it has received.
            *   **Analogy: Think of a Temporary Notepad:** The `last_query` variable is like a small notepad where the server jots down the latest query it received.  It overwrites the previous query each time a new one arrives.
        *   **Provides Query Access (Endpoint `/get_query`):** It creates another endpoint called `/get_query`.  This endpoint allows other computers (specifically, the client computers) to **ask the server "What is the latest query?"** and the server will respond by sending back the text of the `last_query` it has stored.  This endpoint is designed to be accessed using **`GET` requests**, which is a standard way for computers to *request* data from web servers.
            *   **Analogy: Think of an "Information Window":** The `/get_query` endpoint is like an "Information Window" at the post office.  Client computers can come to this window and ask, "What's the latest query?", and the server will give them the information from its "notepad" (`last_query`).
        *   **Network Communication (Port 5000):** The server program **listens for network requests** (both `/send_query` and `/get_query` requests) on a specific "doorway" or **port** on your computer's network connection.  By default, it uses **port `5000`**.  Think of a port as a specific channel for network communication.  Client computers will need to know this port number to talk to the server.
            *   **Analogy: Think of a Door Number:** Port `5000` is like the "door number" of the server program on your network.  Client computers need to know this "door number" to knock on the right door and talk to the server.
        *   **Output:** When you run `src/server.py`, it will print a message to the Command Prompt/Terminal indicating that the server is starting and running, usually showing the address ` * Running on http://0.0.0.0:5000 `.
        *   **No Browser Automation:** The `src/server.py` script itself does *not* perform any browser automation.  Its sole job is to receive and distribute queries over the network.  The browser automation is handled by the `src/client.py` scripts running on the client computers.
        *   **Example Usage Scenario:** You will run `src/server.py` on your Dragon Medical One computer and leave it running in the background.  It will then be ready to receive voice queries (in Phase 3) and distribute them to client computers.  During Phase 2 testing, you will use tools like web browsers or online POST request senders to manually send test queries *to* the server to simulate voice input and test the network distribution.
    *   **Usage:** You will run `src/server.py` **on the designated SERVER COMPUTER** (the Dragon Medical One computer).  It will run continuously in the background, waiting to receive and distribute voice queries.  You need to keep the Command Prompt/Terminal window where you run `src/server.py` open and running for the server to work.  See Section 4.2 "Run the Server Program (`src/server.py`) - Starting the "Brain"" for detailed instructions on how to run the server.

*   **`src/client.py` - Phase 2: Networked Query Distribution - The Client "Helper" Programs:**
    *   **(Think of them as: The "Browser Automation Helpers" or the "Query Typers")**
    *   **Purpose:** This Python script is the **client-side component**.  You will run `src/client.py` on **EACH CLIENT COMPUTER** - every computer where you want the automated browser searching to happen.  These client programs are the "helpers" that do the actual work of listening for queries and typing them into browsers.
    *   **Functionality:**
        *   **Client Listener (Continuous Background Process):**  When you run `src/client.py`, it starts running **continuously in the background**.  It's like a little program that is always "awake" and listening for instructions from the server.  It will keep running until you manually stop it (by pressing Ctrl+C in the Command Prompt/Terminal window).
        *   **Network Communication (Requests Queries from Server):**  Each client program **periodically checks in with the server** (the `src/server.py` program) to see if there is a new search query available.  It does this by sending a **`GET` request** to the server's `/get_query` endpoint.  It's like the client asking the server, "Hey Server, do you have a new query for me?".  It uses the `requests` library to handle this network communication, making it easy to send web requests and receive responses.
            *   **Analogy: Think of a Student Checking for Homework:** Each client program is like a student who periodically checks with the teacher (the server) to see if there is new homework (a new query) assigned.
        *   **Query Detection (Checks for New Queries - Prevents Redundant Typing):** When a client program gets a response from the server, it **compares the query it just received with the query it processed previously**.  It only takes action if it detects a *new* query that it hasn't processed yet.  This is important to prevent the client from re-typing the *same* query into the browsers over and over again if the server keeps sending the same query multiple times.  It ensures that the browser automation only happens when there is a *genuinely new* query to process.
        *   **Browser Automation (Types Query into Chrome - The Core Action):** If a client program detects a *new* query from the server, it then performs the browser automation magic - this is the main action of the client program!  It uses the `pyautogui` and `pygetwindow` libraries to:
            *   **Find Chrome Windows:** It uses `pygetwindow` to automatically find all currently open **Google Chrome browser windows** on the *client computer* where it is running.  It looks for windows that have "Chrome" in their window title.
            *   **Type the Query into Browsers:**  It uses `pyautogui` to simulate keyboard input.  It will automatically:
                *   **Activate each Chrome window** one by one, bringing it to the front.
                *   **Clear the search bar:**  It clears any existing text in the search bar of each window (by simulating pressing Ctrl+A to select all text, and then pressing the Delete key).
                *   **Type the received query text:** It types the text of the new search query that it received from the server into the cleared search bar.
                *   **Press "Enter" to Start Search:**  It simulates pressing the "Enter" key in each window to initiate the search on the website in that browser window.
        *   **Background Threading (Keeps Client Running Smoothly):**  To ensure that the client program can run continuously in the background without freezing up or blocking other operations on the client computer, it uses **Python's `threading` module**.  The query checking (talking to the server) and browser automation (typing into Chrome) tasks are run in a **separate background thread**.  This is important because browser automation can sometimes take a little bit of time, and we don't want the client program to become unresponsive while it's doing the typing.  Background threading allows the main part of the client program to keep running smoothly and continue listening for new queries from the server, even while the browser automation is happening in the background.
        *   **Output:** When you run `src/client.py`, it will print a message to the Command Prompt/Terminal indicating that the client program is starting and running: `Client running. Press Ctrl+C to stop.`.  It will also print messages to the terminal whenever it receives a new query from the server: `New query received: ...`.  If there are any errors during network communication or browser automation, it will also print error messages to the terminal to help with troubleshooting.
        *   **Example Usage Scenario:** You will run `src/client.py` on every computer where you want the automated browser searching to happen.  You will leave these client programs running in the background on each client computer.  They will then automatically listen for queries from the server and perform the browser automation whenever a new query is available.  You need to configure the `SERVER_URL` variable in the `src/client.py` file on each client computer to tell it where to find the server.
    *   **Usage:** You will run `src/client.py` **on EVERY CLIENT COMPUTER** where you want automated browser searching to happen.  You need to run a separate copy of `src/client.py` on each client machine.  Each client program will independently listen for queries from the server and automate browser typing on its own computer.  You need to keep the Command Prompt/Terminal window where you run `src/client.py` open and running on each client computer for the client program to work.  See Section 4.3 "Run the Client Programs (`src/client.py`) - Starting the "Helpers" on Each Computer" for detailed instructions on how to run the client programs.

*   **`docs/README.md` - The Documentation Manual (You are Reading It Now!):**
    *   **(Think of it as: The "Instruction Manual" or "Project Guide")**
    *   **Purpose:** This file, `docs/README.md`, is the **primary documentation** for the entire Dragon Medical One Multi-Computer Voice Control Project.  It's your comprehensive guide to understanding, setting up, using, troubleshooting, and extending the system.
    *   **Content:**  As you can see, it contains detailed information about every aspect of the project, including:
        *   Project goals and motivation
        *   Detailed descriptions of each file and program component
        *   Ultra-detailed, step-by-step setup instructions
        *   Exhaustive testing and usage guides for each phase of the project
        *   Comprehensive troubleshooting tips and solutions for common problems
        *   Developer documentation for those who want to customize or extend the system
        *   Roadmap for future enhancements and development
        *   Contact information and notes
        *   And much more!

*   **`requirements.txt` - Python Package List (The "Ingredients List"):**
    *   **(Think of it as: The "Python Package Ingredients List")**
    *   **Purpose:** This file is a standard Python file that acts as a **list of all the extra Python packages** (libraries, tools) that are *required* for the Python scripts (`src/quick_test.py`, `src/server.py`, `src/client.py`) to run correctly.  It's like a recipe ingredient list for Python.
    *   **Functionality:**  It allows for easy installation of all necessary packages using `pip` (Python's package installer).
    *   **Usage:**  You (or other users) can use this file to quickly install all project dependencies by running the command `pip install -r requirements.txt` in the `DragonVoiceProject` directory.  This ensures that everyone has the correct versions of all the required Python packages installed.  You usually don't need to edit this file directly.  It's typically created or updated automatically using the command `pip freeze > requirements.txt` after you have installed all the packages manually.

## 🛠️ 3. Software You NEED - Install These First

To use the Dragon Medical One Multi-Computer Voice Control Project, you need to install specific software on **each computer** that will be part of the system (both the server computer and all client computers).  Follow these ultra-detailed steps:

### 3.1. Install Python 3.x - The Engine for Our Scripts

Python is the programming language used to create the scripts for this project. You need to install Python version 3 or newer on every computer.

1.  **Go to the Python Download Website:** Open your web browser (like Chrome, Firefox, Edge, Safari) and go to the official Python download page:  [https://www.python.org/downloads/](https://www.python.org/downloads/)

2.  **Download Python 3.x Installer:**
    *   Look for the button or link to download the latest version of **Python 3.x** (it will be something like "Python 3.12.x" or a higher version number).  **Do NOT download Python 2.x!**
    *   Click the button to download the installer for your operating system (Windows, macOS, Linux).  The website should automatically detect your operating system and offer the correct installer.

3.  **Run the Python Installer:**
    *   Once the installer file is downloaded, find it on your computer (usually in your "Downloads" folder) and **double-click** to run it.
    *   **Important Step for Windows Users:**  When the installer window opens, **look for a checkbox that says "Add Python 3.x to PATH" or "Add to environment variables" at the bottom of the installer window.**  **MAKE SURE THIS CHECKBOX IS CHECKED!** This is crucial for Python to work correctly from the command line.  If you miss this step, you may need to reinstall Python.
    *   Follow the on-screen instructions in the installer to complete the Python installation.  Usually, you can just click "Next" or "Install" through most of the steps, accepting the default settings.
    *   Wait for the installation to finish.  You may see a "Setup was successful" message when it's done.

4.  **Verify Python Installation (Optional but Recommended):**
    *   **Open a Command Prompt (Windows) or Terminal (macOS/Linux):**
        *   **Windows:** Search for "cmd" in the Windows search bar and press Enter to open Command Prompt.
        *   **macOS:** Open "Finder", go to "Applications", then "Utilities", and double-click "Terminal".
        *   **Linux:**  Open your terminal application (usually by pressing Ctrl+Alt+T or searching for "Terminal" in your application menu).
    *   **Type the following command EXACTLY as written and press Enter:**
        ```bash
        python --version
        ```
        or (if `python` command doesn't work, try):
        ```bash
        python3 --version
        ```
    *   **Check the Output:** If Python is installed correctly and added to PATH, you should see output that shows the Python version number, like "Python 3.12.x" or similar.  If you see an error message like "'python' is not recognized..." or "'python3' is not recognized...", it means Python is not correctly installed or not added to your system's PATH.  Go back to Step 3 and make sure you checked the "Add Python to PATH" option during installation, or try reinstalling Python.

**Repeat these Python installation steps on EVERY COMPUTER (server and all clients) that will be part of your voice control system.**

### 3.2. Install Required Python Packages - Adding Extra Tools

Our Python scripts need some extra tools (packages) to do things like control the browser, communicate over the network, etc.  You need to install these packages using `pip`, Python's package installer.

1.  **Open a Command Prompt (Windows) or Terminal (macOS/Linux) on EACH COMPUTER:**  (Same as in Step 4 of Python installation verification above).

2.  **Navigate to the `DragonVoiceProject` Folder:**  Use the `cd` command to change the directory in your Command Prompt/Terminal to the `DragonVoiceProject` folder.  For example: `cd Documents/DragonVoiceProject`

3.  **Run the `pip install` Command:**  Once you are in the `DragonVoiceProject` folder, type the following command **EXACTLY as written** and press Enter:
    ```bash
    pip install -r requirements.txt
    ```
    *   **Explanation:** This command tells `pip` to install all the packages listed in the `requirements.txt` file.  `pip` will download these packages from the internet and install them for you.
    *   **Wait for Installation to Finish:**  You will see messages in the Command Prompt/Terminal as `pip` downloads and installs each package.  Wait for it to finish completely.  You should see a message like "Successfully installed ..." or "Requirement already satisfied: ..." for each package.  If you see error messages, carefully check the error message and try to troubleshoot (or ask for help).

**Repeat these Python package installation steps on EVERY COMPUTER (server and all clients) that will be part of your voice control system.**

## ⚙️ 4. Setup - Step-by-Step - Get it Working

Once you have installed Python and the required packages on all computers, follow these steps to configure and run the Dragon Medical One Multi-Computer Voice Control System:

### 4.1. Configure the Client Script (`src/client.py`) - Pointing Clients to the Server

This is a **CRITICAL STEP!** You need to tell each client computer where to find the server computer so they can communicate.

1.  **Open `src/client.py` in a Text Editor:**  Use a simple text editor (like Notepad, TextEdit, or a code editor) to open the `src/client.py` file that you saved in the `DragonVoiceProject/src` folder.  Do this on **EACH CLIENT COMPUTER**.

2.  **Find the `SERVER_URL` Line:**  Look for this line of code in the `src/client.py` file:
    ```python
    SERVER_URL = "http://192.168.1.x:5000"
    ```

3.  **Replace `192.168.1.x` with the SERVER COMPUTER'S IP ADDRESS:**
    *   **Get the Server Computer's IP Address:**  Go to the computer where you will run `src/server.py` (your Dragon Medical One computer).  Open a Command Prompt/Terminal on that computer and type `ipconfig` (Windows) or `ifconfig` (macOS/Linux) and press Enter.  Find the **"IPv4 Address"** for your network connection and **copy** it.
    *   **Edit `src/client.py`:**  In the `src/client.py` file that you opened in the text editor, **carefully replace** the `192.168.1.x` part of the `SERVER_URL` line with the **IPv4 address you copied from the server computer.**  **DO NOT change the `http://` or `:5000` part!**
    *   **Example:** If your server computer's IP address is `192.168.1.110`, the line in `src/client.py` should become:
        ```python
        SERVER_URL = "http://192.168.1.110:5000"
        ```
    *   **Save the `src/client.py` file.**

4.  **Repeat for ALL Client Computers:**  **You MUST repeat Step 3 for the `src/client.py` file on EVERY CLIENT COMPUTER** that will be part of your voice control system.  Each `src/client.py` file needs to be configured to point to the IP address of the SERVER computer.

### 4.2. Run the Server Program (`src/server.py`) - Starting the "Brain"

1.  **Go to the SERVER Computer:**  Go to the computer where you will be using Dragon Medical One (your designated "server" computer).

2.  **Open Command Prompt/Terminal on the SERVER Computer:**

3.  **Navigate to the `DragonVoiceProject/src` Folder:**  Use the `cd` command to go to the `src` directory within your `DragonVoiceProject` folder.

4.  **Start the Server:**  Type the following command and press Enter:
    ```bash
    python src/server.py
    ```

5.  **Keep the Server Running:**  **DO NOT CLOSE** the Command Prompt/Terminal window where you ran `python src/server.py`.  This window needs to stay open and running for the server program to work.  You should see a message like: ` * Running on http://0.0.0.0:5000 ` in the terminal, indicating that the server is active and waiting for connections.  Minimize this window if you need to, but do not close it.

### 4.3. Run the Client Programs (`src/client.py`) - Starting the "Helpers" on Each Computer

1.  **Go to a CLIENT Computer:** Go to one of the computers where you want the automated browser searching to happen (a "client" computer).

2.  **Open Command Prompt/Terminal on the CLIENT Computer:**

3.  **Navigate to the `DragonVoiceProject/src` Folder:** Use the `cd` command to go to the `src` directory within your `DragonVoiceProject` folder.

4.  **Start the Client Program:** Type the following command and press Enter:
    ```bash
    python src/client.py
    ```

5.  **Keep the Client Running:**  **DO NOT CLOSE** the Command Prompt/Terminal window where you ran `python src/client.py`.  This window needs to stay open and running for the client program to work.  You should see the message: `Client running. Press Ctrl+C to stop.` in the terminal, indicating that the client is active and listening for queries.

6.  **Repeat for ALL Client Computers:**  **Repeat Steps 1-5 for EVERY CLIENT COMPUTER** that you want to include in your voice control system.  You need to run `src/client.py` on each of these computers and keep the Command Prompt/Terminal window running on each one.

## ✅ 5. Testing - Quick Checks - Is it GO?

Now that you have set up and run the server and client programs, let's test if everything is working correctly, step-by-step.

### 5.1. Phase 1 Testing: Single Computer Browser Typing (`src/quick_test.py`)

This test verifies that the basic browser automation (typing into Chrome windows) is working on a single computer.  Run this test on **ANY COMPUTER** where you have set up the `DragonVoiceProject` folder.

1.  **Run `src/quick_test.py`:** Open a Command Prompt/Terminal, navigate to the `DragonVoiceProject/src` folder, and run: `python src/quick_test.py`

2.  **Open Chrome Browsers:** Make sure you have **2 or 3 Chrome browser windows OPEN** on the **SAME COMPUTER** where you are running `src/quick_test.py`.  You can open any websites with search bars (like Google, Bing, DuckDuckGo).

3.  **Enter Test Query:** Look at the Command Prompt/Terminal window. You will see the prompt: `Enter your query:`.  **Type a test search query** (for example: `single computer test`) and press Enter.

4.  **Verify Browser Typing:** **IMMEDIATELY CHECK THE CHROME BROWSER WINDOWS on the SAME COMPUTER.**  Watch carefully! You should see the text `single computer test` automatically typed into the search bar of **each** open Chrome window, and then the "Enter" key should be pressed, starting a search in each window.

5.  **If Phase 1 Test FAILS:** If the text is not typed into the Chrome browsers, or if you see error messages in the Command Prompt/Terminal, go to the "Troubleshooting" section (Section 7) and look for solutions for "Browser automation (typing into Chrome) not working".  Fix any issues before proceeding to Phase 2 testing.

6.  **If Phase 1 Test PASSES:** If the text is correctly typed into all Chrome windows on the single computer, congratulations! Basic browser automation is working.  Proceed to Phase 2 testing to verify network communication and multi-computer query distribution.

### 5.2. Phase 2 Testing: Networked Query Distribution (`src/server.py` and `src/client.py`) - Testing Across Multiple Computers

This test verifies that the server and client programs are communicating correctly over your network and that queries are being distributed to multiple computers and typed into their browsers.

1.  **Ensure Server is Running:**  Go to the SERVER computer (Dragon Medical One computer) and make sure the `src/server.py` program is running (from "Setup Instructions" - Step 4).  Check that the Command Prompt/Terminal window for `src/server.py` is open and you see the message ` * Running on http://0.0.0.0:5000 `.

2.  **Ensure Clients are Running:** Go to **EACH CLIENT COMPUTER** and make sure the `src/client.py` program is running (from "Setup Instructions" - Step 5). Check that the Command Prompt/Terminal window for `src/client.py` is open and you see the message `Client running. Press Ctrl+C to stop.` on each client computer.

3.  **Prepare Chrome Browsers on Client Computers:** On **EACH CLIENT COMPUTER**, open 2-3 Chrome browser windows. You can open any websites with search bars.

4.  **Send a Test Query from ANY Computer (using a Web Browser or Online Tool):** You can use any computer that is connected to the same network as your server and client computers to send a test query to the server.  You can even use the SERVER computer itself.
    *   **Simplest Method - Using a Web Browser:**
        *   Open a web browser (like Chrome, Firefox, Edge, Safari) on any computer on your network.
        *   In the browser's address bar, type the following URL, **replacing `<server-ip>` with the actual IP address of your SERVER computer:**
            ```
            http://<server-ip>:5000/send_query
            ```
            For example: `http://192.168.1.110:5000/send_query`
        *   Press Enter. You will likely see a page that says "Method Not Allowed". **This is NORMAL and EXPECTED for this test!**  It just means the server is working and responding.  This method alone does not send the query text.
    *   **More Effective Method - Using an Online POST Request Sender Tool:**  For a proper test, you need to send a `POST` request with form data.  The easiest way to do this is to use an online tool.
        *   Search online for "online post request sender" or "online http client" using your web browser.
        *   Find a website that provides a simple online tool for sending HTTP requests.
        *   In the online tool:
            *   Set the **URL** field to: `http://<server-ip>:5000/send_query` (replace `<server-ip>` with your server's IP address).
            *   Set the **Method** or **Request Type** to `POST`.
            *   Look for a section called **"Form Data"**, **"Request Body"**, or similar (it might be labeled differently depending on the online tool).
            *   Add a new **key-value pair** for the form data:
                *   **Key/Name:** `query`
                *   **Value:** Type your test search query here (e.g., `network multi-computer query test`).
            *   Click the button to **"Send"**, **"Submit"**, or "Execute" the request.

5.  **VERIFY EVERYTHING - Check all computers!**  After sending the test query using the web browser or online tool, check the following:
    *   **Server Terminal Output (SERVER Computer):** Go to the Command Prompt/Terminal window where `src/server.py` is running on the SERVER computer.  **Verify** that you see a message like: `Received query: network multi-computer query test`.  If you see this, it means the server successfully received your test query!
    *   **Client Terminal Output (EACH CLIENT Computer):** Go to the Command Prompt/Terminal windows where `src/client.py` is running on **EACH CLIENT COMPUTER**.  **Verify** that each client terminal shows a message like: `New query received: network multi-computer query test`.  If you see this on all client computers, it means they are successfully receiving the query from the server over the network!
    *   **Browser Automation (EACH CLIENT Computer):** **IMMEDIATELY CHECK THE CHROME BROWSER WINDOWS on EACH CLIENT COMPUTER.**  Watch carefully!  Did the text `network multi-computer query test` get automatically typed into the search bar of **each** open Chrome window on **every client computer**? Did it press "Enter" and start a search in each window on each client computer?

6.  **If Phase 2 Test FAILS:** If you do not see the expected output in the server and client terminals, or if the text is not typed into the Chrome browsers on the client computers, go to the "Troubleshooting" section (Section 7) and look for solutions for "Networked Query Distribution Issues".  Carefully check all setup steps, network configurations, and error messages.  Fix any issues before proceeding to Phase 3 (Dragon Medical One integration).

7.  **If Phase 2 Test PASSES:** If you see all the expected outputs and the query is successfully distributed to multiple computers and typed into their browsers, **CONGRATULATIONS!**  Networked query distribution is working! You have successfully completed Phase 2.  You are now ready to move on to Phase 3, which involves integrating Dragon Medical One to enable voice-controlled queries.

### 5.3. Phase 3 Testing: Dragon Medical One Integration (To be Implemented)

Instructions for testing Phase 3 (Dragon Medical One integration) will be added here once the integration method is implemented and finalized.  This will involve creating a Dragon Medical One custom voice command to trigger the query distribution process.

## 📊 6. Project Management Information

This section provides a high-level overview of the project from a project management perspective.

### 6.1. Project Goals and Objectives (for Project Management)

*   **Primary Goal:** To develop and deploy a functional voice-controlled multi-browser query system that significantly improves research efficiency for users of Dragon Medical One.
*   **Key Objectives:**
    *   Successfully implement network communication between a server and multiple client computers for query distribution.
    *   Achieve reliable browser automation on client computers to automatically type and initiate search queries in Chrome.
    *   Integrate Dragon Medical One voice dictation as the primary input method for the system.
    *   Create a user-friendly and well-documented system that is easy to set up, use, and maintain.
    *   Ensure the system is robust and handles common errors gracefully.
*   **Success Criteria:**
    *   Successful completion of Phase 2 testing, demonstrating reliable networked query distribution.
    *   Successful integration with Dragon Medical One (Phase 3), enabling voice-controlled query initiation.
    *   Positive user feedback on system usability and efficiency gains.
    *   Comprehensive documentation (this `docs/README.md`) for setup, usage, and troubleshooting.

### 6.2. Project Scope and Deliverables

*   **In Scope (Deliverables):**
    *   Functional Python scripts (`src/server.py`, `src/client.py`, `src/quick_test.py`) for networked query distribution and browser automation.
    *   Detailed `docs/README.md` documentation covering setup, usage, troubleshooting, and project overview.
    *   Basic integration with Dragon Medical One for voice-controlled query input (Text File or Clipboard method).
    *   Phase 1 and Phase 2 testing and demonstration of core functionality.
*   **Out of Scope (Non-Deliverables in Initial Phases):**
    *   Advanced User Interface (GUI) for server and client applications (Phase 6 - Future Enhancement).
    *   Support for web browsers other than Google Chrome (Phase 5 - Future Enhancement).
    *   Operation over the public internet without additional security measures (Phase 7 - Future Enhancement).
    *   Highly advanced error handling or fault tolerance beyond basic troubleshooting (Phase 4 - Ongoing Refinement).
    *   Customization for specific websites beyond basic search bar interaction (Phase 5 - Future Enhancement).
    *   Extensive user training materials beyond the `docs/README.md` documentation.

### 6.3. Project Timeline and Phases (with Estimated Durations)

The project is planned in four main phases, with estimated durations:

1.  **Phase 1: Single Computer Demo - Browser Automation Core (Estimated Duration: 1-2 days) - ✅ COMPLETED**
    *   **Milestone:** Successful completion and testing of `src/quick_test.py` demonstrating browser automation on a single computer.
    *   **Status:** Completed (as of March 3, 2025).

2.  **Phase 2: Networked Query Distribution - Connecting the Computers (Estimated Duration: 3-5 days) - 🚧 IN PROGRESS**
    *   **Milestone:** Successful implementation and testing of `src/server.py` and `src/client.py` for networked query distribution to multiple computers.  Successful completion of Phase 2 testing (Section 5B).
    *   **Status:** In Progress (as of March 4, 2025).  Focus is on achieving reliable network communication and browser automation on client computers.

3.  **Phase 3: Dragon Medical One Integration - Voice Control Unleashed (Estimated Duration: 2-3 days) - 🗓️ PLANNED**
    *   **Milestone:** Successful integration of Dragon Medical One with the system, enabling voice-controlled query initiation.  End-to-end voice control workflow fully functional.
    *   **Status:** Planned.  To be started after successful completion of Phase 2.

4.  **Phase 4: Testing, Refinement, and Polish (Estimated Duration: 2-3 days - Ongoing and Iterative) - 🗓️ PLANNED**
    *   **Milestone:**  System is thoroughly tested in various scenarios, error handling is robust, and user experience is refined.  Final documentation is completed.
    *   **Status:** Planned.  To be started after Phase 3 and will be an ongoing, iterative process for continuous improvement.

**Overall Estimated Project Duration (Phase 1 - Phase 4): Approximately 1-2 weeks.**  (Note: These are initial estimates and may be adjusted based on progress and any unforeseen challenges).

### 6.4. Resource Requirements

*   **Human Resources:**
    *   **Project Manager / Developer (Current Role: Beka):** Responsible for project planning, development, testing, documentation, and overall project management.  (Note: For larger projects, these roles could be separated).
*   **Software Resources:**
    *   **Python 3.x:**  Required on all server and client computers.
    *   **Python Packages (Libraries):** `pyautogui`, `pygetwindow`, `flask`, `requests`, `pyperclip` (listed in `requirements.txt`).
    *   **Dragon Medical One (or similar voice recognition software):** Required on the server computer for voice control (Phase 3).
    *   **Google Chrome Browser:** Required on all client computers for browser automation.
    *   **Git (Optional but Recommended):** For version control and code management.
    *   **Online POST Request Sender Tool:** For testing Phase 2 network communication.
*   **Hardware Resources:**
    *   **Multiple Computers (Minimum 2):**
        *   One designated "server" computer (ideally with Dragon Medical One).
        *   One or more "client" computers for browser automation.
    *   **Local Network:**  Reliable local network (Wi-Fi or Ethernet) connecting all computers.
    *   **Internet Connection (Temporary):**  Internet access required during setup to download Python and Python packages.

### 6.5. Roles and Responsibilities

*   **Project Manager / Developer (Current Role: Beka):**
    *   **Project Planning and Management:** Defining project scope, timeline, milestones, and tasks.
    *   **Software Development:**  Writing, testing, and debugging Python scripts (`src/server.py`, `src/client.py`, `src/quick_test.py`).
    *   **Documentation:** Creating and maintaining `docs/README.md` and other project documentation.
    *   **Testing and Quality Assurance:**  Developing and executing test plans, ensuring system functionality and robustness.
    *   **Issue Tracking and Resolution:**  Identifying, diagnosing, and resolving bugs and issues.
    *   **Communication:**  Providing project status updates and communicating with stakeholders (e.g., Robert).

### 6.6. Risk Assessment and Mitigation Strategies

*   **Risk 1: "ModuleNotFoundError" - Missing Python Packages (Installation Issues)**
    *   **Description:** Users may encounter errors due to missing required Python packages.
    *   **Mitigation:**  Provide ultra-detailed, step-by-step instructions for Python and package installation (Section 3).  Include clear troubleshooting steps in "Troubleshooting" section (Section 7.1).  Provide `requirements.txt` for easy package installation.
*   **Risk 2: "Connection refused" - Network Communication Failures (Phase 2)**
    *   **Description:** Client computers may fail to connect to the server due to network configuration issues, firewall blocks, or incorrect IP address settings.
    *   **Mitigation:**  Provide very clear instructions for configuring `SERVER_URL` in `src/client.py` (Section 4.1).  Include detailed troubleshooting steps for network connection issues in "Troubleshooting" section (Section 7.2), including firewall checks and network testing tips.
*   **Risk 3: Browser Automation Failures (Typing into Chrome Issues)**
    *   **Description:** Browser automation (typing into Chrome) may not work reliably due to various factors, such as Chrome window detection problems, interference from other programs, or changes in website structure.
    *   **Mitigation:**  Provide detailed testing instructions for browser automation (Section 5.1 and 5.2).  Include troubleshooting steps for browser automation issues in "Troubleshooting" section (Section 7.3), including tips for running from command line and checking for interfering programs.
*   **Risk 4: Server Not Receiving Queries (Phase 2 Testing Failures)**
    *   **Description:** The server program may not receive test queries sent from web browsers or online tools due to incorrect URLs, request types, or form data.
    *   **Mitigation:**  Provide very precise instructions for testing Phase 2 communication (Section 5.2), including example URLs and form data.  Include troubleshooting steps for server query reception issues in "Troubleshooting" section (Section 7.4), emphasizing URL, request type, and form data verification.

**Overall Risk Mitigation Strategy:**  Comprehensive and ultra-detailed documentation (`docs/README.md`) is the primary risk mitigation strategy.  By providing clear, step-by-step instructions, detailed testing guides, and extensive troubleshooting information, the goal is to minimize user errors, facilitate problem diagnosis, and ensure a higher likelihood of successful project setup and usage.

### 6.7. Progress Tracking and Milestones

Project progress will be tracked against the defined project phases and milestones:

*   **Phase 1 Completion:**  Tracked by successful completion of Phase 1 testing (Section 5.1) and code commit for Phase 1 functionality on GitHub (if using version control).
*   **Phase 2 Completion:** Tracked by successful completion of Phase 2 testing (Section 5.2) and code commit for Phase 2 functionality on GitHub.
*   **Phase 3 Completion:** Tracked by successful integration of Dragon Medical One and end-to-end voice control testing. Code commit for Phase 3 functionality.
*   **Phase 4 Completion:** Tracked by completion of thorough testing, implementation of error handling and robustness improvements, finalization of documentation, and potentially user feedback.  Final code commit for Phase 4 and project version 1.0 release (if applicable).

Regular status updates will be provided based on progress against these milestones.

### 6.8. Communication Plan

*   **Primary Communication Channel:**  `docs/README.md` file will serve as the central and primary source of project documentation, instructions, and status information.  All key project information, updates, and troubleshooting guidance will be documented in this file.
*   **Status Updates:**  Project status updates will be provided periodically, referencing the project phases and milestones outlined in this "Project Management Information" section.  Updates will be communicated through modifications to the `docs/README.md` file and potentially via direct messages or email as needed.
*   **Issue Reporting and Tracking:**  Users encountering issues are encouraged to refer to the "Troubleshooting" section of the `docs/README.md` first.  If issues persist, users can report them by [Specify preferred method - e.g., contacting developer directly via email, or if using GitHub, by creating issues on the GitHub repository].  Issue resolution and updates will be communicated back through the `docs/README.md` and/or directly to the user who reported the issue.

## 7. Troubleshooting - Help! It's Not Working!

If you encounter problems while setting up or testing the Dragon Medical One Multi-Computer Voice Control System, refer to this troubleshooting section for common issues and potential solutions.

### 7.1. Installation Issues

*   **"ModuleNotFoundError" or "No module named '...'":**
    *   **Problem:** This is the **most common issue** and means that Python is missing some of the extra tools (packages) that are required to run the scripts.
    *   **Solution:** **Go back to "Setup Instructions" - Section 3.2. Install Python Packages** and **carefully follow the instructions to install the Python packages using `pip install -r requirements.txt` in the Command Prompt/Terminal on EVERY COMPUTER** (server and all clients).  **Make sure you are in the `DragonVoiceProject` folder** when you run this command!  Double-check that you typed the command correctly and that `pip` is working properly.  If `pip` itself is not recognized, you may need to ensure Python is correctly installed and added to your system's PATH (see Section 3.1).

### 7.2. Network Communication Issues (Phase 2 Testing Failures)

*   **"Connection refused" or "Unable to connect" (Client cannot connect to Server):**
    *   **Problem:** The client program (`src/client.py`) on a client computer cannot establish a connection with the server program (`src/server.py`) running on the server computer.
    *   **Possible Solutions:**
        *   **Verify Server is Running:** **Double-check that `src/server.py` is REALLY running** on the SERVER computer. Go back to the SERVER computer and make absolutely sure that the Command Prompt/Terminal window where you ran `python src/server.py` is still open and running, and that you saw the message ` * Running on http://0.0.0.0:5000 `. If you accidentally closed it, run it again!
        *   **Verify `SERVER_URL` in `src/client.py` is CORRECT:** Open the `src/client.py` file on a CLIENT computer and **double-check that you replaced `http://192.168.1.x:5000` with the correct IPv4 address of the SERVER computer!**  Make sure you didn't make any typos when entering the IP address.  The IP address must be the IPv4 address of the SERVER computer on your local network.
        *   **Computers on Same Network?** **Are ALL computers (server and clients) connected to the SAME LOCAL NETWORK?** They need to be on the same Wi-Fi network or connected to the same router via Ethernet cables so they can communicate with each other.  They cannot be on different networks or guest networks.
        *   **Firewalls Blocking?** **Firewalls on your computers might be blocking network communication.**  Firewalls are security software that can prevent programs from sending and receiving data over the network.  For **testing purposes only**, you can try **temporarily disabling the firewalls** on **both the SERVER and CLIENT computers**.
            *   **Windows Firewall:** Search for "Windows Defender Firewall" in the Windows search bar, open it, and choose "Turn Windows Defender Firewall on or off" in the left panel.  Select "Turn off Windows Defender Firewall (not recommended)" for both "Private network settings" and "Public network settings" and click "OK".  **Remember to turn the firewalls back ON after testing!**
            *   **macOS Firewall:** Go to "System Preferences" -> "Security & Privacy" -> "Firewall" tab.  Click the lock icon to unlock settings, and then click "Turn Off Firewall".  **Remember to turn the firewall back ON after testing!**
            *   **Test Again with Firewalls Disabled:** After disabling firewalls, try running the Phase 2 test again (Section 5.2).  If the system starts working correctly with firewalls disabled, then you know that your firewall is the problem.  **You should NOT leave your firewalls disabled permanently!**  Instead, you will need to **configure your firewall to ALLOW network communication on port `5000` for the `src/server.py` and `src/client.py` programs.**  This is called "adding a firewall exception" or "allowing an app through the firewall".  Consult your firewall software's documentation for instructions on how to add exceptions for specific programs or ports.
        *   **Network Issues Beyond Firewall:** If disabling firewalls does not solve the "Connection refused" error, there might be other network issues, such as problems with your router, network cables, or network configuration.  These are more advanced network troubleshooting steps that are beyond the scope of this documentation.  You may need to consult with a network administrator or IT professional if you suspect deeper network problems.

### 7.3. Browser Automation Issues (Typing into Chrome Not Working)

*   **Browser automation (typing into Chrome) is not working on client computers (Phase 2 Test Failure):**
    *   **Problem:** The `src/client.py` program is not successfully typing the query into the Chrome browser windows on the client computers, even though network communication seems to be working (client terminals show "New query received...").
    *   **Possible Solutions:**
        *   **Are Chrome Browsers OPEN?** **Make sure you have Chrome browser windows OPEN on the CLIENT COMPUTERS** before running the Phase 2 test. The `src/client.py` program can only type into Chrome windows that are already open.  Open 2-3 Chrome windows on each client computer.
        *   **Check for Errors in Client Terminal:** **Look at the Command Prompt/Terminal window where `src/client.py` is running on the CLIENT computer.** Are there any **error messages** showing up in that window?  If yes, carefully copy and paste the entire error message and search online for solutions, or ask for help providing the exact error message.  Error messages can give clues about what is going wrong.
        *   **Run Client from Command Line (Not from IDE):** **Make sure you are running `src/client.py` by typing `python src/client.py` in the Command Prompt/Terminal directly.**  Do not run it from a code editor or IDE (Integrated Development Environment) like VS Code or PyCharm for testing browser automation.  Running from the command line ensures that the script has the necessary permissions to control the keyboard and mouse.
        *   **Other Programs Interfering?** **Sometimes other programs running on your computer can interfere with the keyboard control.**  Try closing any unnecessary applications that might be running in the background on the CLIENT computers and test again.  Some security software or accessibility tools might interfere with `pyautogui`.
        *   **Chrome Window Titles:** The `src/client.py` script finds Chrome windows by looking for windows with "Chrome" in their title.  In rare cases, if your Chrome browser windows have unusual titles, the script might not find them.  You can try modifying the `src/client.py` code to use a more general window title search or to target specific Chrome window classes if needed (advanced customization).

### 7.4. Server Not Receiving Queries (Phase 2 Test Failure)

*   **Server program (`src/server.py`) is not receiving test queries sent from browser/online tool (Phase 2 Test Failure):**
    *   **Problem:** You are sending a test query using a web browser or online POST request tool to the server's IP address and port 5000, but the `src/server.py` terminal does not show the "Received query: ..." message, indicating that the server is not receiving your request.
    *   **Possible Solutions:**
        *   **Is `src/server.py` REALLY Running?** **Double-check that the `src/server.py` program is running** on the SERVER computer. Go back to the SERVER computer and make absolutely sure that the Command Prompt/Terminal window for `src/server.py` is open and running, and that you saw the message ` * Running on http://0.0.0.0:5000 `. If you accidentally closed it, run it again!  If you don't see the "Running on..." message, then the server is not started correctly.
        *   **Correct URL?** **Double-check that you are sending the `POST` request to the CORRECT URL** in your web browser or online tool.  The URL should be **exactly**: `http://<server-ip>:5000/send_query` (make sure you replace `<server-ip>` with the correct IPv4 address of your SERVER computer!).  Double-check for typos in the URL.
        *   **Correct Request Type?** **Make sure you are sending a `POST` request, NOT a `GET` request.**  The server endpoint `/send_query` is designed to receive `POST` requests.  In your online POST request tool, ensure you have selected "POST" as the request method.
        *   **Correct Form Data?** **Make sure you are including FORM DATA in the `POST` request, and that the form data has the correct KEY and VALUE.**  The server expects form data with the **key** set to `query` and the **value** set to your search query text (e.g., `query=my test query`).  Double-check that you have added this form data correctly in your online POST request tool.

## 8. Developer Documentation - Extending and Modifying the Project

{{ This section will be expanded with more technical details for developers who want to customize or extend the project.  For now, it can be a placeholder. }}

### 8.1. Code Structure Overview

### 8.2. Key Functions and Modules

### 8.3. Extending the System - Ideas for Customization

## 9. Future Enhancements (Roadmap) - What's Next?

Here's a roadmap outlining potential future enhancements and development stages for the Dragon Medical One Multi-Computer Voice Control Project:

*   **Phase 3: Dragon Medical One Integration (Next Priority):**
    *   **Goal:**  Enable seamless integration with Dragon Medical One to capture voice dictation directly and trigger the query distribution process using voice commands.
    *   **Tasks:**
        *   Choose the best method for Dragon Medical One integration:
            *   **Option A: Dragon to Text File:**  Create a Dragon Medical One custom command to save dictated text to a file, and modify `src/server.py` to monitor and read from this file.
            *   **Option B: Dragon to Clipboard:** Create a Dragon Medical One command to copy dictated text to the clipboard, and modify `src/server.py` to read from the clipboard.
        *   Implement the chosen integration method in `src/server.py`.
        *   Create a Dragon Medical One custom voice command (e.g., "Start Multi-Query") to initiate the query distribution workflow.
        *   Test end-to-end voice control: Speak into Dragon Medical One, verify query is distributed to multiple computers and typed into browser search bars.

*   **Phase 4: Testing, Refinement, and Polish (Ongoing):**
    *   **Goal:**  Thoroughly test the system in real-world scenarios, improve robustness, handle errors gracefully, and enhance user experience.
    *   **Tasks:**
        *   Extensive testing across different websites, network conditions, and with various query types.
        *   Implement robust error handling in both server and client scripts to manage network interruptions, website changes, and unexpected situations.
        *   Refine browser automation scripts to improve reliability and compatibility with different website search bar structures.
        *   Optimize performance and speed of query distribution.

*   **Phase 5: Website Compatibility Enhancements:**
    *   **Goal:** Expand browser automation to work reliably with a wider range of websites and search bar types beyond basic Google Search.
    *   **Tasks:**
        *   Identify target websites for enhanced compatibility.
        *   Analyze the HTML structure and search bar elements of these websites.
        *   Implement more robust element selectors (e.g., using Selenium WebDriver instead of `pyautogui` for more precise element targeting) in `src/client.py` to handle different website structures and dynamic content.
        *   Add website-specific configurations or logic to handle unique search bar behaviors or website layouts.

*   **Phase 6: User Interface (Optional Enhancement):**
    *   **Goal:** Develop a simple graphical user interface (GUI) for the server and/or client applications to make them easier to use for non-technical users, instead of relying on command-line execution.
    *   **Tasks:**
        *   Choose a suitable Python GUI library (e.g., Tkinter, PyQt, Kivy).
        *   Design and implement a basic GUI for the server application to:
            *   Start/stop the server.
            *   Display server status and logs.
            *   Potentially configure server settings (port number, etc.).
        *   Design and implement a basic GUI for the client application to:
            *   Start/stop the client listener.
            *   Display client status and connection information.
            *   Potentially configure client settings (server IP address, etc.).

*   **Phase 7: Advanced Features (Optional Enhancements):**
    *   **Goal:** Add more advanced features to the system based on user needs and feedback.
    *   **Potential Features:**
        *   **Query History/Logging:** Implement logging of queries sent and received for tracking, debugging, and review.
        *   **Configuration Options:**  Allow users to configure various settings through a configuration file or GUI, such as:
            *   Server port number
            *   List of target websites
            *   Customizable delays or timeouts
        *   **Security Enhancements:**  For more sensitive environments, explore options for secure network communication, such as using HTTPS instead of HTTP for server-client communication.
        *   **Error Reporting and Monitoring:** Implement more detailed error reporting and monitoring within the applications to provide better feedback to users and aid in troubleshooting.

## 10. Contribution Guidelines (Optional)

{{ If you plan to share this project and accept contributions from others, you can add guidelines here on how to contribute code, report issues, suggest features, etc.  For a personal project, this section can be omitted. }}

## 11. License (Optional)

{{ If you plan to share this project publicly, consider adding an open-source license to it, such as the MIT License, Apache 2.0 License, or GPL License.  A license specifies how others can use, modify, and distribute your code.  If you are not sure, you can learn more about open-source licenses at [https://choosealicense.com/](https://choosealicense.com/) and add a license file to your project.  For a personal project, a license is optional. }}

## 12. Contact

[Your Name/Contact Information] -  {{ Your preferred contact method, e.g., email address, GitHub profile link }}

---

{{ Add any other relevant notes or information here - e.g., acknowledgements, disclaimers, etc. }}

## 13. Glossary of Terms - Tech Jargon Explained

To help users who may be less familiar with some of the technical terms used in this documentation, here is a brief glossary of common terms:

*   **API (Application Programming Interface):** A set of rules and specifications that software programs can follow to communicate with each other. In this project, we might use APIs to integrate with Dragon Medical One or other services in the future.
*   **ASCII Art:**  Images created using text characters, often used for simple diagrams or visual elements in text-based documents.
*   **Client:** In a client-server model, a client is a computer or program that *requests* services or data from a server. In this project, `src/client.py` programs running on client computers are clients that request search queries from the server.
*   **Command Prompt (Windows) / Terminal (macOS/Linux):** A text-based interface for interacting with your computer's operating system. You type commands as text, and the computer responds with text output.  Used to run Python scripts and install packages.
*   **DHCP (Dynamic Host Configuration Protocol):** A network management protocol used to automatically assign IP addresses and other network configuration parameters to devices on a network. Most home routers use DHCP to assign IP addresses to your computers and phones.
*   **DNS (Domain Name System):** A system that translates human-readable domain names (like `www.google.com`) into IP addresses that computers use to locate each other on the internet.
*   **Endpoint:** In web server terminology, an endpoint is a specific URL or path on a web server that is designed to handle a particular type of request. In `src/server.py`, `/send_query` and `/get_query` are endpoints.
*   **Ethernet:** A common networking technology that uses physical cables to connect computers and devices in a local network.
*   **FAQ (Frequently Asked Questions):** A list of common questions and their answers, designed to address common user queries and issues.
*   **Firewall:** A network security system that controls incoming and outgoing network traffic based on predefined rules. Firewalls can help protect your computer from unauthorized access but can also sometimes block legitimate network communication if not configured correctly.
*   **Flask:** A lightweight and popular Python web framework used to create web applications and web servers.  Used in `src/server.py` to create the query distribution server.
*   **Form Data:** Data sent in an HTTP request (typically `POST` requests) that is structured as key-value pairs, often used to submit data from web forms or programmatically send data to web servers.
*   **GET Request:** An HTTP request method used to *retrieve* data from a web server.  Client programs use `GET` requests to ask the server for the latest query.
*   **GUI (Graphical User Interface):** A user interface that allows users to interact with software through visual elements like windows, icons, and menus, as opposed to a text-based command-line interface.
*   **HTTP (Hypertext Transfer Protocol):** The foundation of data communication for the World Wide Web.  It's a protocol used to transfer data (like web pages, images, and other resources) between web browsers and web servers.  Our project uses HTTP for communication between the server and client programs.
*   **HTTPS (HTTP Secure):** A secure version of HTTP that encrypts communication between web browsers and web servers, protecting data from eavesdropping and tampering.
*   **IDE (Integrated Development Environment):** A software application that provides comprehensive facilities to computer programmers for software development.  Examples include VS Code, PyCharm, and Eclipse.  While IDEs are great for coding, it's recommended to run the `src/client.py` and `src/server.py` scripts from the command line for testing browser automation to avoid potential permission issues.
*   **IP Address (Internet Protocol Address):** A numerical label assigned to each device participating in a computer network that uses the Internet Protocol for communication.  Think of it as a computer's "network address".  IPv4 addresses are commonly used and look like `192.168.1.100`.
*   **Localhost:** Refers to the current computer you are working on.  The IP address `127.0.0.1` or the hostname `localhost` always points back to your own computer.  Used for testing server and client programs on the same machine.
*   **Local Network:** A computer network that connects computers and devices within a limited area, such as a home, office, or building.  Often uses technologies like Wi-Fi or Ethernet.
*   **Package (Python Package / Library):** A collection of modules (Python code files) that provide reusable functionality for Python programs.  Examples in this project include `pyautogui`, `pygetwindow`, `flask`, `requests`, and `pyperclip`.  Packages extend Python's capabilities and make it easier to perform complex tasks.
*   **PATH (Environment Variable):** A system environment variable that specifies a set of directories where executable programs are located.  Adding Python to PATH allows you to run Python commands (like `python` and `pip`) from any directory in the Command Prompt/Terminal.
*   **pip (Package Installer for Python):** A package management system used to install and manage software packages written in Python.  Used to install the required Python packages for this project using the command `pip install -r requirements.txt`.
*   **Port (Network Port):** A virtual "doorway" or communication endpoint on a computer's network interface.  Port numbers are used to distinguish between different applications or services running on the same computer that are communicating over the network.  Our project uses port `5000` by default for server-client communication.
*   **POST Request:** An HTTP request method used to *send* data to a web server to create or update a resource.  We use `POST` requests to send search queries *to* the server at the `/send_query` endpoint.
*   **pyautogui:** A Python package used for GUI automation.  It allows Python scripts to control the mouse and keyboard, enabling tasks like typing text, clicking buttons, and moving the mouse cursor programmatically.  Used in `src/client.py` and `src/quick_test.py` for browser automation.
*   **pygetwindow:** A Python package used to get information about and control application windows.  Used in `src/client.py` and `src/quick_test.py` to find and manage Chrome browser windows.
*   **pyperclip:** A Python package used for cross-platform clipboard access.  May be used in future phases for Dragon Medical One integration via the clipboard.
*   **Python:** A high-level, interpreted, general-purpose programming language.  The primary language used to develop the Dragon Medical One Multi-Computer Voice Control Project.
*   **requirements.txt:** A text file that lists Python packages and their versions required for a project.  Used to easily install project dependencies using `pip install -r requirements.txt`.
*   **Requests (Python Library):** A popular Python library used for making HTTP requests.  Used in `src/client.py` to communicate with the server and retrieve search queries.
*   **Roadmap:** A high-level plan that outlines the future direction and development stages of a project.
*   **Router:** A networking device that forwards data packets between computer networks.  Home routers typically connect your local network to the internet and also provide Wi-Fi and Ethernet connectivity within your home network.
*   **Server:** In a client-server model, a server is a computer or program that *provides* services or data to clients.  In this project, `src/server.py` running on the server computer is the server that provides the query distribution service to client computers.
*   **Server Computer:** The designated computer in this project that runs the `src/server.py` program and acts as the central hub for query distribution.  Intended to be the computer where Dragon Medical One is used.
*   **Shell:** Another term for Command Prompt (Windows) or Terminal (macOS/Linux).
*   **Socket:** A software construct that represents one endpoint of a network connection.  Sockets are used by programs to send and receive data over a network.  While our current implementation uses HTTP, sockets could be used for more direct network communication in future enhancements.
*   **SSL/TLS (Secure Sockets Layer/Transport Layer Security):** Cryptographic protocols that provide secure communication over a network, often used to encrypt web traffic (HTTPS).
*   **TCP/IP (Transmission Control Protocol/Internet Protocol):** The fundamental communication protocols that underpin the internet and most computer networks.  HTTP, which we use in this project, is built on top of TCP/IP.
*   **Terminal (macOS/Linux) / Command Prompt (Windows):** A text-based interface for interacting with your computer's operating system.  You type commands as text, and the computer responds with text output.  Used to run Python scripts and install packages.
*   **Thread (Threading):** A unit of execution within a program.  Multithreading allows a program to perform multiple tasks concurrently.  Used in `src/client.py` to run the query checking and browser automation in the background without blocking the main program.
*   **Troubleshooting:** The process of diagnosing and resolving problems or errors in a system or process.  Section 7 of this documentation provides troubleshooting tips for common issues in the Dragon Medical One Multi-Computer Voice Control Project.
*   **UDP (User Datagram Protocol):** A network communication protocol that is faster but less reliable than TCP.  While our current implementation uses TCP-based HTTP, UDP could be considered for future enhancements where speed is critical and some data loss is acceptable.
*   **URL (Uniform Resource Locator):**  A web address that specifies the location of a resource on the internet.  Examples include `http://www.google.com` or `http://<server-ip>:5000/send_query`.
*   **VBAN (Voicemeeter Broadcast Audio Network):** A protocol developed by VB-Audio Software (makers of Voicemeeter Banana) for streaming audio over a local network.  Mentioned in earlier discussions as a potential option for audio distribution, but not currently used in the core text-based query distribution system.
*   **VBScript (Visual Basic Scripting Edition):** A scripting language developed by Microsoft, often used for automation tasks in Windows environments.  Mentioned in earlier discussions as a potential option for triggering Python scripts from Dragon NaturallySpeaking, but not currently used in the core implementation.
*   **Virtual Environment (Python):** A self-contained directory that isolates a Python installation and its packages from the system-wide Python installation.  Virtual environments are often used to manage dependencies for different Python projects and avoid conflicts between package versions.  While not strictly required for this project, using virtual environments is generally a good practice for Python development.
*   **Voicemeeter Banana:** A virtual audio mixer application for Windows, mentioned in earlier discussions as a potential tool for advanced audio routing and management, but not currently used in the core text-based query distribution system.
*   **Wi-Fi (Wireless Fidelity):** A wireless networking technology that allows computers and devices to connect to a network without physical cables, using radio waves.

## 14. Tips and Best Practices - Getting the Most Out of Your Voice Control System

To ensure smooth operation and get the best performance from your Dragon Medical One Multi-Computer Voice Control System, consider these tips and best practices:

*   **Start Server First, Then Clients:** Always start the `src/server.py` program on the server computer *before* starting the `src/client.py` programs on the client computers.  The clients need the server to be running and listening for connections before they can connect and receive queries.
*   **Keep Terminal Windows Open:**  **DO NOT close the Command Prompt/Terminal windows** where you are running `src/server.py` and `src/client.py` on each computer.  These windows need to remain open and running for the programs to continue working.  You can minimize them if needed, but do not close them.  If you close the windows, the programs will stop running, and the voice control system will not work.
*   **Test on a Small Scale First:** When setting up the system for the first time, start with a **small-scale test** using just one server computer and one client computer.  Once you have verified that the system is working correctly in this simple setup, you can then gradually add more client computers to your network.  Testing on a small scale first makes it easier to isolate and troubleshoot any issues.
*   **Use Static IP Address for Server (Optional but Recommended for Stability):** For more reliable network communication, especially if your server computer's IP address tends to change (e.g., if you are using DHCP and your router reassigns IP addresses periodically), consider setting a **static IP address** for your server computer.  A static IP address is a fixed IP address that does not change.  You can usually configure a static IP address in your operating system's network settings or in your router's configuration interface.  Refer to your operating system and router documentation for instructions on how to set a static IP address.  If you use a static IP address for your server, you will need to update the `SERVER_URL` in `src/client.py` to use this static IP address.
*   **Check Firewall Settings (If Experiencing Connection Issues):** If you are having trouble getting the client computers to connect to the server, or if the system is not working as expected, **always check your firewall settings** on both the server and client computers.  Firewalls are a common cause of network communication problems.  Temporarily disabling firewalls (for testing purposes only!) or creating firewall exceptions for Python and port `5000` can often resolve connection issues.  Remember to re-enable your firewalls or properly configure firewall rules after testing.
*   **Monitor Terminal Output for Errors:** Keep an eye on the Command Prompt/Terminal windows where `src/server.py` and `src/client.py` are running.  These windows will often display **error messages** if something goes wrong.  If you encounter problems, carefully examine the terminal output for any error messages, copy and paste the error messages, and use them to search online for solutions or ask for help.  Error messages are valuable clues for troubleshooting.
*   **Test Network Connectivity (Ping Command):** If you are having network communication problems, you can use the `ping` command to test basic network connectivity between your computers.  Open a Command Prompt/Terminal on a client computer and type `ping <server-ip>` (replace `<server-ip>` with the IP address of your server computer) and press Enter.  If you get replies from the server computer, it means there is basic network connectivity.  If you get "Request timed out" or "Destination host unreachable" messages, it indicates a network connectivity problem that needs to be investigated further.
*   **Use a Dedicated Network (If Possible):** For optimal performance and reliability, especially if you are using a large number of client computers, consider using a **dedicated local network** for your voice control system.  This can help minimize network congestion and interference from other network traffic.  You can set up a separate Wi-Fi network or use a dedicated Ethernet switch to create a private network for your server and client computers.
*   **Keep Software Updated:** Ensure that you have the latest versions of Python and all required Python packages installed on all computers.  Keeping your software up-to-date can help improve performance, security, and compatibility.  You can update Python packages using `pip install --upgrade <package-name>`.
*   **Provide Feedback and Report Issues:** If you encounter any issues, have suggestions for improvements, or find any bugs in the system, please provide feedback and report issues to the project developers (using the contact information in Section 12).  Your feedback is valuable and helps improve the project for everyone.

## 15. Frequently Asked Questions (FAQ) - Common Questions and Answers

This FAQ section addresses some common questions that users may have about the Dragon Medical One Multi-Computer Voice Control Project.

**Q: Do I need Dragon Medical One to use this system?**

**A:**  While the project is named "Dragon Medical One Multi-Computer Voice Control Project", the core system (Phase 2: Networked Query Distribution) does *not* strictly require Dragon Medical One.  Phase 2, which involves distributing queries to multiple computers, can be tested and used with *any* method of providing text queries to the server (e.g., manually typing queries into the server program, using a web form to send queries, or even using a different voice recognition software).  Dragon Medical One integration is planned for Phase 3, which will add the voice control aspect.  However, for Phase 1 and Phase 2 testing and usage, Dragon Medical One is not necessary.  You can use the `src/quick_test.py` script to test browser automation on a single computer, and you can use tools like web browsers or online POST request senders to manually send test queries to the server to test the network distribution in Phase 2.

**Q: Can I use a different web browser instead of Chrome?**

**A:**  Currently, the browser automation scripts (`src/quick_test.py` and `src/client.py`) are specifically designed to work with **Google Chrome** browser windows.  The scripts use `pygetwindow` to find Chrome windows based on their window titles and `pyautogui` to simulate keyboard input to type into the search bars within those Chrome windows.  While it might be possible to modify the scripts to work with other web browsers (like Firefox, Edge, Safari, etc.), this would require code changes and testing.  The current version of the project is focused on Chrome compatibility.  Future enhancements (Phase 5: Website Compatibility Enhancements) may explore expanding browser compatibility to other browsers.

**Q: Can I use this system over the internet, or does it only work on a local network?**

**A:**  The Dragon Medical One Multi-Computer Voice Control Project, in its current implementation (Phase 2), is designed to work on a **local network**.  The server and client programs communicate with each other using HTTP over your local network.  It is *not* designed to work directly over the public internet without modifications.  Running the system over the internet would raise security considerations and require additional configuration (e.g., setting up port forwarding, using HTTPS for secure communication, and potentially implementing authentication and authorization mechanisms).  For most typical use cases (e.g., research within a home or office network), a local network setup is sufficient and simpler to configure.  Future enhancements (Phase 7: Security Enhancements) may explore options for more secure and wider-area network deployment if there is demand.

**Q: Do I need to be a programmer to set up and use this system?**

**A:**  While some basic technical familiarity is helpful, the Dragon Medical One Multi-Computer Voice Control Project is designed to be **usable by non-programmers** as well, with careful adherence to the detailed setup instructions provided in this documentation.  The "Setup Instructions" (Section 4) are written in a step-by-step, ultra-detailed manner, aiming to make the process as clear and easy to follow as possible, even for users who are not experienced with programming or command-line interfaces.  However, some comfort level with using a computer, installing software, and following instructions is expected.  If you encounter issues, the "Troubleshooting" section (Section 7) provides guidance for resolving common problems.  For users who prefer a more graphical and user-friendly experience, future enhancements (Phase 6: User Interface) may explore adding a GUI to simplify setup and usage.

**Q: What if I have problems or errors during setup or testing?**

**A:**  If you encounter any problems or errors while setting up or testing the Dragon Medical One Multi-Computer Voice Control System, **please refer to the "Troubleshooting" section (Section 7) of this documentation first.**  The Troubleshooting section provides detailed solutions and recovery steps for many common issues that users may encounter, including installation problems, network communication errors, and browser automation failures.  Carefully read through the Troubleshooting section and follow the suggested solutions.  If you are still unable to resolve the issue after consulting the Troubleshooting section, please reach out for help using the contact information provided in Section 12, and provide detailed information about the problem you are encountering, including any error messages you are seeing and the steps you have already taken to troubleshoot.

**Q: Can I customize or extend this system for my specific needs?**

**A:**  Yes, absolutely! The Dragon Medical One Multi-Computer Voice Control Project is designed to be **open and extensible**.  If you have programming experience or are willing to learn, you can definitely customize and extend the system to meet your specific needs.  Section 8 "Developer Documentation - Extending and Modifying the Project" provides some initial guidance and ideas for customization.  The Python scripts (`src/server.py` and `src/client.py`) are written in a modular and relatively straightforward manner, making them reasonably easy to understand and modify.  You can customize things like:

*   **Adding support for more websites and search engines:**  You can modify the browser automation code in `src/client.py` to target different websites and search bar elements.
*   **Integrating different voice recognition software:**  If you prefer to use a voice recognition system other than Dragon Medical One, you can modify the server-side integration logic (in Phase 3) to work with your preferred voice recognition software's API or output methods.
*   **Adding more advanced features:**  You can add features like query history, logging, user interface enhancements, more sophisticated error handling, and many other functionalities, depending on your programming skills and requirements.

If you are interested in customizing or extending the project, it is recommended to have some basic programming knowledge in Python and familiarity with web technologies and network communication concepts.  Feel free to explore the code, experiment with modifications, and contribute back any improvements or customizations you develop!

## 16. Contribution Guidelines (Optional)

{{ If you plan to share this project and accept contributions from others, you can add guidelines here on how to contribute code, report issues, suggest features, etc.  For a personal project, this section can be omitted. }}

## 17. License (Optional)

{{ If you plan to share this project publicly, consider adding an open-source license to it, such as the MIT License, Apache 2.0 License, or GPL License.  A license specifies how others can use, modify, and distribute your code.  If you are not sure, you can learn more about open-source licenses at [https://choosealicense.com/](https://choosealicense.com/) and add a license file to your project.  For a personal project, a license is optional. }}

## 18. Contact

[Your Name/Contact Information] -  {{ Your preferred contact method, e.g., email address, GitHub profile link }}

---

{{ Add any other relevant notes or information here - e.g., acknowledgements, disclaimers, etc. }}

## 19. Push to GitHub - For Programmers

**Ready to put this project on GitHub for version control and sharing? Here's how:**

1.  **Make sure you have Git installed:** If you don't already have Git on your system, download and install it from [https://git-scm.com/downloads](https://git-scm.com/downloads).

2.  **Create a GitHub Repository:**
    *   Go to [https://github.com](https://github.com) and log in to your account.
    *   Click the "+" button in the top right corner and select "New repository".
    *   Choose a repository name (e.g., `DragonVoiceProject`).
    *   You can make it public or private as you prefer.
    *   **Important:**  **Do NOT initialize with a README, .gitignore, or license** at this stage. We will add our existing `docs/README.md` and other files.
    *   Click "Create repository".

3.  **Initialize Git in your Project Folder:**
    *   Open Command Prompt/Terminal.
    *   Navigate to your `DragonVoiceProject` folder using the `cd` command.
    *   Run the command: `git init`  (This creates a new Git repository in your project folder).

4.  **Add Project Files to Git:**
    *   Run the command: `git add .` (This stages all files in your project folder for your first commit).

5.  **Commit Your Initial Code:**
    *   Run the command: `git commit -m "Initial commit of Dragon Voice Project (Phase 2 base)"` (This saves your changes with a descriptive message).

6.  **Connect to Your GitHub Repository:**
    *   On your GitHub repository page, you will see instructions like:
        ```
        git remote add origin <repository URL>
        git branch -M main
        git push -u origin main
        ```
    *   **Copy the `<repository URL>`** from GitHub (it will look like `https://github.com/YourUsername/DragonVoiceProject.git` or `git@github.com:YourUsername/DragonVoiceProject.git`).
    *   **Run the commands in your Command Prompt/Terminal, replacing `<repository URL>` with the URL you copied:**
        ```bash
        git remote add origin <repository URL>
        git branch -M main
        git push -u origin main
        ```
    *   You might be asked to log in to your GitHub account during the `git push` command.

7.  **Your code is now on GitHub!**  Refresh your GitHub repository page in your browser - you should see all your project files there.

**Important Notes for GitHub:**

*   **`.gitignore` (Optional but Recommended):**  You might want to create a `.gitignore` file in your project root to exclude files that shouldn't be tracked in Git (e.g., `__pycache__` folders, `.pyc` files, virtual environment folders if you use them). You can find example `.gitignore` files for Python projects online.
*   **Regular Commits:**  Make frequent commits as you develop the project, with clear and descriptive commit messages. This helps track your progress and makes it easier to revert to previous versions if needed.
*   **Branching (For Larger Projects):** For more complex development, explore using Git branches to work on new features or bug fixes without directly affecting your main codebase.

---

**Tips for Best Use - Make it Smooth**

*   **Testing on Multi-Screen Setup:**  Since Robert has a three-screen setup, **make sure to test the `src/client.py` program on his computer with all three screens active and Chrome windows open across all screens.**  The `pygetwindow` library *should* be able to detect Chrome windows regardless of which screen they are on, but it's always good to verify in a multi-screen environment.  If you encounter any issues with window detection on multi-screen setups, you might need to explore more advanced window management techniques or library options.
