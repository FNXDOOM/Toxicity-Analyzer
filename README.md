# Toxicity Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

A simple web application built with Gradio to analyze text input and predict scores for various types of toxicity using the `detoxify` library.

## Features

*   Analyzes text for multiple toxicity categories:
    *   Toxicity
    *   Severe Toxicity
    *   Obscene
    *   Threat
    *   Insult
    *   Identity Hate
*   Uses the pre-trained `'original'` model from the `detoxify` library.
*   Provides an easy-to-use web interface powered by Gradio.

## Project Structure

```bash
Toxicity-Analyzer/
├── .git/                     # Git version control data
├── .gitignore                # Specifies intentionally untracked files
├── backend/                  # Contains the server-side application
│   ├── main.py               # Python script running Gradio/Detoxify server
│   ├── requirements.txt      # Python dependencies for the backend
│   ├── Dockerfile            # (Optional) For containerizing the backend
│   └── ...                   # (Optional) Any other backend config/helper files
│
├── extension/                # Contains the browser extension files
│   ├── manifest.json         # Core configuration file for the extension (required)
│   ├── popup.html            # HTML for the extension's popup window
│   ├── popup.js              # JavaScript logic for the popup (API calls, UI updates)
│   ├── popup.css             # (Optional) CSS styling for the popup
│   ├── background.js         # (Optional) Background script (Service Worker for MV3) for tasks
│   ├── content_script.js     # (Optional) JS injected into web pages
│   ├── icons/                # Directory for extension icons
│   │   ├── icon16.png
│   │   ├── icon48.png
│   │   └── icon128.png
│   └── ...                   # (Optional) Other JS libraries, CSS files, assets
│
├── LICENSE                   # Project license (e.g., MIT)
└── README.md                 # Main documentation file
```

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/FNXDOOM/Toxicity-Analyzer.git
    cd Toxicity-Analyzer
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: This will install `torch`, `detoxify`, `gradio`, `transformers`, and their dependencies. `torch` can be a large download.*

## Usage

1.  **Run the application:**
    ```bash
    python main.py
    ```

2.  **Access the interface:**
    *   The script will start a local web server and print the URL (usually `http://127.0.0.1:7860` or similar).
    *   Open this URL in your web browser.

3.  **Analyze text:**
    *   Enter the text you want to analyze into the input text box.
    *   Click the "Submit" button (or wait if live updates are enabled).
    *   The predicted toxicity scores for each category will be displayed.

## How it Works

This tool uses the `detoxify` library, which provides access to pre-trained models for toxicity classification. The `main.py` script loads the `'original'` `detoxify` model. When you input text through the Gradio interface, the script passes the text to the model, which returns prediction scores between 0 and 1 for each toxicity category. These scores are then displayed back in the Gradio interface.

## Key Dependencies

*   [Detoxify](https://github.com/unitaryai/detoxify): The core library for toxicity detection.
*   [Gradio](https://www.gradio.app/): Used to create the simple web UI.
*   [PyTorch](https://pytorch.org/): The deep learning framework used by `detoxify`.
*   [Transformers](https://huggingface.co/docs/transformers/index): Often used under the hood by libraries like `detoxify` for model loading and handling.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue if you find bugs or have suggestions for improvements.
