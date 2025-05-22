# 🛡️ AML Monitoring System using GCP Agents

This project is designed to monitor and analyze suspicious financial activities using two AI agents. It includes a web-based interface where you can view customer risks and dive deep into individual cases.

---

## 📌 Features

- **dashboard_agent**: Displays overall customer risk and suspicious data.
- **root_agent**: Provides detailed insights for a given customer by `customer_id`.
- Runs locally and is deployable to Google Cloud using `gcloud`.
- Web UI built to trigger and interact with both agents.

---

## 🚀 Getting Started

### ✅ Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- pip
- `adk` (Agent Deployment Kit CLI)
- Google Cloud SDK (`gcloud`) — for deployment
- WSL (Windows Subsystem for Linux) — if using on Windows

---

### 🛠️ Setup Instructions
```bash
git clone https://github.com/shriram05/gcp_ssp.git
cd aml_monitoring_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
adk web
```
