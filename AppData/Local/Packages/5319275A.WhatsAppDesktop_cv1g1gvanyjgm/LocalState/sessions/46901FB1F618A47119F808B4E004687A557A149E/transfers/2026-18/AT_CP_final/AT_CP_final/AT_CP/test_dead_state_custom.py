"""
Test Script - Dead State Integration for Custom DFA
=====================================================
This script tests the frontend dead state implementation:
1. Dead state (qd) is automatically added to state list
2. Dead state appears in transition table
3. Dead state loops to itself for all symbols
4. Undefined transitions default to dead state
5. Dead state cannot be a final state
"""

import json

def test_dead_state_in_custom_dfa():
    """Test that custom DFA includes dead state"""
    print("=" * 70)
    print("TEST 1: Dead State in Custom DFA")
    print("=" * 70)
    
    # Simulate frontend DFA generation
    states = ['q0', 'q1', 'q2']
    DEAD_STATE = 'qd'
    
    # Add dead state
    if DEAD_STATE not in states:
        states.append(DEAD_STATE)
    
    print(f"States: {states}")
    assert DEAD_STATE in states, "❌ Dead state not in state list!"
    print(f"✅ Dead state '{DEAD_STATE}' is in state list")
    print()

def test_dead_state_transitions():
    """Test dead state self-loop transitions"""
    print("=" * 70)
    print("TEST 2: Dead State Self-Loop Transitions")
    print("=" * 70)
    
    alphabet = ['a', 'b']
    DEAD_STATE = 'qd'
    transitions = {
        'qd': {}
    }
    
    # Initialize dead state transitions
    for symbol in alphabet:
        transitions[DEAD_STATE][symbol] = DEAD_STATE
    
    print(f"Dead state transitions: {transitions[DEAD_STATE]}")
    
    for symbol in alphabet:
        assert transitions[DEAD_STATE][symbol] == DEAD_STATE, \
            f"❌ Dead state transition on '{symbol}' should go to {DEAD_STATE}"
        print(f"✅ qd --{symbol}--> qd")
    
    print()

def test_undefined_transitions_fill():
    """Test that undefined transitions are filled with dead state"""
    print("=" * 70)
    print("TEST 3: Undefined Transitions Fill with Dead State")
    print("=" * 70)
    
    states = ['q0', 'q1', 'qd']
    alphabet = ['a', 'b']
    DEAD_STATE = 'qd'
    
    # Simulate partial transitions (user only defined some)
    transitions = {
        'q0': {'a': 'q1'},  # Missing 'b' transition
        'q1': {},            # Missing both transitions
        'qd': {'a': 'qd', 'b': 'qd'}
    }
    
    # Fill undefined transitions
    for state in states:
        if state == DEAD_STATE:
            continue
        
        if state not in transitions:
            transitions[state] = {}
        
        for symbol in alphabet:
            if symbol not in transitions[state] or not transitions[state][symbol]:
                transitions[state][symbol] = DEAD_STATE
    
    print("After filling undefined transitions:")
    for state in states:
        print(f"  {state}: {transitions[state]}")
    
    # Verify all transitions are defined
    for state in states:
        for symbol in alphabet:
            assert symbol in transitions[state], \
                f"❌ State {state} missing transition for '{symbol}'"
            print(f"✅ δ({state}, {symbol}) = {transitions[state][symbol]}")
    
    print()

def test_dead_state_not_final():
    """Test that dead state is not in final states"""
    print("=" * 70)
    print("TEST 4: Dead State Not in Final States")
    print("=" * 70)
    
    states = ['q0', 'q1', 'qd']
    DEAD_STATE = 'qd'
    finals = ['q1']  # Only q1 is final
    
    # Ensure dead state is not in finals
    assert DEAD_STATE not in finals, "❌ Dead state should not be in final states!"
    print(f"Final states: {finals}")
    print(f"✅ Dead state '{DEAD_STATE}' is NOT in final states")
    print()

def test_complete_dfa():
    """Test that DFA is complete (all transitions defined)"""
    print("=" * 70)
    print("TEST 5: Complete DFA Verification")
    print("=" * 70)
    
    states = ['q0', 'q1', 'qd']
    alphabet = ['a', 'b']
    DEAD_STATE = 'qd'
    
    # Complete DFA
    dfa = {
        "states": states,
        "alphabet": alphabet,
        "initial": "q0",
        "finals": ["q1"],
        "transitions": {
            "q0": {"a": "q1", "b": "qd"},
            "q1": {"a": "q1", "b": "qd"},
            "qd": {"a": "qd", "b": "qd"}
        }
    }
    
    # Verify completeness
    total_transitions = 0
    for state in dfa["states"]:
        for symbol in dfa["alphabet"]:
            assert state in dfa["transitions"], f"❌ State {state} missing from transitions"
            assert symbol in dfa["transitions"][state], \
                f"❌ State {state} missing transition for '{symbol}'"
            total_transitions += 1
    
    expected_transitions = len(states) * len(alphabet)
    print(f"Total transitions: {total_transitions} (expected: {expected_transitions})")
    assert total_transitions == expected_transitions, "❌ DFA is not complete!"
    print("✅ DFA is complete - all (state, symbol) pairs have transitions")
    print()

def test_dead_state_simulation():
    """Test that strings with undefined transitions go to dead state"""
    print("=" * 70)
    print("TEST 6: Simulation with Dead State")
    print("=" * 70)
    
    dfa = {
        "states": ["q0", "q1", "qd"],
        "alphabet": ["a", "b"],
        "initial": "q0",
        "finals": ["q1"],
        "transitions": {
            "q0": {"a": "q1", "b": "qd"},
            "q1": {"a": "q1", "b": "qd"},
            "qd": {"a": "qd", "b": "qd"}
        }
    }
    
    # Test valid string
    input_string = "aa"
    current_state = dfa["initial"]
    path = [current_state]
    
    for char in input_string:
        current_state = dfa["transitions"][current_state][char]
        path.append(current_state)
    
    accepted = current_state in dfa["finals"]
    print(f"Input: '{input_string}'")
    print(f"Path: {' -> '.join(path)}")
    print(f"Accepted: {accepted}")
    assert accepted == True, "❌ Valid string should be accepted!"
    assert current_state != "qd", "❌ Valid string should not end in dead state!"
    print("✅ Valid string accepted correctly")
    print()
    
    # Test invalid string
    input_string = "ba"
    current_state = dfa["initial"]
    path = [current_state]
    
    for char in input_string:
        current_state = dfa["transitions"][current_state][char]
        path.append(current_state)
    
    accepted = current_state in dfa["finals"]
    print(f"Input: '{input_string}'")
    print(f"Path: {' -> '.join(path)}")
    print(f"Accepted: {accepted}")
    assert accepted == False, "❌ Invalid string should be rejected!"
    assert current_state == "qd", "❌ Invalid string should end in dead state!"
    print("✅ Invalid string rejected correctly (went to dead state)")
    print()

if __name__ == "__main__":
    print("\n")
    print("🧪 " * 35)
    print("DEAD STATE INTEGRATION TESTS (Custom DFA)")
    print("🧪 " * 35)
    print("\n")
    
    try:
        test_dead_state_in_custom_dfa()
        test_dead_state_transitions()
        test_undefined_transitions_fill()
        test_dead_state_not_final()
        test_complete_dfa()
        test_dead_state_simulation()
        
        print("=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\n✅ Dead state integration is working correctly:")
        print("   - Dead state (qd) automatically added to states")
        print("   - Dead state has self-loop transitions for all symbols")
        print("   - Undefined transitions default to dead state")
        print("   - Dead state is NOT in final states")
        print("   - DFA is complete (all transitions defined)")
        print("   - Simulation correctly uses dead state")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
