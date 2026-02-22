/**
 * OmniGuard Background Service Worker
 * Intercepts navigation events and communicates with the FastAPI backend.
 */

const API_ENDPOINT = "http://127.0.0.1:8000/api/v1/analyze";

chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
    // Ignore internal chrome URLs and sub-frame navigations
    if (details.frameId !== 0 || details.url.startsWith("chrome://")) return;

    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: details.url })
        });

        const result = await response.json();

        if (result.is_phishing) {
            console.warn(`[OmniGuard] Threat detected on: ${details.url}`);
            // TODO: Inject content script to display a full-page red warning overlay
        }
    } catch (error) {
        console.error("[OmniGuard] Inference API unreachable:", error);
    }
});