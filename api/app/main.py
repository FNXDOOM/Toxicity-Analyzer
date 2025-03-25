from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:8000",
    "chrome-extension://fiphgbbekgakloeddmohebjphieiagmi"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (including OPTIONS)
    allow_headers=["*"],  # Allow all headers
)

@app.post("/analyze_toxicity")
async def analyze_toxicity(text: str):
    # Replace this with your actual toxicity analysis logic
    if "bad" in text.lower():
        toxicity_score = 0.9
        flagged_words = ["bad"]
    else:
        toxicity_score = 0.1
        flagged_words = []
    return {"toxicity_score": toxicity_score, "flagged_words": flagged_words}