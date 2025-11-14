/**
 * Island Browser Trust Shim
 *
 * Simulates Island's browser trust signal by sending telemetry to the backend
 * In production, this would be Island's actual browser extension/agent
 */

(function() {
    'use strict';

    // Generate a session ID
    const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);

    // Collect trust signals
    function collectTrustSignals() {
        return {
            url: window.location.href,
            timestamp: new Date().toISOString(),
            session_id: sessionId,
            user_agent: navigator.userAgent,
            // Simulated Island signals
            sso_verified: true,
            dlp_enabled: true,
            secure_context: window.isSecureContext,
            threat_level: 'low'
        };
    }

    // Send signal to backend
    function sendTrustSignal() {
        const signal = collectTrustSignals();

        fetch('/island/signal', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(signal)
        })
        .then(response => response.json())
        .then(data => {
            console.log('[Island Shim] Trust signal sent:', data);
        })
        .catch(error => {
            console.error('[Island Shim] Failed to send trust signal:', error);
        });
    }

    // Send signal on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', sendTrustSignal);
    } else {
        sendTrustSignal();
    }

    // Send periodic heartbeat (every 60 seconds)
    setInterval(sendTrustSignal, 60000);

    console.log('[Island Shim] Initialized with session:', sessionId);
})();
