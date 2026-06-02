# 🖥️ OS System Monitor Agent

**Student:** Aibek Ulkhanov | **ID:** 24013558

An AI-inspired autonomous agent that continuously monitors operating system resources and takes action when thresholds are exceeded — like a smart alarm system for your computer.

---

## 🔍 Real-World Problem It Solves

Modern computers slow down or crash due to uncontrolled resource usage:

- A process silently consuming 100% CPU
- RAM running out with no warning
- Disk filling up until the system breaks

This agent watches your system **24/7** and alerts you the moment something goes wrong — before it becomes a crisis.

---

## 🧠 Agent Architecture: Observe → Think → Act

```
[ OS Kernel ]
      |
      v
[ OBSERVE: psutil collects CPU / RAM / Disk / Processes ]
      |
      v
[ THINK: Compare vs thresholds → Is anything overloaded? ]
      |
     / \
   YES   NO
    |     |
    v     v
  [ACT]  [Wait 5s, repeat]
  - Print Alert to terminal
  - Log event to monitor.log
  - Show top resource-consuming processes
  - (Optional) Suggest killing heaviest process
```

---

## ⚙️ Thresholds

| Resource | Alert Threshold |
| -------- | --------------- |
| CPU      | > 80%           |
| RAM      | > 85%           |
| Disk     | > 90%           |

---

## 🛠️ Tech Stack

| Tool      | Purpose                      |
| --------- | ---------------------------- |
| Python 3  | Core language                |
| `psutil`  | System metrics collection    |
| `rich`    | Beautiful terminal dashboard |
| `logging` | Persistent event log file    |

---

## 🚀 How to Run

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/os-system-monitor-agent
cd os-system-monitor-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the agent
python monitor_agent.py
```

Press `Ctrl+C` to stop. All alerts are saved to `monitor.log`.

---

## 📁 Project Structure

```
os-system-monitor-agent/
├── monitor_agent.py   # Main agent (Observe → Think → Act)
├── requirements.txt   # Dependencies
├── monitor.log        # Auto-generated alert log
└── README.md
```

---

## 📸 OS Concepts Demonstrated

- **Process Management** — listing and identifying top CPU processes
- **Memory Management** — real-time RAM monitoring
- **Resource Scheduling** — threshold-based automated decision making
- **File I/O** — persistent logging of system events

---