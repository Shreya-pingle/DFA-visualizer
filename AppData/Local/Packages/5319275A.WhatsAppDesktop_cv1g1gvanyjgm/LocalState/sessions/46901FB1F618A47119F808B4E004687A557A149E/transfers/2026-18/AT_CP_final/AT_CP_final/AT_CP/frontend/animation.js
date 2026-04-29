/**
 * Animation Controller - Step-by-Step DFA Animation
 * ==================================================
 * This module manages the animation of DFA simulation:
 * - Play/Pause/Step/Reset controls
 * - Speed control
 * - State and edge highlighting during animation
 * - Progress tracking
 * - Result display (Accepted/Rejected)
 */

// Animation state
let animationState = {
    path: [],              // Path of states visited
    inputString: '',       // Input string being processed
    currentIndex: 0,       // Current position in input string
    isPlaying: false,      // Whether animation is running
    isPaused: false,       // Whether animation is paused
    speed: 1000,           // Delay between steps in milliseconds
    timer: null            // Timeout timer
};

/**
 * Starts the animation (Play button)
 * Called after simulation request to backend
 */
function playAnimation() {
    if (simulationData.path.length === 0) {
        alert('Please start a simulation first');
        return;
    }
    
    if (animationState.isPlaying && !animationState.isPaused) {
        return; // Already playing
    }
    
    if (!animationState.isPaused) {
        // Fresh start
        animationState.path = simulationData.path;
        animationState.inputString = document.getElementById('input-string').value;
        animationState.currentIndex = 0;
    }
    
    animationState.isPlaying = true;
    animationState.isPaused = false;
    
    // Disable play, enable pause
    document.getElementById('btn-play').disabled = true;
    document.getElementById('btn-pause').disabled = false;
    
    // Start animating
    animateStep();
}

/**
 * Executes one step of the animation
 */
function animateStep() {
    if (!animationState.isPlaying || animationState.isPaused) {
        return;
    }
    
    // Check if we've reached the end of the path
    if (animationState.currentIndex >= animationState.path.length - 1) {
        // Animation complete
        stopAnimation();
        
        // Determine if accepted or rejected
        const finalState = animationState.path[animationState.path.length - 1];
        const accepted = currentDFA.finals.includes(finalState);
        
        showResult(accepted);
        return;
    }
    
    // Get current and next state
    const currentState = animationState.path[animationState.currentIndex];
    const nextState = animationState.path[animationState.currentIndex + 1];
    
    // Get the input symbol being processed
    const symbol = animationState.inputString[animationState.currentIndex];
    
    // Highlight the current state
    highlightState(currentState);
    
    // Highlight the transition edge
    highlightEdge(currentState, nextState);
    
    // Update displays
    updateAnimationDisplay(currentState, animationState.currentIndex);
    
    // Highlight current row in transition table
    highlightTransitionTableRow(currentState);
    
    // Move to next step
    animationState.currentIndex++;
    
    // Schedule next step
    animationState.timer = setTimeout(animateStep, animationState.speed);
}

/**
 * Pauses the animation (Pause button)
 */
function pauseAnimation() {
    if (!animationState.isPlaying) {
        return;
    }
    
    animationState.isPaused = !animationState.isPaused;
    
    if (animationState.isPaused) {
        // Pause the animation
        if (animationState.timer) {
            clearTimeout(animationState.timer);
            animationState.timer = null;
        }
        
        // Update button states
        document.getElementById('btn-play').disabled = false;
        document.getElementById('btn-pause').textContent = '▶️ Resume';
    } else {
        // Resume the animation
        document.getElementById('btn-play').disabled = true;
        document.getElementById('btn-pause').textContent = '⏸️ Pause';
        
        // Continue animating
        animateStep();
    }
}

/**
 * Steps forward one character (Step button)
 */
function stepAnimation() {
    if (simulationData.path.length === 0) {
        alert('Please start a simulation first');
        return;
    }
    
    // If not already running, initialize
    if (!animationState.isPlaying) {
        animationState.path = simulationData.path;
        animationState.inputString = document.getElementById('input-string').value;
        animationState.currentIndex = 0;
        animationState.isPlaying = true;
        animationState.isPaused = true;
        
        document.getElementById('btn-pause').disabled = false;
        document.getElementById('btn-reset').disabled = false;
    }
    
    // If we're at the end, show result
    if (animationState.currentIndex >= animationState.path.length - 1) {
        const finalState = animationState.path[animationState.path.length - 1];
        const accepted = currentDFA.finals.includes(finalState);
        
        showResult(accepted);
        return;
    }
    
    // Execute one step manually
    const currentState = animationState.path[animationState.currentIndex];
    const nextState = animationState.path[animationState.currentIndex + 1];
    
    // Highlight current state
    highlightState(currentState);
    highlightEdge(currentState, nextState);
    
    // Update displays
    updateAnimationDisplay(currentState, animationState.currentIndex);
    highlightTransitionTableRow(currentState);
    
    // Move to next step
    animationState.currentIndex++;
    
    // If we've reached the end, show result
    if (animationState.currentIndex >= animationState.path.length - 1) {
        const finalState = animationState.path[animationState.path.length - 1];
        highlightState(finalState);
        
        setTimeout(() => {
            const accepted = currentDFA.finals.includes(finalState);
            showResult(accepted);
        }, 300);
    }
}

/**
 * Resets the animation (Reset button)
 */
function resetAnimation() {
    stopAnimation();
    
    animationState.path = [];
    animationState.inputString = '';
    animationState.currentIndex = 0;
    animationState.isPlaying = false;
    animationState.isPaused = false;
    
    // Clear highlights
    clearHighlights();
    
    // Reset displays
    document.getElementById('current-state-display').textContent = '-';
    document.getElementById('progress-display').textContent = '0 / 0';
    document.getElementById('result-display').className = 'result-display';
    document.getElementById('result-display').textContent = '';
    
    // Reset buttons
    document.getElementById('btn-play').disabled = true;
    document.getElementById('btn-pause').disabled = true;
    document.getElementById('btn-pause').textContent = '⏸️ Pause';
    document.getElementById('btn-step').disabled = true;
    document.getElementById('btn-reset').disabled = true;
    
    // Clear transition table highlight
    highlightTransitionTableRow(null);
    
    // Re-render DFA
    renderDFA(currentDFA);
}

/**
 * Stops the animation timer
 */
function stopAnimation() {
    if (animationState.timer) {
        clearTimeout(animationState.timer);
        animationState.timer = null;
    }
    
    animationState.isPlaying = false;
    animationState.isPaused = false;
}

/**
 * Updates the animation display (current state and progress)
 * @param {string} currentState - Current state name
 * @param {number} index - Current index in input string
 */
function updateAnimationDisplay(currentState, index) {
    document.getElementById('current-state-display').textContent = currentState;
    document.getElementById('progress-display').textContent = 
        `${index} / ${animationState.inputString.length}`;
}

/**
 * Highlights the current state row in the transition table
 * @param {string} stateName - State name to highlight (null to clear)
 */
function highlightTransitionTableRow(stateName) {
    const rows = document.querySelectorAll('.full-transition-table tbody tr');
    
    rows.forEach(row => {
        const firstCell = row.cells[0];
        if (firstCell) {
            const cellText = firstCell.textContent;
            if (stateName && cellText.startsWith(stateName)) {
                row.classList.add('current-state');
            } else {
                row.classList.remove('current-state');
            }
        }
    });
}

/**
 * Shows the final result (Accepted or Rejected)
 * @param {boolean} accepted - Whether the string was accepted
 */
function showResult(accepted) {
    const resultDisplay = document.getElementById('result-display');
    
    if (accepted) {
        resultDisplay.className = 'result-display accept';
        resultDisplay.textContent = '✅ ACCEPTED - String is valid!';
    } else {
        resultDisplay.className = 'result-display reject';
        resultDisplay.textContent = '❌ REJECTED - String is invalid!';
    }
    
    // Update button states
    document.getElementById('btn-play').disabled = true;
    document.getElementById('btn-pause').disabled = true;
    document.getElementById('btn-step').disabled = true;
    
    // Clear highlights after a delay
    setTimeout(() => {
        clearHighlights();
        highlightTransitionTableRow(null);
    }, 2000);
}

/**
 * Updates the animation speed
 */
function updateSpeed() {
    const slider = document.getElementById('speed-slider');
    const speedValue = parseFloat(slider.value);
    
    // Convert speed multiplier to delay (milliseconds)
    // 1x = 1000ms, 2x = 500ms, 0.5x = 2000ms
    animationState.speed = 1000 / speedValue;
    
    document.getElementById('speed-value').textContent = speedValue.toFixed(1) + 'x';
}

/**
 * Keyboard shortcuts for animation control
 */
document.addEventListener('keydown', function(e) {
    // Don't trigger if user is typing in an input field
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {
        return;
    }
    
    switch(e.code) {
        case 'Space':
            e.preventDefault();
            if (animationState.isPlaying && !animationState.isPaused) {
                pauseAnimation();
            } else if (animationState.isPlaying && animationState.isPaused) {
                pauseAnimation();
            } else if (simulationData.path.length > 0) {
                playAnimation();
            }
            break;
            
        case 'ArrowRight':
            e.preventDefault();
            stepAnimation();
            break;
            
        case 'KeyR':
            e.preventDefault();
            resetAnimation();
            break;
            
        case 'KeyS':
            e.preventDefault();
            startSimulation();
            break;
    }
});
