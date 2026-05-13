document.addEventListener('DOMContentLoaded', () => {
    // POC: Connecting UI to LangGraph Backend logic simulation
    const startInvestingBtn = document.getElementById('hero-cta-1');
    
    startInvestingBtn.addEventListener('click', async () => {
        // Change button state to loading
        const originalText = startInvestingBtn.innerText;
        startInvestingBtn.innerText = "Analyzing Client 360...";
        startInvestingBtn.style.opacity = "0.7";
        startInvestingBtn.disabled = true;

        try {
            // Mock API call to our FastAPI/LangGraph backend
            // In a real scenario, this would be: fetch('http://localhost:8000/api/chat', ...)
            console.log("Triggering Master Orchestrator...");
            
            // Simulating API delay and agent reasoning...
            await new Promise(resolve => setTimeout(resolve, 1500));
            startInvestingBtn.innerText = "Detecting Outside Assets...";
            
            await new Promise(resolve => setTimeout(resolve, 1500));
            startInvestingBtn.innerText = "Running Compliance Guardrails...";

            await new Promise(resolve => setTimeout(resolve, 1500));
            
            // Reset button and show mock result
            startInvestingBtn.innerText = originalText;
            startInvestingBtn.style.opacity = "1";
            startInvestingBtn.disabled = false;

            alert("LangGraph Pipeline Executed!\n\n1. Supervisor Agent routed request.\n2. Outside Asset Detector found $325,000 at Fidelity/Schwab.\n3. Compliance Check passed.\n\nReady for Advisor Review.");
            
        } catch (error) {
            console.error("Error connecting to Agentic AI Layer:", error);
            startInvestingBtn.innerText = "Error (See Console)";
        }
    });

    // Add subtle hover effects to cards using vanilla JS
    const cards = document.querySelectorAll('.feature-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.boxShadow = '0 0 20px rgba(139, 92, 246, 0.2)';
        });
        card.addEventListener('mouseleave', () => {
            card.style.boxShadow = 'none';
        });
    });
});
