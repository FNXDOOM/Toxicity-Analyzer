// content-script.js

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("Content script received message:", request.action); // Log received action
  
    // Respond to ping messages to confirm content script is loaded
    if (request.action === "ping") {
      console.log("Content script: Responding to ping.");
      sendResponse({status: "ok"});
      // IMPORTANT: Only return true for actions where you intend to use sendResponse
      return true; // Keep the message channel open for the asynchronous response
    }
  
    // Handle showing the result/error notification
    if (request.action === "showToxicityResult") {
      console.log("Content script: Displaying toxicity result.");
      displayResultOnPage(request.result, request.isError);
      // DO NOT return true here, as we are not calling sendResponse for this action.
      // The background script doesn't expect a response for 'showToxicityResult'.
    }
  
    // If the message action wasn't handled above, the listener implicitly returns undefined,
    // indicating no response is forthcoming.
  });
  
  
  // Function to create and display the notification on the page
  function displayResultOnPage(message, isError) {
    // Remove any existing notification div to prevent duplicates
    const existingDiv = document.getElementById('toxicity-analyzer-result-div');
    if (existingDiv) {
        existingDiv.remove();
    }
  
    // Create the main notification container
    const notificationDiv = document.createElement('div');
    notificationDiv.id = 'toxicity-analyzer-result-div'; // Assign an ID for potential removal
  
    // Set content and apply base styles using cssText for brevity
    notificationDiv.textContent = message; // Use textContent to prevent potential XSS if message content was unsafe
    notificationDiv.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 15px 30px 15px 20px; /* Extra padding on right for close button */
      z-index: 2147483647; /* Max z-index often used by extensions */
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif; /* Use system fonts */
      font-size: 14px;
      max-width: 320px;
      white-space: pre-line; /* Respect newlines in the message */
      transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out; /* Add transform transition */
      opacity: 0; /* Start hidden */
      transform: translateX(20px); /* Start slightly off-screen */
      line-height: 1.4;
    `;
  
    // Apply styles based on whether it's an error or success message
    if (isError) {
      notificationDiv.style.background = "#fee2e2"; // Lighter red background
      notificationDiv.style.color = "#991b1b";      // Darker red text
      notificationDiv.style.border = "1px solid #fca5a5"; // Medium red border
    } else {
      notificationDiv.style.background = "#f0f9ff"; // Lighter blue background
      notificationDiv.style.color = "#0c4a6e";      // Darker blue text
      notificationDiv.style.border = "1px solid #7dd3fc"; // Medium blue border
    }
  
    // --- Add Close Button ---
    const closeButton = document.createElement('button');
    closeButton.textContent = '×'; // Use the multiplication sign '×' for close
    closeButton.setAttribute('aria-label', 'Close Notification'); // Accessibility
    closeButton.style.cssText = `
      position: absolute;
      top: 4px;
      right: 6px;
      background: none;
      border: none;
      font-size: 20px; /* Larger size for easier clicking */
      line-height: 1;
      padding: 2px 4px;
      cursor: pointer;
      color: inherit; /* Inherit color from parent */
      opacity: 0.6;
      transition: opacity 0.2s ease;
    `;
    // Make close button slightly more visible on hover
    closeButton.onmouseover = () => { closeButton.style.opacity = '1'; };
    closeButton.onmouseout = () => { closeButton.style.opacity = '0.6'; };
  
    // Add click listener to remove the notification
    closeButton.addEventListener('click', (e) => {
      e.stopPropagation(); // Prevent potential event bubbling
      notificationDiv.style.opacity = '0';
      notificationDiv.style.transform = 'translateX(20px)';
      // Remove from DOM after fade-out transition
      setTimeout(() => {
          if (document.body.contains(notificationDiv)) { // Check if it still exists
              notificationDiv.remove();
          }
      }, 300); // Match transition duration
    });
  
    // Append close button and notification div to the page
    notificationDiv.appendChild(closeButton);
    document.body.appendChild(notificationDiv);
  
    // --- Animate In and Schedule Auto-Removal ---
    // Animate-in slightly after appending
    setTimeout(() => {
      notificationDiv.style.opacity = '1';
      notificationDiv.style.transform = 'translateX(0)';
    }, 10); // Small delay to allow initial styles to apply
  
    // Set timer to automatically remove the notification after a delay
    const autoRemoveDelay = isError ? 10000 : 7000; // Show errors slightly longer
    setTimeout(() => {
      // Check if the element still exists in the DOM (user might have closed it)
      if (document.body.contains(notificationDiv)) {
        // Trigger fade-out animation
        notificationDiv.style.opacity = '0';
        notificationDiv.style.transform = 'translateX(20px)';
        // Remove from DOM after fade-out transition
        setTimeout(() => {
             if (document.body.contains(notificationDiv)) {
                notificationDiv.remove();
             }
         }, 300); // Match transition duration
      }
    }, autoRemoveDelay);
  }
  
  
  // Log to confirm the script loaded (useful for debugging injection issues)
  console.log("Content script: Toxicity Analyzer content script loaded and listener attached.");