# Dead State - Quick Reference

## 🔑 Key Constant
```javascript
const DEAD_STATE = 'qd';
```

---

## 🛠️ Core Functions

### 1. Initialize Dead State Transitions
```javascript
initializeDeadStateTransitions();
```
**When to call:**
- After alphabet changes
- After DFA generation
- When dead state is added

**What it does:**
- Sets `δ(qd, symbol) = qd` for all symbols

---

### 2. Fill Undefined Transitions
```javascript
fillUndefinedTransitions();
```
**When to call:**
- Before validation
- Before simulation
- When user requests complete DFA

**What it does:**
- Fills missing transitions with `qd`
- Skips dead state itself
- Ensures complete DFA

---

## 📍 Integration Points

### In `generateStates()`:
```javascript
// Add dead state
if (!currentDFA.states.includes(DEAD_STATE)) {
    currentDFA.states.push(DEAD_STATE);
}

// Initialize if alphabet exists
if (currentDFA.alphabet && currentDFA.alphabet.length > 0) {
    initializeDeadStateTransitions();
}
```

### In `updateAlphabet()`:
```javascript
// After resetting transitions
initializeDeadStateTransitions();
```

### In `validateCurrentDFA()`:
```javascript
// Before sending to backend
fillUndefinedTransitions();
initializeDeadStateTransitions();
updateTransitionTable();
updateFullTransitionTable();
```

### In `startSimulation()`:
```javascript
// Before sending to backend
fillUndefinedTransitions();
initializeDeadStateTransitions();
updateTransitionTable();
updateFullTransitionTable();
```

---

## 🎨 UI Styling

### Dead State Detection:
```javascript
const isDeadState = state === DEAD_STATE || 
                    state === 'q_reject' || 
                    state.toLowerCase().includes('reject') || 
                    state.toLowerCase().includes('dead');
```

### Visual Indicators:
- **Color:** `#ef4444` (red)
- **Background:** `#fee2e2` or `#fef2f2` (light red)
- **Font:** Bold
- **Label:** "(Dead State)"

---

## ⚠️ Constraints

1. **Dead state CANNOT be renamed**
   - Input field is disabled
   - Validation prevents renaming to "qd"

2. **Dead state CANNOT be final**
   - Excluded from final states checkboxes
   - Never added to `currentDFA.finals`

3. **Dead state CANNOT be deleted**
   - Automatically re-added if missing
   - Always present in state list

---

## 🔄 Complete DFA Example

**Input:**
```
States: q0, q1, qd
Alphabet: a, b
User defines: δ(q0, a) = q1
```

**After `fillUndefinedTransitions()`:**
```
δ(q0, a) = q1     ✓ User-defined
δ(q0, b) = qd     ← Auto-filled
δ(q1, a) = qd     ← Auto-filled
δ(q1, b) = qd     ← Auto-filled
δ(qd, a) = qd     ✓ Dead state loop
δ(qd, b) = qd     ✓ Dead state loop
```

---

## 🧪 Testing

Run tests:
```bash
python test_dead_state.py          # Starts-with mode
python test_dead_state_custom.py   # Custom mode
```

Expected: All tests pass ✅

---

## 📋 Checklist

When modifying DFA initialization:
- [ ] Dead state added to `currentDFA.states`
- [ ] Dead state added to `currentDFA.transitions`
- [ ] Dead state transitions initialized
- [ ] Dead state excluded from finals
- [ ] UI updated with dead state styling
- [ ] Dropdowns include dead state option
- [ ] Undefined transitions fill to dead state

---

**Quick Debug:**
```javascript
console.log('States:', currentDFA.states);
console.log('Has dead state:', currentDFA.states.includes(DEAD_STATE));
console.log('Dead state transitions:', currentDFA.transitions[DEAD_STATE]);
```
