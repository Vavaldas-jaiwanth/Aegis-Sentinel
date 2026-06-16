# 🛡️ Enterprise AI Malware Scanner (Malware Defender)

![Build Status](https://img.shields.io/badge/build-passing-success)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A next-generation, AI-powered static malware analysis engine. **Malware Defender** leverages a highly optimized LightGBM model trained on the EMBER 2018 dataset to detect zero-day threats, ransomware, and malicious payloads without relying on outdated signature databases.

It extracts 2,351 microscopic features from Portable Executables (PE) and ZIP archives in real-time, executing high-speed inferences purely on the local endpoint.

---

## ✨ Key Features

1. **AI Decision Explainability (SHAP)**: Doesn't just block a file—it tells you *why*. Using native LightGBM `pred_contrib`, the system translates raw mathematical SHAP values into human-readable interpretations (e.g., `🔴 Suspicious` or `🟢 Legitimate`) to explain which features tipped the model's decision boundary.
2. **Real-Time Background Protection**: A lightweight Watchdog daemon that monitors high-risk directories (like `Downloads` and `Desktop`) and instantly intercepts new files as they touch the disk.
3. **Enterprise Web Dashboard**: A modern, dark-themed Streamlit UI for SOC analysts to manually investigate suspicious files. Seamlessly integrates with GitHub Releases to distribute the massive compiled Desktop Agent globally without crashing cloud memory limits.
4. **Memory-Safe Hashing Engine**: Generates SHA-256 hashes using 4MB chunking, ensuring the agent uses a flat memory profile even when scanning 10GB+ ISOs.
5. **Air-Gapped Privacy**: Operates 100% locally. No files, hashes, or telemetry are sent to the cloud.

---

## 🏗️ Architecture

The project is structured into a clean, modular, enterprise-ready architecture:

```text
MalwareDetect/
├── bin/
│   ├── dashboard.py           # Presentation: Streamlit Web UI
│   └── cli.py                 # Presentation: CLI Entry Point
├── engine/
│   ├── extractors/            # Mathematical Feature Extraction Layer
│   ├── ml/                    # Singleton Model Loading & SHAP Engine
│   ├── utils/                 # Loggers, Config Managers, and Hashers
│   ├── scanner.py             # Core inference workflow pipeline
│   ├── folder_scanner.py      # ThreadPool-powered batch scanning
│   └── watcher.py             # Event-driven real-time daemon
├── data/
│   ├── models/                # Git-LFS tracked LightGBM models
│   └── cache/                 # Local JSON caching to prevent rescans
└── docs/                      # Technical Documentation
```

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install the required dependencies. Note that this project uses **Git LFS** to pull down the massive 127MB ML model.

```bash
git clone https://github.com/YOUR_USERNAME/MalwareDetect.git
cd MalwareDetect
git lfs pull
pip install -r requirements.txt
```

### 2. Build the Desktop Agent

Compile the standalone `.exe` using the included PyInstaller spec file. Once compiled, you can upload `dist/MalwareDefender_Agent.zip` to your GitHub Releases page so it can be downloaded from the Web Dashboard.

```bash
pyinstaller malware_defender.spec
```

### 3. Launch the Web Dashboard

To launch the Streamlit Web UI for manual file scanning:

```bash
streamlit run bin/dashboard.py
```

### 4. Start the Background Agent (Protect Mode)

To enable real-time local endpoint protection:

```bash
python bin/cli.py protect
```

### 5. Scan via Command Line

Scan a single file and request AI decision reasoning:

```bash
python bin/cli.py scan -f suspicious_file.exe --explain
```

---

## 🧠 The Machine Learning Model

This engine uses a **LightGBM Gradient Boosting framework** instead of traditional deep learning. 

* **Why?** LightGBM provides unmatched inference speed (sub 50 milliseconds) and a tiny memory footprint, which is an absolute requirement for an endpoint security agent running in the background.
* **Training Data**: Trained on the [Endgame EMBER 2018](https://github.com/endgameinc/ember) dataset.
* **Threshold**: Calibrated at `0.8336` to mathematically ensure a strict 1% False Positive Rate for enterprise safety.

---

## 📖 Technical Documentation

For an exhaustive breakdown of the design patterns used (Singleton, Strategy, Facade), performance benchmarks, deployment strategies, and security vulnerabilities (TOCTOU), please read the [Project Technical Documentation](docs/PROJECT_TECHNICAL_DOCUMENTATION.md).

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
