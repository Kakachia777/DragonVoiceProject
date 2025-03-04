# Dragon Voice Project - Technical Architecture

## System Overview

The Dragon Voice Project implements a distributed system for voice-controlled multi-computer browser automation. This document outlines the technical architecture, component interactions, and design decisions.

## Architecture Diagram

```
+------------------+      +------------------+      +------------------+
| Dragon Medical   |      |                  |      |     Client 1     |
|      One         | ---> |     Server       | ---> | (Chrome Browser) |
| (Voice Input)    |      | (Query Handler)  |      |                  |
+------------------+      +------------------+      +------------------+
                                  |
                                  |                 +------------------+
                                  |                 |     Client 2     |
                                  +---------------> | (Chrome Browser) |
                                  |                 |                  |
                                  |                 +------------------+
                                  |
                                  |                 +------------------+
                                  |                 |     Client N     |
                                  +---------------> | (Chrome Browser) |
                                                    |                  |
                                                    +------------------+
```

## Component Architecture

### 1. Server Component

**Purpose**: Accepts and distributes search queries to client computers.

**Key Technologies**:
- Python 3.x
- Flask web framework
- HTTP REST API

**Core Modules**:
- **Query Receiver**: Accepts queries via HTTP POST requests
- **Query Storage**: Maintains the most recent query
- **Query Provider**: Serves queries to clients via HTTP GET requests
- **Dragon Integration**: Monitors for voice-dictated queries (Phase 3)

**API Endpoints**:
- `/send_query` (POST): Receives new search queries
- `/get_query` (GET): Provides the most recent query to clients
- `/check_dragon_file` (GET): Checks for Dragon Medical One output (Phase 3)
- `/check_clipboard` (GET): Alternative Dragon integration method (Phase 3)

**Data Flow**:
1. Server receives query via POST request or Dragon integration
2. Query is stored in memory
3. Clients poll the server periodically to retrieve the latest query

### 2. Client Component

**Purpose**: Retrieves queries from the server and automates browser input.

**Key Technologies**:
- Python 3.x
- Requests library for HTTP communication
- PyGetWindow for window management
- PyAutoGUI for keyboard automation
- Threading for non-blocking operation

**Core Modules**:
- **Server Poller**: Periodically checks server for new queries
- **Window Manager**: Identifies and activates Chrome windows
- **Input Automator**: Types queries and executes searches
- **Query Tracker**: Prevents duplicate processing of the same query

**Data Flow**:
1. Client polls server at regular intervals
2. When a new query is detected, client identifies all Chrome windows
3. For each window, client:
   - Activates the window
   - Clears existing content
   - Types the query
   - Presses Enter to execute search

### 3. Testing Component

**Purpose**: Validates core browser automation functionality without network dependencies.

**Key Technologies**:
- Python 3.x
- PyGetWindow
- PyAutoGUI

**Core Modules**:
- **Window Detector**: Identifies Chrome windows
- **Keyboard Simulator**: Types queries and executes searches

## Data Models

### Query Object
```python
{
    "query_text": string,      # The search query text
    "timestamp": datetime,     # When the query was received
    "source": string           # How the query was received (POST, file, clipboard)
}
```

### Configuration Model
```python
{
    "server": {
        "host": string,        # Server hostname/IP
        "port": integer,       # Server port (default: 5000)
        "poll_interval": float # How often to check for Dragon input (seconds)
    },
    "client": {
        "server_url": string,  # URL of the server
        "poll_interval": float # How often to check for new queries (seconds)
        "typing_delay": float  # Delay between keystrokes (seconds)
    },
    "browser": {
        "window_title": string # Window title pattern to match
    }
}
```

## Communication Protocols

### Server-Client Communication
- **Protocol**: HTTP/REST
- **Data Format**: Plain text and JSON
- **Authentication**: None in initial version (local network only)
- **Error Handling**: HTTP status codes and error messages

### Query Distribution Process
1. Client sends GET request to `/get_query`
2. Server responds with the latest query
3. Client compares with previously processed query
4. If new, client processes the query
5. Client waits for poll interval before requesting again

## Security Considerations

The initial version focuses on functionality rather than security, with these assumptions:
- System operates on trusted local networks only
- No sensitive data is transmitted
- No authentication is implemented in Phase 1-2

Future security enhancements:
- Basic authentication for API endpoints
- HTTPS for encrypted communication
- Input validation and sanitization
- Rate limiting for API endpoints

## Scalability and Performance

### Current Limitations
- In-memory query storage (no persistence)
- Single server instance (no load balancing)
- Sequential browser automation (one window at a time)

### Future Scalability Improvements
- Database backend for query storage
- Multiple server instances with load balancing
- Parallel browser automation
- WebSocket communication for reduced latency

## Technical Debt and Considerations

- **Error Handling**: Needs more robust implementation
- **Logging**: Currently uses basic console output
- **Configuration**: Hardcoded values should be moved to config files
- **Browser Support**: Chrome-specific logic limits flexibility
- **Testing**: Needs comprehensive automated testing

## Deployment Architecture

### Development Environment
- Local Python installation
- Flask development server
- Direct execution of scripts

### Production Environment
- Python virtual environments
- Potential Windows service or Linux daemon
- Configuration files for each environment
- Logging to files rather than console

## Integration Points

### Dragon Medical One Integration Options
1. **File-Based Integration**:
   - Dragon outputs to text file
   - Server monitors file for changes
   - Simple but may have performance issues

2. **Clipboard-Based Integration**:
   - Dragon copies to clipboard
   - Server monitors clipboard for changes
   - More efficient but may conflict with other applications

3. **Direct API Integration** (if available):
   - Direct communication with Dragon API
   - Most efficient but depends on available Dragon interfaces

### Future Integration Possibilities
- Integration with other voice recognition systems
- Support for additional browsers
- Integration with specific web applications
- Mobile device support 