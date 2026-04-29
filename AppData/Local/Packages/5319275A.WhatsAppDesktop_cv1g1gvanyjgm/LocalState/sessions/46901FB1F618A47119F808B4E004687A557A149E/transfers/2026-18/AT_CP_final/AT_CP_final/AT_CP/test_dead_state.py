"""
Test Script - Dead State Verification for "Starts With" DFA
=============================================================
This script tests that:
1. Dead state (q_reject) is created for "starts with" pattern
2. Dead state has proper transitions (loops to itself)
3. Dead state is NOT an accept state
4. Invalid strings correctly transition to dead state and are rejected
"""

from backend.dfa_generator import generate_starts_with
from backend.dfa_logic import simulate_dfa, validate_dfa

def test_dead_state_exists():
    """Test that dead state is created in starts-with DFA"""
    print("=" * 60)
    print("TEST 1: Dead State Existence")
    print("=" * 60)
    
    dfa = generate_starts_with("ab", ["a", "b"])
    
    # Check if q_reject is in states
    assert "q_reject" in dfa["states"], "❌ Dead state (q_reject) not found in states!"
    print("✅ Dead state (q_reject) exists in states")
    
    # Check if q_reject is NOT in finals
    assert "q_reject" not in dfa["finals"], "❌ Dead state should NOT be an accept state!"
    print("✅ Dead state is NOT an accept state")
    
    # Check if q_reject has transitions defined
    assert "q_reject" in dfa["transitions"], "❌ Dead state has no transitions!"
    print("✅ Dead state has transitions defined")
    
    print()

def test_dead_state_transitions():
    """Test that dead state loops to itself for all symbols"""
    print("=" * 60)
    print("TEST 2: Dead State Self-Loop Transitions")
    print("=" * 60)
    
    dfa = generate_starts_with("ab", ["a", "b"])
    
    # Check that all transitions from q_reject go back to q_reject
    for symbol in dfa["alphabet"]:
        target = dfa["transitions"]["q_reject"][symbol]
        assert target == "q_reject", f"❌ Dead state transition on '{symbol}' should go to q_reject, not {target}"
        print(f"✅ Dead state: q_reject --{symbol}--> q_reject")
    
    print()

def test_invalid_string_rejection():
    """Test that strings not starting with pattern go to dead state"""
    print("=" * 60)
    print("TEST 3: Invalid String Rejection via Dead State")
    print("=" * 60)
    
    dfa = generate_starts_with("ab", ["a", "b"])
    
    # Test string starting with wrong character
    test_string = "ba"
    result = simulate_dfa(dfa, test_string)
    
    print(f"Input string: '{test_string}'")
    print(f"Path: {' -> '.join(result['path'])}")
    print(f"Final state: {result['final_state']}")
    print(f"Accepted: {result['accepted']}")
    
    # Should end in q_reject
    assert result["final_state"] == "q_reject", f"❌ Should end in q_reject, but ended in {result['final_state']}"
    print("✅ String correctly transitions to dead state")
    
    # Should be rejected
    assert result["accepted"] == False, "❌ String should be rejected!"
    print("✅ String is correctly rejected")
    
    print()

def test_valid_string_acceptance():
    """Test that valid strings are accepted"""
    print("=" * 60)
    print("TEST 4: Valid String Acceptance")
    print("=" * 60)
    
    dfa = generate_starts_with("ab", ["a", "b"])
    
    # Test valid string
    test_string = "abba"
    result = simulate_dfa(dfa, test_string)
    
    print(f"Input string: '{test_string}'")
    print(f"Path: {' -> '.join(result['path'])}")
    print(f"Final state: {result['final_state']}")
    print(f"Accepted: {result['accepted']}")
    
    # Should NOT be in q_reject
    assert result["final_state"] != "q_reject", f"❌ Valid string should not end in dead state!"
    print("✅ Valid string does NOT go to dead state")
    
    # Should be accepted
    assert result["accepted"] == True, "❌ Valid string should be accepted!"
    print("✅ Valid string is correctly accepted")
    
    print()

def test_dfa_validation():
    """Test that the generated DFA is valid"""
    print("=" * 60)
    print("TEST 5: DFA Validation")
    print("=" * 60)
    
    dfa = generate_starts_with("ab", ["a", "b"])
    validation = validate_dfa(dfa)
    
    print(f"DFA Valid: {validation['valid']}")
    if validation['errors']:
        print(f"Errors: {validation['errors']}")
    
    assert validation['valid'], f"❌ DFA should be valid! Errors: {validation['errors']}"
    print("✅ Generated DFA is valid")
    
    print()

def test_transition_table_completeness():
    """Test that all states including dead state are in transition table"""
    print("=" * 60)
    print("TEST 6: Transition Table Completeness")
    print("=" * 60)
    
    dfa = generate_starts_with("ab", ["a", "b"])
    
    print(f"States: {dfa['states']}")
    print(f"States in transitions: {list(dfa['transitions'].keys())}")
    
    # All states should have transitions
    for state in dfa["states"]:
        assert state in dfa["transitions"], f"❌ State {state} missing from transition table!"
        print(f"✅ State '{state}' has transitions defined")
        
        # All symbols should have transitions
        for symbol in dfa["alphabet"]:
            assert symbol in dfa["transitions"][state], f"❌ State {state} missing transition for symbol {symbol}"
    
    print("✅ All states have complete transition entries")
    
    print()

if __name__ == "__main__":
    print("\n")
    print("🧪 " * 30)
    print("DEAD STATE VERIFICATION TESTS")
    print("🧪 " * 30)
    print("\n")
    
    try:
        test_dead_state_exists()
        test_dead_state_transitions()
        test_invalid_string_rejection()
        test_valid_string_acceptance()
        test_dfa_validation()
        test_transition_table_completeness()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Dead state is properly implemented:")
        print("   - Dead state (q_reject) exists")
        print("   - Dead state has self-loop transitions")
        print("   - Dead state is NOT an accept state")
        print("   - Invalid strings correctly transition to dead state")
        print("   - Transition table includes dead state")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
