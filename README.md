# OmniGuard: Real-Time Multi-Modal Phishing Defense System

OmniGuard is a proactive, end-to-end machine learning system designed to detect and block sophisticated phishing attacks in real-time. Unlike traditional URL-blocking lists that rely on outdated databases, OmniGuard utilizes a hybrid Multi-Modal Deep Learning architecture to analyze both the structural anomalies of a URL and the visual rendering of the webpage simultaneously.



## Key Features

* Multi-Modal AI Architecture: Fuses visual features (captured via headless rendering and processed by ResNet18) with statistical tabular data to detect UI-spoofing attacks.
* High-Performance C++ Engine: Replaces slow Python string manipulations with a custom C++ module (compiled via Pybind11) to calculate Shannon entropy and extract URL features in sub-milliseconds.
* Real-Time Inference: Deployed as an asynchronous FastAPI microservice, ensuring near-instantaneous threat scoring.
* Zero-Friction User Experience: Integrates directly into the browser via a custom Chrome Extension, monitoring DOM events and alerting users before malicious payloads execute.
* Automated Data Pipeline: Utilizes Playwright to dynamically scrape, render, and label thousands of live phishing and legitimate websites to continuously update the training dataset.

## Technology Stack

* Deep Learning: PyTorch, TorchVision
* Backend API: FastAPI, Uvicorn, Pydantic
* Systems Programming: C++17, Pybind11, CMake
* Data Acquisition: Playwright (Asynchronous), Pandas
* Frontend/Client: Google Chrome Extension API (Manifest V3), JavaScript, HTML/CSS

## System Architecture

1. Browser Extension: Intercepts web navigation events and forwards the target URL to the local backend.
2. Inference API (FastAPI): Receives the request and orchestrates the feature extraction.
3. C++ Engine: Instantly computes statistical anomalies and URL structures.
4. PyTorch Model: Evaluates the combined tensor data (visual + statistical) to generate a threat confidence score.
5. Action: If the risk score exceeds the dynamic threshold, the extension injects a blocking overlay into the browser.

## Installation & Setup

### Prerequisites
* Python 3.9+
* C++17 compatible compiler (MSVC for Windows, GCC/Clang for Linux/macOS)
* Google Chrome

### Step 1: Clone the Repository
```
git clone https://github.com/alirenkucuk/OmniGuard-Phishing-Detection.git
cd OmniGuard-Phishing-Detection
```

### Step 2: Install Dependencies
```
pip install -r requirements.txt
playwright install chromium
```
### Step 3: Compile the C++ Engine
```
cd cpp_engine
python setup.py build_ext --inplace
```
### Step 4: Start the Inference Server
```
cd ../backend
uvicorn app:app --reload
```

### Step 5: Load the Chrome Extension
1. Open Google Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right corner.
3. Click "Load unpacked" and select the `browser_extension` directory from this project.

## Usage

With the FastAPI server running and the extension loaded, simply browse the web. The extension will silently analyze incoming URLs. If a phishing threat is detected, the inference engine will flag it with a 200 OK status in the terminal, and the extension will log the threat.
