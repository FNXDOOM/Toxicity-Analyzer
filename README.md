
# Toxicity Analyzer Project

This project consists of a FastAPI API for analyzing text toxicity and a Chrome extension that allows users to easily analyze selected text on any webpage using the API.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.7+**
*   **pip** (Python package installer)
*   **Google Chrome Browser**

## Setting up the FastAPI API

1.  **Navigate to the API directory:**

    ```bash
    cd Toxicity-Analyzer-Project/api
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**

    *   **On Windows:**

        ```bash
        .\venv\Scripts\activate
        ```

    *   **On macOS and Linux:**

        ```bash
        source venv/bin/activate
        ```

4.  **Install the required packages:**

    ```bash
    pip install fastapi uvicorn
    # or, for more complete functionality:
    pip install fastapi[standard]
    # or even for more complete functionality and optional dependencies
    pip install fastapi[all]
    ```

5.  **Run the FastAPI application:**

    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

    *   `app.main:app`: Specifies the module and object containing the FastAPI application.
    *   `--host 0.0.0.0`:  Allows the API to be accessed from any IP address (important for the Chrome extension).
    *   `--port 8000`:  Specifies the port number the API will listen on.
    *   `--reload`: Enables automatic reloading of the server when code changes are detected (useful for development).

    You should see output indicating that the Uvicorn server is running on `http://0.0.0.0:8000`.

## Loading the Chrome Extension

1.  **Open Chrome and go to `chrome://extensions/`.**
2.  **Enable "Developer mode"** in the top right corner.
3.  **Click "Load unpacked".**
4.  **Navigate to the `Toxicity-Analyzer-Project/extension` directory** and select it.

The "Toxicity Analyzer" extension should now be loaded.

## Using the Chrome Extension

1.  **Navigate to any website with text.**
2.  **Select some text.**
3.  **Right-click on the selected text.**
4.  **Choose "Analyze Toxicity"** from the context menu.
5.  **An alert box will appear, displaying the toxicity score** returned by the FastAPI API.

## Troubleshooting

*   **CORS Errors:** If you encounter CORS (Cross-Origin Resource Sharing) errors, ensure that:
    *   The `origins` list in `api/app/main.py` includes `chrome-extension://YOUR_EXTENSION_ID`, replacing `YOUR_EXTENSION_ID` with the actual ID of your Chrome extension (found on the `chrome://extensions` page).
    *   You have cleared your browser cache and restarted the Uvicorn server after making changes to the `origins` list.
    *   `CORSMiddleware` is added to FastAPI before defining routes.
*   **"Could not import module" Error:** If you get an error like "Could not import module 'app.main'", double-check that the `main.py` file is located in the correct directory and that you're running the `uvicorn` command from the `api` directory. Also, make sure the `__init__.py` file exists in the `app/` directory.
*   **400 Bad Request Errors:** These can be caused by malformed requests. Ensure the API is running and the extension is sending the correct headers (especially the `Origin` header). Clear your browser cache.
*   **Extension Not Loading:** Double-check the contents of `extension/manifest.json` for any errors. Make sure the file is valid JSON.

## Customization

*   **API Endpoint:** You can modify the `/analyze_toxicity` endpoint in `api/app/main.py` to implement your own toxicity analysis logic.
*   **Extension Behavior:** You can modify `extension/background.js` to change the way the extension interacts with the API (e.g., display the results in a different format, send different data to the API).
*   **UI:** You can customize the UI of the extension by modifying the `extension/popup.html` file.

## Contributing

Contributions are welcome! Please submit pull requests with bug fixes, new features, or improvements to the documentation.



