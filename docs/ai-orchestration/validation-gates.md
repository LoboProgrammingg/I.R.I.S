# IRIS AI Orchestration — Validation Gates

## Purpose

Validation gates are **deterministic checkpoints** in the AI graph that:
- Block execution if requirements are not met
- Ask for clarification when data is ambiguous
- Prevent hallucination by requiring explicit values
- Enforce business rules before tool execution

---

## Gate 1: Input Validation

### Location
`app/ai/nodes/input_normalization.py`

### Rules
| Rule | Threshold | Action |
|------|-----------|--------|
| Empty input | len == 0 | Ask clarification |
| Whitespace only | strip() == "" | Ask clarification |
| Audio transcription failure | None result | Ask retry |

### What It Prevents
- Processing empty messages
- Wasting resources on invalid input
- Proceeding with failed transcriptions

---

## Gate 2: Intent Confidence

### Location
`app/ai/nodes/intent_classification.py`

### Rules
| Rule | Threshold | Action |
|------|-----------|--------|
| Low confidence | < 0.7 | Ask clarification |
| Unknown intent | UNKNOWN | Ask clarification |

### What It Prevents
- Acting on uncertain classifications
- Executing wrong operations
- Hallucinating user intent

---

## Gate 3: Entity Validation

### Location
`app/ai/nodes/validation_gate.py`

### Required Entities by Intent

| Intent | Required Entities |
|--------|------------------|
| CREATE_BOLETO | contact_name, amount_cents, due_date |
| CANCEL_BOLETO | boleto_id |
| CHECK_STATUS | boleto_id |
| SEND_MESSAGE | contact_name, message_content |
| LIST_BOLETOS | (none) |
| GENERAL_QUESTION | (none) |

### Value Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| amount_cents | > 0 | "O valor precisa ser positivo." |
| amount_cents | <= 10000000 | "O valor máximo permitido é R$ 100.000,00." |
| due_date | >= today | "A data de vencimento não pode ser no passado." |
| due_date | valid format | "Data de vencimento inválida." |

### What It Prevents
- Missing required data
- Invalid monetary values
- Past due dates
- Malformed dates

---

## Gate 4: Confirmation Gate

### Location
`app/ai/nodes/confirmation_gate.py`

### Rules
| Intent | Requires Confirmation |
|--------|-----------------------|
| CREATE_BOLETO | **YES** |
| CANCEL_BOLETO | **YES** |
| CHECK_STATUS | NO |
| SEND_MESSAGE | NO |
| LIST_BOLETOS | NO |

### Confirmation Detection
| User Says | Interpretation |
|-----------|----------------|
| "sim", "confirmo", "pode", "ok" | CONFIRMED |
| "não", "cancela", "pare" | REJECTED |
| (anything else) | PENDING |

### What It Prevents
- Accidental boleto creation
- Unintended cancellations
- Money movement without explicit consent

---

## Gate 5: Tool Execution Guards

### Location
`app/ai/nodes/tool_execution.py`

### Pre-Execution Checks
1. `validation_result == PASS`
2. `confirmation_status == CONFIRMED` (for monetary actions)
3. `intent != UNKNOWN`

### What It Prevents
- Executing with invalid data
- Executing without confirmation
- Executing unknown operations

---

## Hallucination Prevention Matrix

| Risk | Gate | Mitigation |
|------|------|------------|
| Invented amount | Entity Validation | Must extract explicit number |
| Invented date | Entity Validation | Must parse valid date |
| Invented contact | Tool Execution | Contact must exist in DB |
| Assumed confirmation | Confirmation Gate | Explicit YES required |
| Invented boleto ID | Tool Execution | ID must exist in DB |
| Fabricated result | Response Generation | Based only on tool output |

---

## Flow Diagram with Gates

```
INPUT
  │
  ▼
┌─────────────────────┐
│ GATE 1: Input Valid │─── FAIL ──► "Não entendi. Pode repetir?"
└─────────┬───────────┘
          │ PASS
          ▼
┌─────────────────────┐
│ GATE 2: Intent      │─── LOW CONFIDENCE ──► "O que você deseja?"
│         Confidence  │
└─────────┬───────────┘
          │ PASS
          ▼
┌─────────────────────┐
│ GATE 3: Entity      │─── MISSING ──► "Preciso saber: [campo]"
│         Validation  │
└─────────┬───────────┘
          │ PASS
          ▼
┌─────────────────────┐
│ GATE 4: Confirmation│─── PENDING ──► "Confirma? (Sim/Não)"
│         (if needed) │─── REJECTED ──► "Operação cancelada."
└─────────┬───────────┘
          │ CONFIRMED / NOT_REQUIRED
          ▼
┌─────────────────────┐
│ GATE 5: Tool Checks │─── FAIL ──► (blocked silently)
└─────────┬───────────┘
          │ PASS
          ▼
      TOOL EXECUTION
          │
          ▼
      RESPONSE
```

---

## Implementation Notes

### Determinism
All gates use deterministic rules:
- No probabilistic decisions after intent classification
- No heuristics without explicit thresholds
- No silent passes - every gate has explicit pass/fail

### Auditability
All gate decisions are logged:
- `validation_gate_pass` / `validation_gate_fail`
- `confirmation_pending` / `confirmation_confirmed` / `confirmation_rejected`
- `tool_execution_blocked` / `tool_execution_success`

### No Bypass
Gates cannot be bypassed:
- Graph nodes execute in strict order
- Each node checks if it should stop
- `should_stop()` method enforces flow control

---

## Open Questions

1. Should we allow partial confirmation (e.g., "criar boleto de 100 reais sim")?
2. Should we add rate limiting as a gate?
3. Should we add tenant-specific validation rules?
