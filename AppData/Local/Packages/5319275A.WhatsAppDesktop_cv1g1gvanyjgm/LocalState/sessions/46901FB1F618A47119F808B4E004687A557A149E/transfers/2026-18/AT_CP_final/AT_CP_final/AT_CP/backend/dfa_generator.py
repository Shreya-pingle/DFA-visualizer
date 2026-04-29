"""
DFA Generator Module - Pattern-Based DFA Construction
======================================================
This module automatically generates DFAs for common pattern-matching tasks.

It implements three fundamental pattern types:
1. Starts With: Strings that begin with a specific pattern
2. Ends With: Strings that end with a specific pattern
3. Contains Substring: Strings that contain a pattern anywhere

These generators demonstrate how theoretical DFA construction works in practice.
Each generator creates a complete, valid DFA with all transitions defined.
"""


def generate_starts_with(pattern, alphabet):
    """
    Generates a DFA that accepts strings STARTING WITH the given pattern.
    
    Theory:
    -------
    To recognize strings starting with pattern P = p1p2...pn:
    - Create states q0, q1, q2, ..., qn (n+1 states for pattern of length n)
    - qi represents having matched the first i characters of the pattern
    - qn is the accept state (pattern fully matched at start)
    - Add a trap/reject state for invalid starts
    - Once in qn, stay in qn (any continuation is valid)
    
    Example: Pattern "ab" with alphabet {a, b}
    - q0: start state
    - q1: matched "a"
    - q2: matched "ab" (ACCEPT)
    - q3: trap state (started with wrong character)
    
    Transitions:
    - q0 --a--> q1, q0 --b--> q3
    - q1 --a--> q3, q1 --b--> q2
    - q2 --a,b--> q2 (accept all continuations)
    - q3 --a,b--> q3 (trap state)
    
    Parameters:
        pattern (str): The pattern that strings must start with (e.g., "ab")
        alphabet (list): List of symbols in the alphabet (e.g., ["a", "b"])
    
    Returns:
        dict: Complete DFA structure
    """
    states = []
    transitions = {}
    
    # Create states: q0, q1, ..., qn, q_reject (dead state)
    # qn is accept state, q_reject is trap/dead state
    n = len(pattern)
    for i in range(n + 1):
        states.append(f"q{i}")
    states.append("q_reject")  # Dead state - explicitly added for invalid transitions
    
    # Accept state is qn (pattern fully matched)
    # q_reject (dead state) is NOT an accept state
    finals = [f"q{n}"]
    
    # Build transitions
    for i in range(n + 1):
        current_state = f"q{i}"
        transitions[current_state] = {}
        
        if i < n:
            # Still matching the pattern
            expected_char = pattern[i]
            for symbol in alphabet:
                if symbol == expected_char:
                    # Matched next character, progress to next state
                    transitions[current_state][symbol] = f"q{i+1}"
                else:
                    # Wrong character, go to reject state
                    transitions[current_state][symbol] = "q_reject"
        else:
            # In accept state (qn) - stay here for any input
            # Once pattern is matched at start, accept all continuations
            for symbol in alphabet:
                transitions[current_state][symbol] = current_state
    
    # Dead state (trap state) - once here, never leave
    # All transitions from dead state go back to dead state
    transitions["q_reject"] = {}
    for symbol in alphabet:
        transitions["q_reject"][symbol] = "q_reject"
    
    # Construct complete DFA
    dfa = {
        "states": states,
        "alphabet": alphabet,
        "initial": "q0",
        "finals": finals,
        "transitions": transitions
    }
    
    return dfa


def generate_ends_with(pattern, alphabet):
    """
    Generates a DFA that accepts strings ENDING WITH the given pattern.
    
    Theory:
    -------
    To recognize strings ending with pattern P = p1p2...pn:
    - Track the longest suffix of the input that matches a prefix of P
    - This is similar to the KMP (Knuth-Morris-Pratt) algorithm's failure function
    - State qi means we've matched the last i characters as the first i of P
    - qn is the accept state (we just completed the pattern)
    
    Example: Pattern "ab" with alphabet {a, b}
    - q0: no match or last char was not useful
    - q1: last char was 'a' (could be start of "ab")
    - q2: last two chars were "ab" (ACCEPT)
    
    Transitions:
    - q0 --a--> q1, q0 --b--> q0
    - q1 --a--> q1, q1 --b--> q2
    - q2 --a--> q1, q2 --b--> q0
    
    Parameters:
        pattern (str): The pattern that strings must end with (e.g., "ab")
        alphabet (list): List of symbols in the alphabet
    
    Returns:
        dict: Complete DFA structure
    """
    n = len(pattern)
    
    # Create states: q0, q1, ..., qn
    states = [f"q{i}" for i in range(n + 1)]
    
    # Only qn is accept state
    finals = [f"q{n}"]
    
    # Build transition function using KMP-like logic
    transitions = {}
    for i in range(n + 1):
        current_state = f"q{i}"
        transitions[current_state] = {}
        
        for symbol in alphabet:
            # Try to find the longest prefix of pattern that is a suffix
            # of (pattern[0:i] + symbol)
            if i < n and symbol == pattern[i]:
                # Perfect match, advance to next state
                transitions[current_state][symbol] = f"q{i+1}"
            else:
                # Mismatch or full match - find fallback state
                # Build the string we're trying to match
                if i < n:
                    test_string = pattern[:i] + symbol
                else:
                    test_string = pattern + symbol
                
                # Find longest prefix of pattern that matches suffix of test_string
                fallback = 0
                for length in range(min(len(test_string), n), 0, -1):
                    if test_string.endswith(pattern[:length]):
                        fallback = length
                        break
                
                transitions[current_state][symbol] = f"q{fallback}"
    
    # Construct complete DFA
    dfa = {
        "states": states,
        "alphabet": alphabet,
        "initial": "q0",
        "finals": finals,
        "transitions": transitions
    }
    
    return dfa


def generate_contains_substring(pattern, alphabet):
    """
    Generates a DFA that accepts strings CONTAINING the given pattern as a substring.
    
    Theory:
    -------
    To recognize strings containing pattern P anywhere:
    - Similar to "ends with" but the accept state becomes a trap state
    - Once we've seen the pattern, we stay in the accept state forever
    - State qi means we've matched the last i characters as prefix of P
    - qn is accept state (pattern found)
    
    Example: Pattern "aba" with alphabet {a, b}
    - q0: no useful match
    - q1: last char 'a'
    - q2: last two chars 'ab'
    - q3: found 'aba' (ACCEPT - trap state)
    
    Transitions:
    - q0 --a--> q1, q0 --b--> q0
    - q1 --a--> q1, q1 --b--> q2
    - q2 --a--> q3, q2 --b--> q0
    - q3 --a,b--> q3 (once found, always accepting)
    
    Parameters:
        pattern (str): The substring to search for (e.g., "aba")
        alphabet (list): List of symbols in the alphabet
    
    Returns:
        dict: Complete DFA structure
    """
    n = len(pattern)
    
    # Create states: q0, q1, ..., qn
    states = [f"q{i}" for i in range(n + 1)]
    
    # Only qn is accept state (pattern found)
    finals = [f"q{n}"]
    
    # Build transition function
    transitions = {}
    for i in range(n + 1):
        current_state = f"q{i}"
        transitions[current_state] = {}
        
        for symbol in alphabet:
            if i == n:
                # Already in accept state - stay here (trap state)
                # Once pattern is found, string is accepted regardless of what follows
                transitions[current_state][symbol] = current_state
            elif symbol == pattern[i]:
                # Match next character in pattern
                transitions[current_state][symbol] = f"q{i+1}"
            else:
                # Mismatch - find fallback state
                if i < n:
                    test_string = pattern[:i] + symbol
                else:
                    test_string = pattern + symbol
                
                # Find longest prefix of pattern that matches suffix
                fallback = 0
                for length in range(min(len(test_string), n), 0, -1):
                    if test_string.endswith(pattern[:length]):
                        fallback = length
                        break
                
                transitions[current_state][symbol] = f"q{fallback}"
    
    # Construct complete DFA
    dfa = {
        "states": states,
        "alphabet": alphabet,
        "initial": "q0",
        "finals": finals,
        "transitions": transitions
    }
    
    return dfa


def generate_dfa(mode, pattern, alphabet):
    """
    Main generator function that dispatches to the appropriate pattern generator.
    
    Parameters:
        mode (str): One of "starts", "ends", or "substring"
        pattern (str): The pattern to match
        alphabet (list): List of symbols in the alphabet
    
    Returns:
        dict: Complete DFA structure
    
    Raises:
        ValueError: If mode is invalid
    """
    # Validate inputs
    if mode not in ["starts", "ends", "substring"]:
        raise ValueError(f"Invalid mode: {mode}. Must be 'starts', 'ends', or 'substring'")
    
    if not pattern:
        raise ValueError("Pattern cannot be empty")
    
    if not alphabet:
        raise ValueError("Alphabet cannot be empty")
    
    # Check that pattern uses only symbols from alphabet
    alphabet_set = set(alphabet)
    for char in pattern:
        if char not in alphabet_set:
            raise ValueError(
                f"Pattern contains '{char}' which is not in alphabet {alphabet}"
            )
    
    # Generate DFA based on mode
    if mode == "starts":
        return generate_starts_with(pattern, alphabet)
    elif mode == "ends":
        return generate_ends_with(pattern, alphabet)
    elif mode == "substring":
        return generate_contains_substring(pattern, alphabet)
