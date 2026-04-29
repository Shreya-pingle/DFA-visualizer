"""
DFA Logic Module - Core Automata Theory Implementation
========================================================
This module implements the fundamental DFA (Deterministic Finite Automaton) logic.

A DFA is formally defined as a 5-tuple: M = (Q, Σ, δ, q0, F)
Where:
  - Q: Finite set of states
  - Σ: Finite input alphabet
  - δ: Transition function (Q × Σ → Q)
  - q0: Initial state (q0 ∈ Q)
  - F: Set of final/accept states (F ⊆ Q)

This module provides:
  1. DFA validation (checking if the structure is correct)
  2. DFA simulation (processing input strings step-by-step)
  3. Deterministic property verification
"""


def validate_dfa(dfa):
    """
    Validates a DFA structure to ensure it follows the formal definition.
    
    A valid DFA must satisfy:
    1. Has all required components: states, alphabet, initial, finals, transitions
    2. Initial state must be in the set of states
    3. All final states must be in the set of states
    4. Every state must have exactly one transition for each symbol in alphabet
    5. All transition targets must be valid states
    
    Parameters:
        dfa (dict): DFA in the format:
                   {
                       "states": ["q0", "q1"],
                       "alphabet": ["0", "1"],
                       "initial": "q0",
                       "finals": ["q1"],
                       "transitions": {"q0": {"0": "q1", "1": "q0"}, ...}
                   }
    
    Returns:
        dict: {"valid": bool, "errors": [list of error messages]}
    """
    errors = []
    
    # Check 1: Verify all required fields exist
    required_fields = ["states", "alphabet", "initial", "finals", "transitions"]
    for field in required_fields:
        if field not in dfa:
            errors.append(f"Missing required field: '{field}'")
    
    # If basic fields are missing, return early
    if errors:
        return {"valid": False, "errors": errors}
    
    states = set(dfa["states"])
    alphabet = set(dfa["alphabet"])
    initial = dfa["initial"]
    finals = set(dfa["finals"])
    transitions = dfa["transitions"]
    
    # Check 2: Initial state must be in Q
    if initial not in states:
        errors.append(f"Initial state '{initial}' is not in the set of states Q")
    
    # Check 3: All final states must be in Q
    for final_state in finals:
        if final_state not in states:
            errors.append(f"Final state '{final_state}' is not in the set of states Q")
    
    # Check 4: Every state must have transitions defined
    for state in states:
        if state not in transitions:
            errors.append(f"No transitions defined for state '{state}'")
            continue
        
        state_transitions = transitions[state]
        
        # Check 5: Every state must have a transition for each symbol in alphabet
        for symbol in alphabet:
            if symbol not in state_transitions:
                errors.append(
                    f"State '{state}' missing transition for symbol '{symbol}'"
                )
        
        # Check 6: All transition targets must be valid states
        for symbol, target_state in state_transitions.items():
            if target_state not in states:
                errors.append(
                    f"Transition δ({state}, {symbol}) = '{target_state}' is not a valid state"
                )
    
    # Check 7: Verify deterministic property (no duplicate transitions)
    is_deterministic, det_errors = check_deterministic(dfa)
    if not is_deterministic:
        errors.extend(det_errors)
    
    # Return validation result
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def check_deterministic(dfa):
    """
    Checks if the DFA is truly deterministic.
    
    A DFA is deterministic if:
    - For every state q ∈ Q and every symbol a ∈ Σ,
      there is EXACTLY ONE transition δ(q, a)
    
    This is already enforced by the structure (dict allows only one value per key),
    but we verify completeness here.
    
    Parameters:
        dfa (dict): DFA structure
    
    Returns:
        tuple: (is_deterministic: bool, errors: [list])
    """
    errors = []
    states = dfa["states"]
    alphabet = dfa["alphabet"]
    transitions = dfa["transitions"]
    
    for state in states:
        if state not in transitions:
            errors.append(f"State '{state}' has no transitions defined")
            continue
        
        # Check that transitions only contain symbols from alphabet
        for symbol in transitions[state]:
            if symbol not in alphabet:
                errors.append(
                    f"State '{state}' has transition for symbol '{symbol}' "
                    f"which is not in alphabet Σ"
                )
    
    is_deterministic = len(errors) == 0
    return is_deterministic, errors


def simulate_dfa(dfa, input_string):
    """
    Simulates the DFA on a given input string step-by-step.
    
    This is the core execution engine that demonstrates how a DFA processes input:
    1. Start at the initial state q0
    2. For each character in the input string:
       - Look up the transition function δ(current_state, character)
       - Move to the next state
       - Record the path
    3. After processing all characters:
       - If final state ∈ F, ACCEPT the string
       - Otherwise, REJECT the string
    
    Parameters:
        dfa (dict): Valid DFA structure
        input_string (str): String to process (e.g., "0011", "abab")
    
    Returns:
        dict: {
            "path": [list of states visited],
            "final_state": last state reached,
            "accepted": bool (whether string is accepted),
            "error": error message if any (e.g., invalid symbol)
        }
    
    Example:
        DFA accepts strings ending with '0'
        Input: "100"
        Path: ["q0", "q0", "q1", "q1"]
        Final: "q1"
        Accepted: True (q1 is in final states)
    """
    # Validate input string against alphabet
    alphabet = set(dfa["alphabet"])
    for char in input_string:
        if char not in alphabet:
            return {
                "path": [],
                "final_state": None,
                "accepted": False,
                "error": f"Symbol '{char}' is not in alphabet Σ = {sorted(alphabet)}"
            }
    
    # Start simulation from initial state
    current_state = dfa["initial"]
    path = [current_state]  # Record the path of states visited
    
    # Process each character in the input string
    for char in input_string:
        # Get transition for current state and input symbol
        # δ(current_state, char) -> next_state
        next_state = dfa["transitions"][current_state][char]
        current_state = next_state
        path.append(current_state)  # Add to path
    
    # Determine if string is accepted
    # String is accepted if final state is in the set of accept states F
    accepted = current_state in dfa["finals"]
    
    return {
        "path": path,
        "final_state": current_state,
        "accepted": accepted,
        "error": None
    }


def get_dfa_info(dfa):
    """
    Returns formatted information about the DFA for display.
    
    This helps visualize the 5-tuple definition: M = (Q, Σ, δ, q0, F)
    
    Parameters:
        dfa (dict): DFA structure
    
    Returns:
        dict: Formatted DFA components for UI display
    """
    return {
        "states": dfa["states"],
        "alphabet": dfa["alphabet"],
        "initial": dfa["initial"],
        "finals": dfa["finals"],
        "num_states": len(dfa["states"]),
        "num_symbols": len(dfa["alphabet"]),
        "transition_function": dfa["transitions"]
    }
