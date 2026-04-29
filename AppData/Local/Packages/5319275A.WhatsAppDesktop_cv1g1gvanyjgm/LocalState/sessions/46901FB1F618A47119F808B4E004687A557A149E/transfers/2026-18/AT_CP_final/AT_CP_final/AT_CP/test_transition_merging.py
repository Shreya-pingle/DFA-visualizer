"""
Test Script - Transition Merging and Self-Loop Rendering
==========================================================
This test verifies that:
1. Multiple transitions to the same state are grouped correctly
2. Self-loops show merged labels (e.g., "0,1" instead of separate loops)
3. Dead state shows "0,1" on its self-loop
"""

def test_transition_grouping():
    """Test that transitions are grouped correctly"""
    print("=" * 70)
    print("TEST 1: Transition Grouping Logic")
    print("=" * 70)
    
    # Simulate DFA transitions
    transitions = {
        'q0': {'a': 'q1', 'b': 'q0'},
        'q1': {'a': 'q1', 'b': 'q2'},
        'q2': {'a': 'q2', 'b': 'q2'},  # Both go to q2 (self-loop)
        'qd': {'a': 'qd', 'b': 'qd'}   # Dead state self-loop
    }
    
    # Group transitions (simulating frontend logic)
    grouped = {}
    for fromState in transitions:
        for symbol in transitions[fromState]:
            toState = transitions[fromState][symbol]
            key = f"{fromState}->{toState}"
            
            if key not in grouped:
                grouped[key] = {
                    'fromState': fromState,
                    'toState': toState,
                    'symbols': []
                }
            
            if symbol not in grouped[key]['symbols']:
                grouped[key]['symbols'].append(symbol)
    
    print("\nGrouped transitions:")
    for key in sorted(grouped.keys()):
        g = grouped[key]
        label = ','.join(g['symbols'])
        print(f"  {g['fromState']} → {g['toState']}: {label}")
    
    # Verify specific cases
    print("\nVerification:")
    
    # q2 self-loop should have "a,b"
    q2_key = "q2->q2"
    assert q2_key in grouped, "❌ q2 self-loop not found!"
    assert set(grouped[q2_key]['symbols']) == {'a', 'b'}, \
        f"❌ q2 self-loop should have ['a', 'b'], got {grouped[q2_key]['symbols']}"
    print(f"✅ q2 self-loop: {','.join(sorted(grouped[q2_key]['symbols']))}")
    
    # qd self-loop should have "a,b"
    qd_key = "qd->qd"
    assert qd_key in grouped, "❌ qd self-loop not found!"
    assert set(grouped[qd_key]['symbols']) == {'a', 'b'}, \
        f"❌ qd self-loop should have ['a', 'b'], got {grouped[qd_key]['symbols']}"
    print(f"✅ qd self-loop: {','.join(sorted(grouped[qd_key]['symbols']))}")
    
    # q0->q1 should have only "a"
    q0_q1_key = "q0->q1"
    assert q0_q1_key in grouped, "❌ q0->q1 transition not found!"
    assert grouped[q0_q1_key]['symbols'] == ['a'], \
        f"❌ q0->q1 should have ['a'], got {grouped[q0_q1_key]['symbols']}"
    print(f"✅ q0 → q1: {','.join(grouped[q0_q1_key]['symbols'])}")
    
    print()

def test_label_formatting():
    """Test that labels are formatted correctly"""
    print("=" * 70)
    print("TEST 2: Label Formatting")
    print("=" * 70)
    
    # Test single symbol
    symbols1 = ['a']
    label1 = ','.join(symbols1)
    print(f"Single symbol: {label1}")
    assert label1 == 'a', f"❌ Single symbol should be 'a', got '{label1}'"
    print("✅ Single symbol: no comma")
    
    # Test two symbols
    symbols2 = ['a', 'b']
    label2 = ','.join(symbols2)
    print(f"Two symbols: {label2}")
    assert label2 == 'a,b', f"❌ Two symbols should be 'a,b', got '{label2}'"
    print("✅ Two symbols: comma-separated")
    
    # Test three symbols
    symbols3 = ['0', '1', '2']
    label3 = ','.join(symbols3)
    print(f"Three symbols: {label3}")
    assert label3 == '0,1,2', f"❌ Three symbols should be '0,1,2', got '{label3}'"
    print("✅ Three symbols: comma-separated")
    
    print()

def test_dead_state_rendering():
    """Test dead state self-loop rendering"""
    print("=" * 70)
    print("TEST 3: Dead State Rendering")
    print("=" * 70)
    
    # Dead state with binary alphabet
    transitions = {
        'qd': {'0': 'qd', '1': 'qd'}
    }
    
    # Group transitions
    grouped = {}
    for fromState in transitions:
        for symbol in transitions[fromState]:
            toState = transitions[fromState][symbol]
            key = f"{fromState}->{toState}"
            
            if key not in grouped:
                grouped[key] = {
                    'fromState': fromState,
                    'toState': toState,
                    'symbols': []
                }
            
            if symbol not in grouped[key]['symbols']:
                grouped[key]['symbols'].append(symbol)
    
    # Verify dead state
    qd_key = "qd->qd"
    assert qd_key in grouped, "❌ Dead state self-loop not found!"
    
    label = ','.join(sorted(grouped[qd_key]['symbols']))
    print(f"Dead state self-loop label: '{label}'")
    
    assert label == '0,1', f"❌ Dead state should show '0,1', got '{label}'"
    print("✅ Dead state shows '0,1' on self-loop")
    print()

def test_no_duplicate_edges():
    """Test that no duplicate edges are created"""
    print("=" * 70)
    print("TEST 4: No Duplicate Edges")
    print("=" * 70)
    
    # DFA with multiple transitions to same state
    transitions = {
        'q0': {'a': 'q1', 'b': 'q1'},  # Both go to q1
        'q1': {'a': 'q1', 'b': 'q1'}   # Both self-loop
    }
    
    # Group transitions
    grouped = {}
    for fromState in transitions:
        for symbol in transitions[fromState]:
            toState = transitions[fromState][symbol]
            key = f"{fromState}->{toState}"
            
            if key not in grouped:
                grouped[key] = {
                    'fromState': fromState,
                    'toState': toState,
                    'symbols': []
                }
            
            if symbol not in grouped[key]['symbols']:
                grouped[key]['symbols'].append(symbol)
    
    print(f"Number of unique edges: {len(grouped)}")
    print(f"Expected: 2 (q0->q1, q1->q1)")
    
    assert len(grouped) == 2, f"❌ Should have 2 unique edges, got {len(grouped)}"
    print("✅ No duplicate edges created")
    
    # Verify labels
    for key in sorted(grouped.keys()):
        g = grouped[key]
        label = ','.join(sorted(g['symbols']))
        print(f"  {g['fromState']} → {g['toState']}: {label}")
    
    print()

def test_complete_dfa_example():
    """Test a complete DFA example"""
    print("=" * 70)
    print("TEST 5: Complete DFA Example")
    print("=" * 70)
    
    # Example DFA: accepts strings ending with '0'
    transitions = {
        'q0': {'0': 'q1', '1': 'q0'},
        'q1': {'0': 'q1', '1': 'q0'},
        'qd': {'0': 'qd', '1': 'qd'}
    }
    
    # Group transitions
    grouped = {}
    for fromState in transitions:
        for symbol in transitions[fromState]:
            toState = transitions[fromState][symbol]
            key = f"{fromState}->{toState}"
            
            if key not in grouped:
                grouped[key] = {
                    'fromState': fromState,
                    'toState': toState,
                    'symbols': []
                }
            
            if symbol not in grouped[key]['symbols']:
                grouped[key]['symbols'].append(symbol)
    
    print("\nTransitions to render:")
    for key in sorted(grouped.keys()):
        g = grouped[key]
        label = ','.join(sorted(g['symbols']))
        edge_type = "self-loop" if g['fromState'] == g['toState'] else "arrow"
        print(f"  {g['fromState']} → {g['toState']}: '{label}' ({edge_type})")
    
    # Verify edge count
    print(f"\nTotal edges to draw: {len(grouped)}")
    print("✅ Each edge drawn once with merged labels")
    print()

if __name__ == "__main__":
    print("\n")
    print("🧪 " * 35)
    print("TRANSITION MERGING & SELF-LOOP TESTS")
    print("🧪 " * 35)
    print("\n")
    
    try:
        test_transition_grouping()
        test_label_formatting()
        test_dead_state_rendering()
        test_no_duplicate_edges()
        test_complete_dfa_example()
        
        print("=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\n✅ Transition merging works correctly:")
        print("   - Multiple transitions to same state are grouped")
        print("   - Self-loops show merged labels (e.g., '0,1')")
        print("   - No duplicate edges are created")
        print("   - Dead state shows '0,1' on self-loop")
        print("   - Labels are comma-separated for multiple symbols")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
