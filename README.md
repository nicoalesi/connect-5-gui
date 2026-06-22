# Connect-5 GUI

A Python-based graphical user interface for playing **Connect-5** .

The GUI is built using Pygame and communicates with external agents using a simple stdin/stdout protocol similar to UCI-style engines.

The primary purpose of this software is to support the development and testing of the Omega5 agent engine. It is not designed to be general-purpose, or reusable, but it may be freely adapted to suit individual needs.

---

## Features

- Player vs Agent (PVA) mode
- Agent vs Agent (AVA) mode
- Real-time visualization using Pygame
- Asynchronous communication with external agents
- Configurable agents and search depths via JSON config file

---

## Project structure

```
├─ main.py
├─ game_gui.py
├─ agent_interface.py
└─ config.json
```

---

## How it works

The Python GUI **does not** implement any AI logic.

It acts as a visualizer and communicates with one or more agents that run as subprocesses using a specific protocol.

---

## Configuration file

There are two supported modes:
- **Player vs. Agent (PVA)**: The player plays against a single agent.
- **Agent vs. Agent (AVA)**: Two agents play against each other.

<br>

Each agent must specify:
- A binary executable path
- A search depth

<br>

The configuration is set using a JSON config file.

### Example (PVA)
`config.json`
```json
{
    "mode": "PVA",
    "agents": {
        "1": {
            "binary": "./engine",
            "depth": 6
        }
    }
}
```

### Example (AVA)
`config.json`
```json
{
  "mode": "AVA",
  "agents": {
      "1": {
          "binary": "./engine1",
          "depth": 6
      },
      "2": {
          "binary": "./engine2",
          "depth": 6
      }
  }
}
```

---

## Agent communication protocol

Every agent that is linked to the GUI is required to support the following commands.

### Set position
```
position startpos moves <move> <move> ...
```

### Start search
```
go <depth>
```

### Agent move
```
bestmove <move>
```

Moves are encoded as integers in the range [0, 99], representing board coordinates.

### Board indexing

By default, the board is a 10x10 grid.

```
00 01 02 03 04 05 06 07 08 09
10 11 12 13 14 15 16 17 18 19
20 21 22 23 24 25 26 27 28 29
30 31 32 33 34 35 36 37 38 39
40 41 42 43 44 45 46 47 48 49
50 51 52 53 54 55 56 57 58 59
60 61 62 63 64 65 66 67 68 69
70 71 72 73 74 75 76 77 78 79
80 81 82 83 84 85 86 87 88 89
90 91 92 93 94 95 96 97 98 99
```

A move can be encoded as:
```
move = row * 10 + col
```

---

## Installation

### Requirements
- Python 3.9+
- Pygame

A virtual environment is recommended.

### Running the GUI

```
python3 main.py config.json
```

---

## Responsibilities division

### Python GUI
- Rendering board with Pygame
- Handling user input
- Managing game state
- Communicating with external engines

### Agent engine
- Board evaluation
- Move generation
- Search

---

## Notes

- Input is not validated nor sanitized
- Invalid engine behavior may cause undefined game states
