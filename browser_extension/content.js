/**
 * OmniGuard Content Script
 * Injects a warning overlay directly into the DOM if the background script detects phishing.
 */

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "SHOW_WARNING") {
        const overlay = document.createElement("div");
        overlay.id = "omniguard-warning-overlay";
        overlay.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(255, 0, 0, 0.9); color: white; z-index: 999999; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: sans-serif;">
                <h1 style="font-size: 48px; margin-bottom: 20px;">🚨 OMNIGUARD WARNING 🚨</h1>
                <p style="font-size: 24px;">This website has been flagged as a phishing attempt.</p>
                <p>Proceeding is highly discouraged.</p>
            </div>
        `;
        document.body.appendChild(overlay);
        
        // Stop the page from loading further
        window.stop(); 
    }
});