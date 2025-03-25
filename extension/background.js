chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
      id: "analyze-toxicity",
      title: "Analyze Toxicity",
      contexts: ["selection"] // Only show the menu item when text is selected
    });
  });
  
  chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "analyze-toxicity" && info.selectionText) {
      const selectedText = info.selectionText;
  
      fetch("http://localhost:8000/analyze_toxicity", { // Replace with your API endpoint
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ text: selectedText })
      })
        .then(response => response.json())
        .then(data => {
          const toxicityScore = data.toxicity_score;
          alert(`Toxicity Score: ${toxicityScore}`);  // Display the score
        })
        .catch(error => {
          console.error("Error:", error);
          alert("Error analyzing toxicity.  Check the console for details.");
        });
    }
  });