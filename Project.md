# Dragon Medical One Multi-Computer Voice Control Project - Project Overview

**Version:** 1.0
**Date:** March 4, 2025

---

## 1. Project Summary

This project aims to create a voice-controlled system that significantly speeds up research and information gathering.  By using Dragon Medical One on a central computer, users can dictate a search query once and have it automatically populated and searched across multiple Chrome browser windows on other computers in a local network.

## 2. Key Features

*   **Voice-Activated Query Distribution:** Trigger search queries using voice dictation via Dragon Medical One.
*   **Multi-Computer Automation:** Distribute queries to multiple client computers on a local network.
*   **Automated Browser Input:** Automatically type queries into Chrome browser search bars on client computers.
*   **Simultaneous Searching:** Initiate searches across multiple computers and browsers at once.
*   **Simplified Workflow:** Eliminate manual typing and copy-pasting of queries across multiple systems.

## 3. Target Audience

This project is designed for:

*   Researchers
*   Medical Professionals
*   Data Analysts
*   Anyone who frequently needs to perform the same online searches across multiple computers or browser windows.

## 4. Technology Stack

*   **Python:** Primary programming language for server and client applications.
*   **Flask:**  Lightweight Python web framework for creating the server application.
*   **pyautogui:** Python library for GUI automation (keyboard and mouse control).
*   **pygetwindow:** Python library for window management (finding Chrome windows).
*   **requests:** Python library for making HTTP requests (client-server communication).
*   **Dragon Medical One (or similar):** Voice recognition software for voice input (Phase 3 integration).

## 5. Project Phases (Simplified)

1.  **Phase 1: Single Computer Demo:** Core browser automation on one computer.
2.  **Phase 2: Networked Query Distribution:**  Basic server-client communication and query distribution.
3.  **Phase 3: Dragon Medical One Integration:** Voice control via Dragon Medical One.
4.  **Phase 4: Testing and Refinement:**  Robustness, error handling, and user experience improvements.

## 6. Quick Start - Get Up and Running Fast

For detailed instructions, see `README.md`.  For a super quick start:

1.  **Install Python:** On server and at least one client computer.
2.  **Install Packages:** `pip install -r requirements.txt` in project folder on each computer.
3.  **Configure `client.py`:** Set `SERVER_URL` to server computer's IP address.
4.  **Run `server.py`** on the server computer.
5.  **Run `client.py`** on the client computer(s).
6.  **Test Phase 2:** Use online POST request tool to send query to server IP.

---

**For detailed setup, usage, and troubleshooting, please refer to the `README.md` file.**