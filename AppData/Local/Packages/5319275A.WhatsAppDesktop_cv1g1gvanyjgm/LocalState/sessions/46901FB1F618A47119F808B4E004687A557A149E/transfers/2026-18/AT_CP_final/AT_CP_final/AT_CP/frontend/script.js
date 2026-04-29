/**
 * Main Application Controller - DFA Simulator
 * ============================================
 * This file handles:
 * - User input management
 * - Dynamic state and transition table generation
 * - API communication with Flask backend
 * - DFA construction from UI inputs
 * - Mode switching (Custom, Starts, Ends, Substring)
 */

// Global state to store the current DFA
let currentDFA = {
    states: [],
    alphabet: [],
    initial: null,
    finals: [],
    transitions: {}
};

// Simulation state
let simulationData = {
    path: [],
    currentIndex: 0,
    isRunning: false
};

// API base URL - change this if your Flask server runs on different host/port
const API_BASE = 'http://localhost:5000/api';

/**
 * Initialize the application when the page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('DFA Simulator initialized');
    
    // Set up mode buttons
    setupModeButtons();
    
    // Generate initial states
    generateStates();
});

/**
 * Sets up click handlers for mode selection buttons
 */
function setupModeButtons() {
    const modeButtons = document.querySelectorAll('.mode-btn');
    
    modeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            modeButtons.forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Get the mode
            const mode = this.dataset.mode;
            
            // Show/hide pattern input section
            const patternSection = document.getElementById('pattern-input-section');
            if (mode === 'custom') {
                patternSection.classList.add('hidden');
            } else {
                patternSection.classList.remove('hidden');
                
                // Show dead state info only for "starts" mode
                const deadStateInfo = document.getElementById('dead-state-info');
                if (mode === 'starts') {
                    deadStateInfo.style.display = 'block';
                } else {
                    deadStateInfo.style.display = 'none';
                }
            }
        });
    });
}

/**
 * Dead State Configuration
 * Constant representing the dead/trap state name
 */
const DEAD_STATE = 'qd';

/**
 * Generates state names based on the number input
 * Creates default names: q0, q1, q2, ..., q(n-1) + dead state (qd)
 */
function generateStates() {
    const numStatesInput = document.getElementById('num-states');
    const numStates = parseInt(numStatesInput.value);
    
    if (isNaN(numStates) || numStates < 1 || numStates > 20) {
        alert('Please enter a valid number of states (1-20)');
        return;
    }
    
    // Clear current states
    currentDFA.states = [];
    currentDFA.transitions = {};
    
    // Generate state names
    for (let i = 0; i < numStates; i++) {
        currentDFA.states.push(`q${i}`);
    }
    
    // Add dead state if not already present
    if (!currentDFA.states.includes(DEAD_STATE)) {
        currentDFA.states.push(DEAD_STATE);
    }
    
    // Set initial state to q0
    currentDFA.initial = currentDFA.states[0];
    
    // Clear finals (dead state is NOT a final state)
    currentDFA.finals = [];
    
    // Initialize transitions for all states including dead state
    currentDFA.states.forEach(state => {
        currentDFA.transitions[state] = {};
    });
    
    // If alphabet exists, auto-populate dead state transitions (loop to itself)
    if (currentDFA.alphabet && currentDFA.alphabet.length > 0) {
        initializeDeadStateTransitions();
    }
    
    // Update UI
    updateStateNamesUI();
    updateInitialStateSelect();
    updateFinalStatesCheckboxes();
    updateTransitionTable();
    updateFullTransitionTable();
    updateDFATuple();
}

/**
 * Updates the alphabet based on user input
 * Parses comma-separated symbols
 */
function updateAlphabet() {
    const alphabetInput = document.getElementById('alphabet-input');
    const alphabetStr = alphabetInput.value.trim();
    
    if (!alphabetStr) {
        alert('Please enter at least one alphabet symbol');
        return;
    }
    
    // Parse comma-separated symbols
    const symbols = alphabetStr.split(',').map(s => s.trim()).filter(s => s.length > 0);
    
    // Remove duplicates
    currentDFA.alphabet = [...new Set(symbols)];
    
    // Reset transitions for new alphabet
    currentDFA.states.forEach(state => {
        currentDFA.transitions[state] = {};
    });
    
    // Initialize dead state transitions (loop to itself for all symbols)
    initializeDeadStateTransitions();
    
    // Update UI
    updateTransitionTable();
    updateFullTransitionTable();
    updateDFATuple();
}

/**
 * Initializes dead state transitions
 * Dead state loops to itself for all input symbols
 */
function initializeDeadStateTransitions() {
    if (!currentDFA.alphabet || currentDFA.alphabet.length === 0) {
        return;
    }
    
    // Ensure dead state exists in transitions
    if (!currentDFA.transitions[DEAD_STATE]) {
        currentDFA.transitions[DEAD_STATE] = {};
    }
    
    // Set all transitions from dead state to dead state (trap behavior)
    currentDFA.alphabet.forEach(symbol => {
        currentDFA.transitions[DEAD_STATE][symbol] = DEAD_STATE;
    });
}

/**
 * Fills undefined transitions with dead state
 * Ensures complete DFA: every (state, symbol) pair has a transition
 */
function fillUndefinedTransitions() {
    currentDFA.states.forEach(state => {
        // Skip dead state itself
        if (state === DEAD_STATE) return;
        
        // Ensure transitions object exists
        if (!currentDFA.transitions[state]) {
            currentDFA.transitions[state] = {};
        }
        
        // Fill missing transitions with dead state
        currentDFA.alphabet.forEach(symbol => {
            if (!currentDFA.transitions[state][symbol]) {
                currentDFA.transitions[state][symbol] = DEAD_STATE;
            }
        });
    });
}

/**
 * Updates the state names input fields
 */
function updateStateNamesUI() {
    const container = document.getElementById('state-names-container');
    container.innerHTML = '';
    
    currentDFA.states.forEach((state, index) => {
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'state-name-input';
        input.value = state;
        input.dataset.index = index;
        
        // Prevent renaming of dead state
        if (state === DEAD_STATE) {
            input.disabled = true;
            input.style.backgroundColor = '#fee2e2';
            input.style.color = '#ef4444';
            input.style.fontWeight = 'bold';
            input.title = 'Dead state cannot be renamed';
        }
        
        // Update state name on change
        input.addEventListener('change', function() {
            const newName = this.value.trim();
            if (newName) {
                const oldName = currentDFA.states[index];
                
                // Prevent renaming to dead state name
                if (newName === DEAD_STATE) {
                    alert('Cannot rename state to "qd" (dead state). Please use a different name.');
                    this.value = oldName;
                    return;
                }
                
                currentDFA.states[index] = newName;
                
                // Update transitions
                if (currentDFA.transitions[oldName]) {
                    currentDFA.transitions[newName] = currentDFA.transitions[oldName];
                    delete currentDFA.transitions[oldName];
                }
                
                // Update references in other transitions
                currentDFA.states.forEach(state => {
                    currentDFA.alphabet.forEach(symbol => {
                        if (currentDFA.transitions[state][symbol] === oldName) {
                            currentDFA.transitions[state][symbol] = newName;
                        }
                    });
                });
                
                // Update UI
                updateInitialStateSelect();
                updateFinalStatesCheckboxes();
                updateTransitionTable();
                updateFullTransitionTable();
                updateDFATuple();
            }
        });
        
        container.appendChild(input);
    });
}

/**
 * Updates the initial state dropdown
 */
function updateInitialStateSelect() {
    const select = document.getElementById('initial-state-select');
    select.innerHTML = '';
    
    currentDFA.states.forEach(state => {
        const option = document.createElement('option');
        option.value = state;
        option.textContent = state;
        
        if (state === currentDFA.initial) {
            option.selected = true;
        }
        
        select.appendChild(option);
    });
    
    // Update on change
    select.onchange = function() {
        currentDFA.initial = this.value;
        updateDFATuple();
        renderDFA(currentDFA);
        updateFullTransitionTable();
    };
}

/**
 * Updates the final states checkboxes
 * Dead state is excluded from final states
 */
function updateFinalStatesCheckboxes() {
    const container = document.getElementById('final-states-container');
    container.innerHTML = '';
    
    currentDFA.states.forEach(state => {
        // Skip dead state - it cannot be a final state
        if (state === DEAD_STATE) {
            return;
        }
        
        const div = document.createElement('div');
        div.className = 'checkbox-item';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `final-${state}`;
        checkbox.value = state;
        
        if (currentDFA.finals.includes(state)) {
            checkbox.checked = true;
        }
        
        const label = document.createElement('label');
        label.htmlFor = `final-${state}`;
        label.textContent = state;
        
        // Update on change
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                if (!currentDFA.finals.includes(state)) {
                    currentDFA.finals.push(state);
                }
            } else {
                currentDFA.finals = currentDFA.finals.filter(s => s !== state);
            }
            updateDFATuple();
            renderDFA(currentDFA);
            updateFullTransitionTable();
        });
        
        div.appendChild(checkbox);
        div.appendChild(label);
        container.appendChild(div);
    });
}

/**
 * Updates the transition table in the input panel
 */
function updateTransitionTable() {
    const container = document.getElementById('transition-table-container');
    container.innerHTML = '';
    
    if (currentDFA.states.length === 0 || currentDFA.alphabet.length === 0) {
        container.innerHTML = '<p style="color: #6b7280; text-align: center;">Generate states and update alphabet to see transition table</p>';
        return;
    }
    
    const table = document.createElement('table');
    table.className = 'mini-transition-table';
    
    // Header row
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    const thState = document.createElement('th');
    thState.textContent = 'State';
    headerRow.appendChild(thState);
    
    currentDFA.alphabet.forEach(symbol => {
        const th = document.createElement('th');
        th.textContent = symbol;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Body rows
    const tbody = document.createElement('tbody');
    currentDFA.states.forEach(state => {
        const row = document.createElement('tr');
        
        // Check if this is a dead/reject state
        const isDeadState = state === DEAD_STATE || state === 'q_reject' || state.toLowerCase().includes('reject') || state.toLowerCase().includes('dead');
        
        // State name cell
        const tdState = document.createElement('td');
        tdState.textContent = state;
        
        // Style dead state row
        if (isDeadState) {
            tdState.style.color = '#ef4444';
            tdState.style.fontWeight = 'bold';
            row.style.backgroundColor = '#fef2f2';
        }
        
        row.appendChild(tdState);
        
        // Transition cells
        currentDFA.alphabet.forEach(symbol => {
            const td = document.createElement('td');
            
            const select = document.createElement('select');
            select.dataset.state = state;
            select.dataset.symbol = symbol;
            
            // Add option for each state
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = '-';
            select.appendChild(defaultOption);
            
            currentDFA.states.forEach(targetState => {
                const option = document.createElement('option');
                option.value = targetState;
                option.textContent = targetState;
                
                // Set current value if exists
                if (currentDFA.transitions[state] && currentDFA.transitions[state][symbol] === targetState) {
                    option.selected = true;
                }
                
                select.appendChild(option);
            });
            
            // Update transition on change
            select.addEventListener('change', function() {
                const targetState = this.value;
                if (targetState) {
                    if (!currentDFA.transitions[state]) {
                        currentDFA.transitions[state] = {};
                    }
                    currentDFA.transitions[state][symbol] = targetState;
                    
                    // Ensure dead state transitions remain intact
                    if (state !== DEAD_STATE) {
                        initializeDeadStateTransitions();
                    }
                    
                    updateFullTransitionTable();
                    updateDFATuple();
                }
            });
            
            td.appendChild(select);
            row.appendChild(td);
        });
        
        tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    container.appendChild(table);
}

/**
 * Updates the full transition table at the bottom
 */
function updateFullTransitionTable() {
    const container = document.getElementById('full-transition-table');
    container.innerHTML = '';
    
    if (currentDFA.states.length === 0 || currentDFA.alphabet.length === 0) {
        container.innerHTML = '<p style="color: #6b7280; text-align: center; padding: 20px;">No transitions to display</p>';
        return;
    }
    
    const table = document.createElement('table');
    table.className = 'full-transition-table';
    
    // Header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    const thState = document.createElement('th');
    thState.textContent = 'State';
    headerRow.appendChild(thState);
    
    currentDFA.alphabet.forEach(symbol => {
        const th = document.createElement('th');
        th.textContent = symbol;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Body
    const tbody = document.createElement('tbody');
    currentDFA.states.forEach(state => {
        const row = document.createElement('tr');
        
        // Check if this is a dead/reject state
        const isDeadState = state === DEAD_STATE || state === 'q_reject' || state.toLowerCase().includes('reject') || state.toLowerCase().includes('dead');
        
        const tdState = document.createElement('td');
        let stateText = state;
        if (state === currentDFA.initial) stateText += ' ▶';
        if (currentDFA.finals.includes(state)) stateText += ' ✓';
        if (isDeadState) stateText += ' (Dead State)';
        tdState.textContent = stateText;
        
        // Style dead state differently
        if (isDeadState) {
            tdState.style.color = '#ef4444';
            tdState.style.fontWeight = 'bold';
        }
        
        row.appendChild(tdState);
        
        currentDFA.alphabet.forEach(symbol => {
            const td = document.createElement('td');
            const target = currentDFA.transitions[state] && currentDFA.transitions[state][symbol];
            td.textContent = target || '-';
            td.style.color = target ? '#10b981' : '#6b7280';
            
            // Highlight dead state transitions
            if (isDeadState && target === state) {
                td.style.color = '#ef4444';
                td.style.fontWeight = 'bold';
            }
            
            row.appendChild(td);
        });
        
        tbody.appendChild(row);
    });
    
    table.appendChild(tbody);
    container.appendChild(table);
}

/**
 * Updates the DFA 5-tuple display
 */
function updateDFATuple() {
    const container = document.getElementById('dfa-tuple-content');
    
    if (currentDFA.states.length === 0) {
        container.innerHTML = '<p>Enter states and alphabet to see the DFA tuple</p>';
        return;
    }
    
    const statesStr = `{${currentDFA.states.join(', ')}}`;
    const alphabetStr = `{${currentDFA.alphabet.join(', ')}}`;
    const initialStr = currentDFA.initial || '-';
    const finalsStr = `{${currentDFA.finals.join(', ')}}`;
    
    container.innerHTML = `
        <div><strong>M = (Q, Σ, δ, q0, F)</strong></div>
        <div><strong>Q</strong> = ${statesStr}</div>
        <div><strong>Σ</strong> = ${alphabetStr}</div>
        <div><strong>q0</strong> = ${initialStr}</div>
        <div><strong>F</strong> = ${finalsStr}</div>
        <div><strong>|Q|</strong> = ${currentDFA.states.length} states</div>
        <div><strong>|Σ|</strong> = ${currentDFA.alphabet.length} symbols</div>
    `;
}

/**
 * Validates the current DFA by sending it to the backend
 */
async function validateCurrentDFA() {
    if (currentDFA.states.length === 0) {
        alert('Please generate states first');
        return;
    }
    
    // Fill any undefined transitions with dead state before validation
    fillUndefinedTransitions();
    initializeDeadStateTransitions();
    
    // Update UI to reflect filled transitions
    updateTransitionTable();
    updateFullTransitionTable();
    
    try {
        const response = await fetch(`${API_BASE}/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentDFA)
        });
        
        const result = await response.json();
        
        if (result.valid) {
            alert('✅ DFA is valid! You can now simulate it.');
            renderDFA(currentDFA);
        } else {
            const errorMsg = '❌ Invalid DFA:\n' + result.errors.join('\n');
            alert(errorMsg);
        }
    } catch (error) {
        console.error('Validation error:', error);
        alert('Error connecting to backend server. Make sure Flask is running.');
    }
}

/**
 * Starts simulation of the current DFA with the input string
 */
async function startSimulation() {
    const inputString = document.getElementById('input-string').value;
    
    if (currentDFA.states.length === 0) {
        alert('Please create a DFA first');
        return;
    }
    
    if (!inputString) {
        alert('Please enter an input string');
        return;
    }
    
    // Fill any undefined transitions with dead state before simulation
    fillUndefinedTransitions();
    initializeDeadStateTransitions();
    
    // Update UI to reflect filled transitions
    updateTransitionTable();
    updateFullTransitionTable();
    
    try {
        // Send simulation request to backend
        const response = await fetch(`${API_BASE}/simulate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                dfa: currentDFA,
                input_string: inputString
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert('Error: ' + result.error);
            return;
        }
        
        // Store simulation data
        simulationData.path = result.path;
        simulationData.currentIndex = 0;
        simulationData.isRunning = false;
        
        // Enable animation controls
        document.getElementById('btn-play').disabled = false;
        document.getElementById('btn-step').disabled = false;
        document.getElementById('btn-reset').disabled = false;
        
        // Render the DFA
        renderDFA(currentDFA);
        
        // Show path
        displayPath(result.path, inputString);
        
        // Start animation automatically
        playAnimation();
        
    } catch (error) {
        console.error('Simulation error:', error);
        alert('Error connecting to backend server. Make sure Flask is running.');
    }
}

/**
 * Displays the transition path
 */
function displayPath(path, inputString) {
    const pathDisplay = document.getElementById('path-display');
    const pathContent = document.getElementById('path-content');
    
    pathDisplay.style.display = 'block';
    
    let pathStr = path.join(' → ');
    pathContent.textContent = `Path: ${pathStr}`;
}

/**
 * Handles pattern-based DFA generation
 */
async function handlePatternGeneration() {
    const activeBtn = document.querySelector('.mode-btn.active');
    if (!activeBtn) {
        alert('Please select a mode');
        return;
    }
    
    const mode = activeBtn.dataset.mode;
    
    if (mode === 'custom') {
        alert('Custom mode - please build your DFA manually');
        return;
    }
    
    const patternInput = document.getElementById('pattern-input');
    const pattern = patternInput.value.trim();
    
    if (!pattern) {
        alert('Please enter a pattern');
        return;
    }
    
    // Get alphabet
    const alphabetInput = document.getElementById('alphabet-input');
    const alphabetStr = alphabetInput.value.trim();
    
    if (!alphabetStr) {
        alert('Please enter an alphabet');
        return;
    }
    
    const alphabet = alphabetStr.split(',').map(s => s.trim()).filter(s => s.length > 0);
    
    try {
        // Request DFA generation from backend
        const response = await fetch(`${API_BASE}/generate-dfa`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mode: mode,
                pattern: pattern,
                alphabet: alphabet
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert('Error: ' + result.error);
            return;
        }
        
        // Update current DFA
        currentDFA = result.dfa;
        
        // Ensure dead state is present (for "starts" mode, backend uses q_reject)
        // Map q_reject to qd for consistency, or add qd if missing
        const hasDeadState = currentDFA.states.some(s => 
            s === DEAD_STATE || 
            s === 'q_reject' || 
            s.toLowerCase().includes('reject') || 
            s.toLowerCase().includes('dead')
        );
        
        if (!hasDeadState && mode === 'custom') {
            // For custom mode, add dead state if not present
            if (!currentDFA.states.includes(DEAD_STATE)) {
                currentDFA.states.push(DEAD_STATE);
            }
            initializeDeadStateTransitions();
        } else if (mode === 'starts') {
            // For starts mode, backend creates q_reject, ensure it's properly set up
            const rejectState = currentDFA.states.find(s => 
                s === 'q_reject' || s.toLowerCase().includes('reject')
            );
            if (rejectState) {
                // Ensure q_reject transitions are complete
                initializeDeadStateTransitions();
            }
        }
        
        // Update UI
        document.getElementById('num-states').value = currentDFA.states.length;
        updateStateNamesUI();
        updateInitialStateSelect();
        updateFinalStatesCheckboxes();
        updateTransitionTable();
        updateFullTransitionTable();
        updateDFATuple();
        
        // Render the DFA
        renderDFA(currentDFA);
        
        // Show success message
        const modeNames = {
            'starts': 'starts with',
            'ends': 'ends with',
            'substring': 'contains substring'
        };
        
        alert(`✅ DFA generated for strings ${modeNames[mode]} "${pattern}"`);
        
    } catch (error) {
        console.error('Generation error:', error);
        alert('Error connecting to backend server. Make sure Flask is running.');
    }
}

/**
 * Resets the simulation
 */
function resetSimulation() {
    resetAnimation();
    
    document.getElementById('input-string').value = '';
    document.getElementById('path-display').style.display = 'none';
    document.getElementById('result-display').className = 'result-display';
    document.getElementById('result-display').textContent = '';
    
    simulationData = {
        path: [],
        currentIndex: 0,
        isRunning: false
    };
    
    renderDFA(currentDFA);
}
