# IRIS AI Orchestration — Graph Design

## 1. Role of the AI

The AI is a **financial operations assistant** embedded in IRIS.

### Responsibilities
- Understand user intent from text/audio
- Extract structured entities (contact, amount, date)
- Explain financial state clearly
- Request explicit confirmation for monetary actions
- Call deterministic use cases only
- Never make financial decisions autonomously

### Explicit Boundaries
| Allowed | Forbidden |
|---------|-----------|
| Classify intent | Write to database |
| Extract entities | Decide monetary values |
| Ask clarification | Invent IDs or dates |
| Request confirmation | Execute without confirmation |
| Call approved tools | Bypass validation gates |
| Explain results | Access raw SQL |

---

## 2. Graph Nodes

### Node 1: Input Normalization
- **Purpose**: Normalize user input (text/audio) to standard format
- **Input**: Raw user message (text or audio reference)
- **Output**: Normalized text string
- **Failure modes**: Invalid input type, empty message
- **Stop condition**: If input is empty or malformed → respond with clarification request

### Node 2: Audio Transcription (conditional)
- **Purpose**: Convert audio to text via external service
- **Input**: Audio file reference
- **Output**: Transcribed text
- **Failure modes**: Transcription failure, unsupported format
- **Stop condition**: If transcription fails → ask user to retry

### Node 3: Intent Classification
- **Purpose**: Classify user intent into predefined categories
- **Input**: Normalized text
- **Output**: Intent enum + confidence score
- **Failure modes**: Low confidence, unknown intent
- **Stop condition**: If confidence < 0.7 → ask clarification

### Allowed Intents
- CREATE_BOLETO
- CANCEL_BOLETO
- CHECK_STATUS
- SEND_MESSAGE
- LIST_BOLETOS
- GENERAL_QUESTION
- UNKNOWN

### Node 4: Entity Extraction
- **Purpose**: Extract structured entities from text
- **Input**: Normalized text + intent
- **Output**: Extracted entities (contact, amount, date, etc.)
- **Failure modes**: Missing required entities, ambiguous values
- **Stop condition**: If required entity missing → ask for it

### Node 5: Validation Gate
- **Purpose**: Ensure all required entities are present and valid
- **Input**: Intent + extracted entities
- **Output**: Validation result (pass/fail/clarify)
- **Failure modes**: Missing fields, invalid formats
- **Stop condition**: If validation fails → ask clarification

### Node 6: Confirmation Gate
- **Purpose**: Request explicit user confirmation for monetary actions
- **Input**: Validated intent + entities
- **Output**: Confirmation status (pending/confirmed/rejected)
- **Failure modes**: User rejects, timeout
- **Stop condition**: If not confirmed → do not execute

### Node 7: Tool Execution
- **Purpose**: Call approved use case with validated parameters
- **Input**: Confirmed intent + entities
- **Output**: Use case result
- **Failure modes**: Use case exception, provider error
- **Stop condition**: If tool fails → explain error to user

### Node 8: Response Generation
- **Purpose**: Generate human-readable response
- **Input**: Tool result or error
- **Output**: User-facing message
- **Failure modes**: None (deterministic formatting)
- **Stop condition**: Always succeeds

### Node 9: Audit Logging
- **Purpose**: Log AI decision for auditability
- **Input**: Full graph state
- **Output**: None (side effect: log entry)
- **Failure modes**: Log failure (non-blocking)
- **Stop condition**: Never blocks main flow

---

## 3. Graph Flow

```
START
  │
  ▼
[Input Normalization]
  │
  ├─ audio? ─► [Audio Transcription] ─┐
  │                                    │
  ▼◄──────────────────────────────────┘
[Intent Classification]
  │
  ├─ low confidence? ─► [Response: Ask Clarification] ─► END
  │
  ▼
[Entity Extraction]
  │
  ▼
[Validation Gate]
  │
  ├─ missing entities? ─► [Response: Ask for Missing] ─► END
  │
  ▼
[Confirmation Gate] ◄── (only for monetary actions)
  │
  ├─ not confirmed? ─► [Response: Action Cancelled] ─► END
  │
  ▼
[Tool Execution]
  │
  ├─ error? ─► [Response: Explain Error] ─► END
  │
  ▼
[Response Generation]
  │
  ▼
[Audit Logging]
  │
  ▼
END
```

---

## 4. Graph State Schema

### Ephemeral State (Redis)
- `conversation_id`: UUID
- `turn_count`: int
- `last_intent`: str
- `pending_confirmation`: dict | None
- `extracted_entities`: dict
- `awaiting_clarification`: bool

### Persistent State (PostgreSQL)
- Audit logs only
- No conversation storage unless explicitly required

### State Model
```python
class AIGraphState:
    conversation_id: str
    user_input: str
    normalized_input: str | None
    intent: str | None
    intent_confidence: float
    entities: dict[str, Any]
    validation_result: str  # pass | fail | clarify
    confirmation_status: str  # pending | confirmed | rejected | not_required
    tool_result: dict | None
    response: str | None
    error: str | None
```

---

## 5. Hallucination Risk Points

| Risk | Location | Mitigation |
|------|----------|------------|
| Invented amounts | Entity Extraction | Validation gate requires explicit amount |
| Invented dates | Entity Extraction | Date must be parseable, normalized |
| Invented contacts | Entity Extraction | Contact must exist in DB (tool checks) |
| Assumed confirmation | Confirmation Gate | Explicit YES required, never assumed |
| Invented IDs | Tool Execution | All IDs come from system, not LLM |
| Fabricated results | Response Generation | Response based only on tool output |

### Blocking Mechanisms
1. **Validation Gate**: Blocks if required entities missing
2. **Confirmation Gate**: Blocks monetary actions without explicit YES
3. **Tool Contracts**: Tools validate all inputs independently
4. **No Direct DB Access**: AI cannot query or write to DB

---

## 6. Open Questions

1. **Audio transcription**: Which provider? Gemini built-in or separate?
2. **Confidence threshold**: Is 0.7 appropriate for intent classification?
3. **Confirmation timeout**: How long to wait for user confirmation?
4. **Rate limiting**: Should AI requests be rate-limited per tenant?
5. **Multi-turn context**: How many turns to retain in Redis?

---

## 7. Tools Available

| Tool | Use Case | Requires Confirmation |
|------|----------|----------------------|
| `create_boleto` | CreateBoletoUseCase | YES |
| `cancel_boleto` | CancelBoletoUseCase | YES |
| `get_boleto_status` | GetBoletoStatusUseCase | NO |
| `queue_message` | QueueMessageUseCase | NO |

---

**AI Graph design complete. Proceeding to implementation skeleton.**
