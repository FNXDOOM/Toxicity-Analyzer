import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn
import traceback # Import traceback for detailed error logging

# --- Configuration ---
load_dotenv()  # Load variables from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
    print("=" * 60)
    print("ERROR: GEMINI_API_KEY environment variable not found or not set.")
    print("Please create a .env file in the 'backend' directory with:")
    print("GEMINI_API_KEY=YOUR_ACTUAL_API_KEY")
    print("You can get a key from Google AI Studio: https://aistudio.google.com/app/apikey")
    print("=" * 60)
    model = None # Indicate model is not available
else:
    try:
        # Configure the Gemini client
        genai.configure(api_key=GEMINI_API_KEY)
        # Select the model
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        print("Gemini API Configured Successfully.")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        model = None


# --- FastAPI App Setup ---
app = FastAPI(title="Toxicity Analysis API")

# --- CORS Configuration ---
# Store JUST the ID letters here (replace with your actual ID)
CHROME_EXTENSION_ID_ONLY = "cehmnnnpfakbklhioabdljhjilodpgnd" # <-- EDIT THIS LINE with your actual ID letters

origins = [
    "http://localhost",
    "http://localhost:8000",
    f"chrome-extension://{CHROME_EXTENSION_ID_ONLY}" # <--- CORRECTED: Construct the full origin here
    # Add any other origins if needed
]

# Optional: Adjust the warning check if you keep it
if not CHROME_EXTENSION_ID_ONLY or CHROME_EXTENSION_ID_ONLY == "YOUR_EXTENSION_ID_HERE":
     print("=" * 60)
     print("WARNING: CHROME_EXTENSION_ID_ONLY is not set correctly in main.py.")
     print("Find your extension's ID in chrome://extensions (Developer Mode on)")
     print("and set the CHROME_EXTENSION_ID_ONLY variable.")
     print("The extension might not be able to connect until this is fixed.")
     print("=" * 60)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Uses the corrected origins list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Body Model ---
class AnalyzeRequest(BaseModel):
    text: str

# --- Gemini Safety Settings Mapping ---
RATING_TO_SCORE = {
    "NEGLIGIBLE": 0.1,
    "LOW": 0.4,
    "MEDIUM": 0.7,
    "HIGH": 0.95,
    "UNKNOWN": 0.0, # Handle potential unknowns
    "UNSPECIFIED": 0.0,
}
BLOCKED_SCORE = 1.0 # Score if Gemini blocks the prompt outright


# --- API Endpoint ---
@app.post("/analyze_toxicity")
async def analyze_toxicity(request: AnalyzeRequest):
    """
    Analyzes the input text for toxicity using the Gemini API's safety ratings.
    Receives text from the Chrome extension and returns analysis results.
    """
    if model is None:
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail="Gemini API is not configured or failed to initialize. Check API Key and server logs."
        )

    text_to_analyze = request.text
    # Log input text length and snippet, but not the full text anymore
    print(f"Backend received text (length {len(text_to_analyze)}): '{text_to_analyze[:100]}...'")
    if not text_to_analyze:
        print("Backend: Received empty text, returning 0.0 score.")
        return {"toxicity_score": 0.0, "flagged_categories": [], "flagged_words": [], "block_reason": None}

    try:
        # Define safety settings for the API call. Using lower threshold for testing.
        print("DEBUG: Using safety threshold: BLOCK_LOW_AND_ABOVE") # Log threshold being used
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"}
        ]

        # --- REMOVED DEBUG LOG FOR EXACT INPUT TEXT ---
        # print(f"DEBUG: EXACT text being sent to Gemini: ---START---\n{text_to_analyze}\n---END---")
        # --------------------------------------------

        print("Sending request to Gemini API...")
        response = model.generate_content(
            text_to_analyze,
            safety_settings=safety_settings,
            generation_config={"candidate_count": 1} # Only need prompt feedback
        )
        print("Received response from Gemini API.")

        # --- CRITICAL DEBUG LOGS (Keep these) ---
        print("-" * 20, "GEMINI RESPONSE DEBUG START", "-" * 20)
        if hasattr(response, 'prompt_feedback'):
            print(f"RAW Gemini Prompt Feedback object: {response.prompt_feedback}") # Log the whole object
            if response.prompt_feedback:
                 print(f"  - Block Reason: {response.prompt_feedback.block_reason}")
                 print(f"  - Safety Ratings object: {response.prompt_feedback.safety_ratings}") # Log the list of ratings
            else:
                 print("  - Prompt Feedback object exists but is None or Falsy (e.g., empty).")
        else:
            print("  - Response object has NO 'prompt_feedback' attribute.")
        print("-" * 20, "GEMINI RESPONSE DEBUG END", "-" * 20)
        # --- END CRITICAL DEBUG LOGS ---

        max_score = 0.0 # Initialize score
        flagged_categories = []
        block_reason_str = None

        # Check if the prompt itself was blocked
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback and response.prompt_feedback.block_reason:
             block_reason_str = response.prompt_feedback.block_reason.name
             print(f"DEBUG: Prompt blocked. Reason: {block_reason_str}. Setting score to {BLOCKED_SCORE}")
             max_score = BLOCKED_SCORE
             if response.prompt_feedback.safety_ratings:
                 flagged_categories = [
                    rating.category.name for rating in response.prompt_feedback.safety_ratings
                    if rating.probability.name in ["LOW", "MEDIUM", "HIGH"]
                ]

        # If not blocked, evaluate the safety ratings
        elif hasattr(response, 'prompt_feedback') and response.prompt_feedback and response.prompt_feedback.safety_ratings:
            print("DEBUG: Processing safety ratings...")
            for rating in response.prompt_feedback.safety_ratings:
                try:
                    category_name = rating.category.name if hasattr(rating, 'category') and hasattr(rating.category, 'name') else "UNKNOWN_CATEGORY"
                    probability_name = rating.probability.name if hasattr(rating, 'probability') and hasattr(rating.probability, 'name') else "UNKNOWN_PROBABILITY"

                    print(f"  DEBUG - Rating Category: {category_name}, Received Probability Name: '{probability_name}'")
                    score = RATING_TO_SCORE.get(probability_name, 0.0)
                    print(f"  DEBUG - Mapped Score: {score}")

                    if score > max_score:
                        max_score = score
                        print(f"    DEBUG - New max_score: {max_score}")
                    if probability_name in ["LOW", "MEDIUM", "HIGH"]:
                        flagged_categories.append(category_name)
                except AttributeError as ae:
                    print(f"  WARN - Could not access attributes of a rating object: {ae}. Rating object: {rating}")

            print(f"DEBUG: Finished processing ratings. Final max_score before return: {max_score}")

            # --- Optional: Default score if max_score is still 0.0 after processing ratings ---
            if max_score == 0.0:
                 print("DEBUG: All processed ratings resulted in score 0.0 or less. Defaulting to NEGLIGIBLE score (0.1).")
                 max_score = 0.1 # Default to NEGLIGIBLE score
            # --- End Optional Default ---

        else:
             # Log if the ratings loop was skipped or if feedback/ratings were missing
             print("DEBUG: No safety ratings found or processed (prompt_feedback missing, empty, or ratings list empty).")
             # --- Optional: Default score if no ratings ---
             print("DEBUG: Defaulting to NEGLIGIBLE score (0.1) due to missing ratings.")
             max_score = 0.1 # Default to NEGLIGIBLE score
             # --- End Optional Default ---


        flagged_words = []

        print(f"Backend returning: {{'toxicity_score': {max_score}, 'flagged_categories': {list(set(flagged_categories))}, 'block_reason': {block_reason_str}, ...}}")
        return {
            "toxicity_score": max_score,
            "flagged_categories": list(set(flagged_categories)),
            "flagged_words": flagged_words,
            "block_reason": block_reason_str
        }

    except Exception as e:
        print(f"ERROR processing request: {e}")
        print(traceback.format_exc()) # Print full traceback
        raise HTTPException(
             status_code=500,
             detail=f"Error during toxicity analysis: {str(e)}"
        )

# --- Root Endpoint (Optional: for testing if server is running) ---
@app.get("/")
async def read_root():
    return {"message": "Toxicity Analysis API is running. Use the POST /analyze_toxicity endpoint."}


# --- Run the server (for local execution) ---
if __name__ == "__main__":
    print("Starting Uvicorn server on http://localhost:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)