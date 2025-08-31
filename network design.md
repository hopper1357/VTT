# Modular VTT Design Document

## 1. Vision

A Virtual Tabletop (VTT) platform designed to support multiple tabletop RPG systems (e.g., Dungeons & Dragons, Shadowrun, Star Wars, Traveller, etc.) through a **modular architecture**. The core system is written in **Python**, while **modules are developed in JavaScript**. The application supports **online multiplayer**, allowing GMs and players to connect in real time.

---

## 2. Core Design Principles

* **System Agnostic Core:** The Python engine handles networking, persistence, and UI rendering, while game rules are loaded via modules.
* **Sandboxed Modules:** Game-specific rules written in JavaScript are sandboxed to ensure safety and separation from the core.
* **Online Multiplayer:** Real-time play enabled through WebSockets, allowing players to share maps, rolls, and character updates.
* **Flexible UI Definitions:** Character sheets, rule references, and dice mechanics are defined in module metadata and scripts.
* **Persistence:** Campaigns, assets, and user data are saved to a database with asset storage for media.

---

## 3. System Components

### Core (Python)

* **Networking Layer:** FastAPI + WebSockets for real-time communication.
* **Session Manager:** Tracks players, GMs, campaigns, and states.
* **Rules API:** Loads and executes module-specific JS functions in a sandbox (QuickJS / Pyodide).
* **Persistence Layer:** Saves campaigns, character data, maps, and sessions.
* **Asset Manager:** Handles storage/retrieval of maps, tokens, music, etc.

### Modules (JavaScript)

* **Rules Engine:** Dice mechanics, character progression, initiative handling.
* **UI Definitions:** JSON-based character sheets, reference materials.
* **Scripts:** Player macros, auto-calculations, rules enforcement.
* **Sandbox Execution:** Runs in-browser for client-side features, and inside Python JS runtime for validation.

### Database Layer

* **Relational DB (PostgreSQL/SQLite):** Stores campaigns, users, sessions, module references.
* **Blob Storage (S3/Minio/File System):** Stores assets like maps, tokens, audio.

### Clients

* **Web Browser (React/Vue/Svelte):** Web-based interface for easy access.
* **Desktop Client (Electron/Tauri):** For offline and heavy asset use.
* **Mobile Client (Optional, Web-first):** Responsive design for tablets/phones.

---

## 4. Networking Architecture

### High-Level Flow

```
Players (Clients) ──▶ Game Server (Python) ──▶ Database (Game State, Assets, Users)
          ▲                                      │
          │                                      ▼
          └─────────── Real-time Sync ◀───────── Modules (JavaScript)
```

### Components

* **Clients:** Send actions (rolls, moves) and render updates.
* **Game Server:** Manages sessions, validates rules, syncs states.
* **Modules:** Loaded per campaign, enforce system rules.
* **Database & Assets:** Persist all long-term campaign data.

### Networking Diagram

```
+----------------+      WebSockets/API      +----------------+
|   Player A     | <──────────────────────> |                |
|  Browser/Client|                          |                |
+----------------+                          |                |
                                            |   Game Server  |
+----------------+      WebSockets/API      |   (Python)     |
|   Player B     | <──────────────────────> |                |
|  Desktop Client|                          |                |
+----------------+                          |                |
                                            |   - Session Mgr|
+----------------+      REST for assets     |   - Rules API  |
|  Player C      | <──────────────────────> |   - DB Sync    |
|  Mobile Client |                          |                |
+----------------+                          +----------------+
                                                       │
                                                       ▼
                                                +-------------+
                                                |  Database   |
                                                +-------------+
                                                       │
                                                       ▼
                                                +-------------+
                                                |  Assets/Map |
                                                +-------------+
```

### Real-Time State Sync Example

1. Player A moves a token → Client sends **“MOVE\_TOKEN”** event to server.
2. Server validates via module rules → updates session state.
3. Server broadcasts **“TOKEN\_MOVED”** event to all clients.
4. All clients instantly update the map.

---

## 5. Scalability Considerations

* Use **Redis pub/sub** for multi-server deployments.
* Sessions run in-memory, persisted to DB on save/interval.
* Modules loaded per-session, allowing multiple game systems simultaneously.

---

## 6. Future Enhancements

* **Voice/Video Chat integration** (WebRTC).
* **Marketplace for Modules/Assets.**
* **Offline Mode** with local saves.
* **Custom Script Editor** for GMs to write quick macros.

---

This design ensures a **flexible, modular, and scalable online VTT**, with Python powering the server and JS powering the rules and modules.
