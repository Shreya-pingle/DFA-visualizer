/**
 * Graph Rendering Engine - SVG-based DFA Visualization
 * =====================================================
 * This module handles all SVG rendering for the DFA diagram:
 * - Circular layout calculation for state positioning
 * - Drawing states (circles, double circles for accept states)
 * - Drawing transitions (arrows with labels)
 * - Handling self-loops and bidirectional transitions
 * - Highlighting active states and edges during animation
 */

// Store state positions for animation highlighting
let statePositions = {};

/**
 * Renders the complete DFA diagram on the SVG canvas
 * @param {Object} dfa - The DFA structure
 */
function renderDFA(dfa) {
    const svgContent = document.getElementById('svg-content');
    svgContent.innerHTML = '';
    
    // Clear stored positions
    statePositions = {};
    
    if (dfa.states.length === 0) {
        const text = createSVGElement('text', {
            x: '50%',
            y: '50%',
            'text-anchor': 'middle',
            'fill': '#6b7280',
            'font-size': '20'
        }, 'Generate states to see the DFA diagram');
        svgContent.appendChild(text);
        return;
    }
    
    // Calculate positions using circular layout
    calculateCircularLayout(dfa.states);
    
    // Group transitions by (fromState, toState) pairs
    const groupedTransitions = groupTransitions(dfa.transitions);
    
    // Draw grouped transitions (so they appear behind states)
    for (let key in groupedTransitions) {
        const { fromState, toState, symbols } = groupedTransitions[key];
        drawGroupedTransition(svgContent, fromState, toState, symbols);
    }
    
    // Draw start arrow
    if (dfa.initial && statePositions[dfa.initial]) {
        drawStartArrow(svgContent, dfa.initial);
    }
    
    // Draw states
    dfa.states.forEach(state => {
        drawState(svgContent, state, dfa.finals.includes(state));
    });
}

/**
 * Groups transitions by (fromState, toState) pairs
 * Merges symbols that lead to the same state
 * @param {Object} transitions - DFA transition function
 * @returns {Object} - Grouped transitions with merged symbols
 */
function groupTransitions(transitions) {
    const grouped = {};
    
    for (let fromState in transitions) {
        for (let symbol in transitions[fromState]) {
            const toState = transitions[fromState][symbol];
            const key = `${fromState}->${toState}`;
            
            if (!grouped[key]) {
                grouped[key] = {
                    fromState: fromState,
                    toState: toState,
                    symbols: []
                };
            }
            
            // Add symbol if not already present
            if (!grouped[key].symbols.includes(symbol)) {
                grouped[key].symbols.push(symbol);
            }
        }
    }
    
    return grouped;
}

/**
 * Calculates circular layout positions for states
 * Positions states evenly around a circle
 * @param {Array} states - Array of state names
 */
function calculateCircularLayout(states) {
    const svg = document.getElementById('dfa-svg');
    const width = svg.clientWidth || 800;
    const height = svg.clientHeight || 500;
    
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.35;
    
    states.forEach((state, index) => {
        const angle = (2 * Math.PI * index) / states.length - Math.PI / 2;
        statePositions[state] = {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle)
        };
    });
}

/**
 * Draws a single state on the SVG canvas
 * @param {SVGElement} svgContent - The SVG group to draw into
 * @param {string} stateName - Name of the state
 * @param {boolean} isFinal - Whether this is a final/accept state
 */
function drawState(svgContent, stateName, isFinal) {
    const pos = statePositions[stateName];
    if (!pos) return;
    
    // Check if this is a dead/reject state (support both qd and q_reject)
    const isDeadState = stateName === 'qd' || stateName === 'q_reject' || 
                        stateName.toLowerCase().includes('reject') || 
                        stateName.toLowerCase().includes('dead');
    
    const group = createSVGElement('g', {});
    
    // For final states, draw double circle
    if (isFinal) {
        const outerCircle = createSVGElement('circle', {
            cx: pos.x,
            cy: pos.y,
            r: 42,
            class: 'state-circle accept',
            'data-state': stateName
        });
        group.appendChild(outerCircle);
    }
    
    // Main circle - use different style for dead state
    const circle = createSVGElement('circle', {
        cx: pos.x,
        cy: pos.y,
        r: isFinal ? 35 : 38,
        class: 'state-circle' + (isFinal ? ' accept' : '') + (isDeadState ? ' dead-state' : ''),
        'data-state': stateName,
        style: isDeadState ? 'fill: #fee2e2; stroke: #ef4444; stroke-width: 3;' : ''
    });
    group.appendChild(circle);
    
    // State label - use different color for dead state
    const text = createSVGElement('text', {
        x: pos.x,
        y: pos.y + 6,
        class: 'state-text',
        style: isDeadState ? 'fill: #ef4444; font-weight: bold;' : ''
    }, stateName);
    group.appendChild(text);
    
    svgContent.appendChild(group);
}

/**
 * Draws a grouped transition with merged symbols
 * Handles self-loops, bidirectional, and regular transitions
 * @param {SVGElement} svgContent - The SVG group to draw into
 * @param {string} fromState - Source state
 * @param {string} toState - Target state
 * @param {Array} symbols - Array of input symbols
 */
function drawGroupedTransition(svgContent, fromState, toState, symbols) {
    const fromPos = statePositions[fromState];
    const toPos = statePositions[toState];
    
    if (!fromPos || !toPos) return;
    
    // Merge symbols into comma-separated label
    const label = symbols.join(',');
    
    if (fromState === toState) {
        // Self-loop - draw once with merged label
        drawSelfLoop(svgContent, fromPos, label, fromState, toState);
    } else {
        // Check if there's a reverse transition
        const hasReverse = hasReverseTransition(fromState, toState);
        
        if (hasReverse) {
            // Curved arrow for bidirectional transitions
            drawCurvedArrow(svgContent, fromPos, toPos, label, fromState, toState);
        } else {
            // Straight arrow
            drawStraightArrow(svgContent, fromPos, toPos, label, fromState, toState);
        }
    }
}

/**
 * Draws a transition arrow between two states
 * Handles self-loops, bidirectional, and regular transitions
 * @param {SVGElement} svgContent - The SVG group to draw into
 * @param {string} fromState - Source state
 * @param {string} toState - Target state
 * @param {string} symbol - Input symbol for this transition
 */
function drawTransition(svgContent, fromState, toState, symbol) {
    const fromPos = statePositions[fromState];
    const toPos = statePositions[toState];
    
    if (!fromPos || !toPos) return;
    
    if (fromState === toState) {
        // Self-loop
        drawSelfLoop(svgContent, fromPos, symbol, fromState, toState);
    } else {
        // Check if there's a reverse transition
        const hasReverse = hasReverseTransition(fromState, toState);
        
        if (hasReverse) {
            // Curved arrow for bidirectional transitions
            drawCurvedArrow(svgContent, fromPos, toPos, symbol, fromState, toState);
        } else {
            // Straight arrow
            drawStraightArrow(svgContent, fromPos, toPos, symbol, fromState, toState);
        }
    }
}

/**
 * Checks if there's a reverse transition between two states
 * @param {string} fromState - Source state
 * @param {string} toState - Target state
 * @returns {boolean} - True if reverse transition exists
 */
function hasReverseTransition(fromState, toState) {
    // This would need access to the current DFA
    // For simplicity, we'll draw all non-self-loops as straight arrows
    // A more sophisticated version would track all transitions
    return false;
}

/**
 * Draws a self-loop transition (state to itself)
 * @param {SVGElement} svgContent - The SVG group
 * @param {Object} pos - Position of the state
 * @param {string} symbol - Input symbol
 * @param {string} fromState - Source state name
 * @param {string} toState - Target state name
 */
function drawSelfLoop(svgContent, pos, symbol, fromState, toState) {
    const startX = pos.x - 25;
    const startY = pos.y - 35;
    const endX = pos.x + 25;
    const endY = pos.y - 35;
    const controlX = pos.x;
    const controlY = pos.y - 75;
    
    const path = createSVGElement('path', {
        d: `M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`,
        class: 'transition-arrow',
        'data-from': fromState,
        'data-to': toState
    });
    svgContent.appendChild(path);
    
    // Label
    const text = createSVGElement('text', {
        x: controlX,
        y: controlY - 10,
        class: 'transition-label'
    }, symbol);
    svgContent.appendChild(text);
}

/**
 * Draws a curved arrow (for bidirectional transitions)
 * @param {SVGElement} svgContent - The SVG group
 * @param {Object} fromPos - Source position
 * @param {Object} toPos - Target position
 * @param {string} symbol - Input symbol
 * @param {string} fromState - Source state name
 * @param {string} toState - Target state name
 */
function drawCurvedArrow(svgContent, fromPos, toPos, symbol, fromState, toState) {
    const dx = toPos.x - fromPos.x;
    const dy = toPos.y - fromPos.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    const radius = 38;
    const startX = fromPos.x + (dx / distance) * radius;
    const startY = fromPos.y + (dy / distance) * radius;
    const endX = toPos.x - (dx / distance) * (radius + 8);
    const endY = toPos.y - (dy / distance) * (radius + 8);
    
    // Calculate control point for curve
    const midX = (startX + endX) / 2;
    const midY = (startY + endY) / 2;
    const perpX = -(endY - startY) * 0.25;
    const perpY = (endX - startX) * 0.25;
    const controlX = midX + perpX;
    const controlY = midY + perpY;
    
    const path = createSVGElement('path', {
        d: `M ${startX} ${startY} Q ${controlX} ${controlY} ${endX} ${endY}`,
        class: 'transition-arrow',
        'data-from': fromState,
        'data-to': toState
    });
    svgContent.appendChild(path);
    
    // Label
    const text = createSVGElement('text', {
        x: controlX,
        y: controlY - 10,
        class: 'transition-label'
    }, symbol);
    svgContent.appendChild(text);
}

/**
 * Draws a straight arrow between two states
 * @param {SVGElement} svgContent - The SVG group
 * @param {Object} fromPos - Source position
 * @param {Object} toPos - Target position
 * @param {string} symbol - Input symbol
 * @param {string} fromState - Source state name
 * @param {string} toState - Target state name
 */
function drawStraightArrow(svgContent, fromPos, toPos, symbol, fromState, toState) {
    const dx = toPos.x - fromPos.x;
    const dy = toPos.y - fromPos.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    const radius = 38;
    const startX = fromPos.x + (dx / distance) * radius;
    const startY = fromPos.y + (dy / distance) * radius;
    const endX = toPos.x - (dx / distance) * (radius + 8);
    const endY = toPos.y - (dy / distance) * (radius + 8);
    
    const path = createSVGElement('path', {
        d: `M ${startX} ${startY} L ${endX} ${endY}`,
        class: 'transition-arrow',
        'data-from': fromState,
        'data-to': toState
    });
    svgContent.appendChild(path);
    
    // Label at midpoint
    const labelX = (startX + endX) / 2;
    const labelY = (startY + endY) / 2;
    
    const text = createSVGElement('text', {
        x: labelX,
        y: labelY - 10,
        class: 'transition-label'
    }, symbol);
    svgContent.appendChild(text);
}

/**
 * Draws the start arrow pointing to the initial state
 * @param {SVGElement} svgContent - The SVG group
 * @param {string} state - Initial state name
 */
function drawStartArrow(svgContent, state) {
    const pos = statePositions[state];
    if (!pos) return;
    
    const startX = pos.x - 95;
    const startY = pos.y;
    const endX = pos.x - 38;
    const endY = pos.y;
    
    const path = createSVGElement('path', {
        d: `M ${startX} ${startY} L ${endX} ${endY}`,
        class: 'start-arrow'
    });
    svgContent.appendChild(path);
    
    const text = createSVGElement('text', {
        x: startX - 15,
        y: startY + 5,
        class: 'transition-label',
        fill: '#10b981'
    }, 'start');
    svgContent.appendChild(text);
}

/**
 * Highlights a state during animation
 * @param {string} stateName - Name of the state to highlight
 */
function highlightState(stateName) {
    const circles = document.querySelectorAll('.state-circle');
    circles.forEach(circle => {
        if (circle.dataset.state === stateName) {
            circle.classList.add('active');
        } else {
            circle.classList.remove('active');
        }
    });
}

/**
 * Highlights a transition edge during animation
 * @param {string} fromState - Source state
 * @param {string} toState - Target state
 */
function highlightEdge(fromState, toState) {
    const arrows = document.querySelectorAll('.transition-arrow');
    arrows.forEach(arrow => {
        if (arrow.dataset.from === fromState && arrow.dataset.to === toState) {
            arrow.classList.add('active');
        } else {
            arrow.classList.remove('active');
        }
    });
}

/**
 * Clears all highlights
 */
function clearHighlights() {
    const circles = document.querySelectorAll('.state-circle');
    circles.forEach(circle => circle.classList.remove('active'));
    
    const arrows = document.querySelectorAll('.transition-arrow');
    arrows.forEach(arrow => arrow.classList.remove('active'));
}

/**
 * Creates an SVG element with attributes
 * @param {string} tag - SVG tag name
 * @param {Object} attributes - Key-value pairs of attributes
 * @param {string} text - Text content (optional)
 * @returns {SVGElement} - The created SVG element
 */
function createSVGElement(tag, attributes, text) {
    const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
    
    for (let key in attributes) {
        if (attributes[key] !== null && attributes[key] !== undefined) {
            element.setAttribute(key, attributes[key]);
        }
    }
    
    if (text !== undefined) {
        element.textContent = text;
    }
    
    return element;
}
