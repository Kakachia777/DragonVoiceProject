## 👨‍💻 Push to GitHub - For Programmers

**Ready to put this project on GitHub for version control and sharing? Here's how:**

1.  **Make sure you have Git installed:** If you don't already have Git on your system, download and install it from [https://git-scm.com/downloads](https://git-scm.com/downloads).
    // ... (rest of "Push to GitHub" section - unchanged) ...

---

## 👨‍💻 For Programmers - Project Technical Overview

If you are a programmer joining the Dragon Medical One Multi-Computer Voice Control Project, this section provides a detailed technical overview to get you started. For detailed instructions and user guides, please refer to the other sections of this `README.md` file.

### 1. Project Summary (Technical Perspective)

#### 1.1 System Architecture & Design Philosophy

The Dragon Medical One Multi-Computer Voice Control Project implements a distributed automation system utilizing a client-server architecture to solve a specific workflow bottleneck: efficiently distributing voice-dictated search queries to multiple browser interfaces across a multi-screen or multi-computer setup.

**Core Architecture:**
* **Separation of Concerns:** The system separates query acquisition (server-side, voice-driven) from query execution (client-side, browser automation).
* **Stateless Communication Model:** A lightweight HTTP-based communication protocol between server and clients minimizes dependencies and simplifies scaling.
* **Polling-Based Query Distribution:** Client-initiated polling rather than server-pushed updates provides robustness in variable network conditions.
* **Thread-Safe Design:** Background threads for network operations ensure non-blocking UI interactions.

**Technical Implementation Stack:**
* **Backend:** Python 3.x with Flask for HTTP services
* **Frontend Automation:** Python with pyautogui/pygetwindow for UI manipulation
* **Inter-Process Communication:** HTTP REST endpoints
* **Voice Processing:** Integration with Dragon Medical One (third-party)

#### 1.2 Component Breakdown

**Server Component (`src/server.py`):**
* **Implementation:** Flask-based RESTful service (chosen for its lightweight footprint and rapid development capabilities)
* **Endpoints:**
  * `/send_query` (POST): Accepts form data with 'query' parameter
  * `/get_query` (GET): Returns the most recently stored query
  * `/check_dragon_file` (GET): [Phase 3] Monitors text file for Dragon Medical One input
  * `/check_clipboard` (GET): [Phase 3-Alt] Monitors system clipboard for Dragon Medical One input
* **In-Memory State Management:** Currently utilizes a global `last_query` variable for query storage, sufficiently performant for projected user load.
* **Thread Safety:** Flask's development server handles concurrent requests with a thread-per-request model.
* **Cross-Origin Considerations:** CORS not implemented as the system operates on local networks only.
* **Startup Process:** Initializes HTTP listener on port 5000, binding to all network interfaces (0.0.0.0).

**Client Component (`src/client.py`):**
* **Implementation:** Standalone Python executable leveraging threading for non-blocking operation
* **Network Layer:** Implements HTTP client using the `requests` library with configurable timeout handling
* **UI Automation:**
  * **Window Management:** Uses pygetwindow for Chrome window identification and focus manipulation
  * **Input Simulation:** Leverages pyautogui for keyboard event simulation with configurable delays
  * **Idempotency Handling:** Tracks last processed query to prevent duplicate executions
* **Threading Model:** 
  * Primary thread: Maintains application lifecycle and handles signals
  * Secondary thread: Manages polling and browser automation, preventing UI freezing
* **Error Handling:** Implements graceful exception handling for network timeouts, window management failures, and automation errors

**Testing Component (`src/quick_test.py`):**
* **Implementation:** Simplified single-machine testing harness
* **Purpose:** Validates browser automation functionality without network dependencies
* **Usage:** Developer and end-user diagnostic tool

#### 1.3 Data Flow & Processing Pipeline

1. **Input Acquisition:**
   * [Current] Manual HTTP POST to `/send_query` endpoint
   * [Phase 3] Dragon Medical One dictation → text file (`C:/dragon_query.txt`) → Server polling
   * [Alternative] Dragon Medical One dictation → clipboard → Server polling

2. **Server Processing:**
   * Request validation and sanitization
   * Query storage in server memory
   * Query availability via `/get_query` endpoint

3. **Client Processing:**
   * Asynchronous polling of server endpoint (1-second intervals, configurable)
   * Differential analysis (new query vs. previous query)
   * Window enumeration using Win32 API (via pygetwindow)
   * Sequential window activation and input simulation

4. **Browser Interaction:**
   * Window activation (brings window to foreground)
   * Content selection (Ctrl+A)
   * Content deletion (Delete key)
   * Query insertion (individual keystrokes)
   * Search execution (Enter key)

#### 1.4 Technical Design Decisions & Rationale

**Why Flask over alternatives?**
* Lightweight footprint compared to Django/FastAPI
* Built-in development server simplifies deployment
* Sufficient performance characteristics for expected load
* Familiar syntax for potential maintainers

**Why polling over WebSockets/push notifications?**
* Simplifies client implementation
* Reduces system complexity
* More robust in unstable network environments
* Acceptable performance given low-frequency updates

**Why pyautogui over Selenium/browser automation frameworks?**
* Works across arbitrary browser-based applications
* No browser-specific dependencies or plugins required
* Simulates actual user input for maximum compatibility
* Handles non-standard web applications and internal sites

**Tradeoffs in Current Implementation:**
* **Performance vs. Simplicity:** The polling approach introduces latency but significantly simplifies the architecture
* **Robustness vs. Features:** Focus on core functionality over edge cases
* **Security Considerations:** HTTP (not HTTPS) acceptable for local network, non-sensitive data

#### 1.5 Current Limitations & Technical Debt

* **Error Recovery:** Limited retry logic for failed operations
* **Logging:** Basic console output rather than structured logging
* **Configuration:** Hardcoded parameters rather than configuration files
* **Browser Support:** Chrome-specific window detection logic
* **Scalability:** In-memory query storage limits horizontal scaling

#### 1.6 Deployment Considerations

* **Network Requirements:** All devices must be on same local network
* **Firewall Configuration:** Port 5000 TCP access required between clients and server
* **Python Environment:** Consistent Python 3.x environment across all machines
* **Server Reliability:** No persistence layer; server restart clears current query
* **Client Distribution:** Manual installation on each client machine

### 2. Code Structure and Key Files

The project code is organized as follows:

*   **`src/` Folder:** Contains the core Python scripts:
    *   **`src/server.py`:**  The Flask server application for query distribution.
    *   **`src/client.py`:** The client-side script for browser automation and query retrieval.
    *   **`src/quick_test.py`:** A utility script for testing browser automation on a single computer (Phase 1 testing).
*   **`docs/` Folder:** Contains project documentation (including this `README.md` file).
*   **`requirements.txt`:** Lists Python package dependencies.

### 3. Key Technologies and Libraries

*   **Python:** The primary programming language.
*   **Flask:**  A micro web framework used for creating the server application (`src/server.py`).
*   **pyautogui:** Python library for GUI automation (simulating keyboard and mouse input) - used in `src/client.py` and `src/quick_test.py`.
*   **pygetwindow:** Python library for window management (finding and activating Chrome browser windows) - used in `src/client.py` and `src/quick_test.py`.
*   **requests:** Python library for making HTTP requests (for client-server communication in Phase 2) - used in `src/client.py`.
*   **pyperclip:** Python library for clipboard access (potential future use for Dragon Medical One integration).

### 4. Development Setup - Quick Guide for Programmers

To set up a development environment:

1.  **Install Python 3.x:** Ensure Python 3.x is installed on your development machine (see detailed instructions in Section 3.1 "Install Python 3.x").
2.  **Install Python Packages:** Navigate to the `DragonVoiceProject` directory in your terminal/command prompt and run: `pip install -r requirements.txt` (see Section 3.2 "Install Required Python Packages").
3.  **Run Scripts from Command Line:** It is recommended to run `src/server.py` and `src/client.py` from the command line for testing browser automation to avoid potential permission issues.

### 5. Workflow and Data Flow (Simplified)

1.  **Voice Input (Future Phase 3 Integration):**  In the planned Phase 3, Dragon Medical One voice dictation will be the input method. Currently, for testing Phase 2, queries are manually sent to the server via HTTP POST requests.
2.  **Query Storage (Text File - Phase 3):**  For Dragon Medical One integration (Phase 3 - Option A), the dictated query will be saved to a text file (`C:/dragon_query.txt`). The server reads from this file.
3.  **Server Receives Query (`src/server.py`):** The `src/server.py` program (Flask server) is responsible for receiving and storing the latest query.
4.  **Client Retrieves Query (`src/client.py`):**  `src/client.py` periodically sends GET requests to the server's `/get_query` endpoint to check for new queries.
5.  **Browser Automation (`src/client.py`):** Upon receiving a new query, `src/client.py` uses `pygetwindow` to find Chrome windows and `pyautogui` to type the query and press "Enter" in each window.

### 6. Extending and Modifying the Project

*   Refer to Section 8 "Developer Documentation - Extending and Modifying the Project" (currently under development in `docs/README.md`) for more detailed information on code structure, key functions, and ideas for customization.
*   Feel free to explore the code, experiment with modifications, and contribute improvements.

### 7. Version Control - GitHub (Recommended)

*   It is highly recommended to use Git for version control. See Section 19 "Push to GitHub - For Programmers" for instructions on setting up a GitHub repository for this project.
*   Make regular commits with clear and descriptive commit messages.
*   Consider using branches for feature development or bug fixes.

---
**(Rest of docs/README.md content remains unchanged after this section)** 