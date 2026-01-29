You must follow ALL rules in `.windsurf/rules/*`.

Act as a **Senior AI Engineer specialized in deterministic AI systems**.

## Objective
Design the AI Graph (LangGraph or equivalent) before any implementation.

## Tasks
1. Describe the **role of the AI** in the system (explicit boundaries).
2. Define the **graph nodes** (no code yet):
   - Input normalization
   - Audio transcription
   - Intent classification
   - Entity extraction
   - Validation gate
   - Confirmation gate
   - Tool execution
   - Response generation
   - Audit logging
3. For each node, describe:
   - Input
   - Output
   - Failure modes
   - Stop conditions
4. Define **graph state schema** (what lives in Redis vs DB).
5. Identify **hallucination risk points** and how the graph blocks them.
6. List **open questions**.

## Constraints
- No code
- No provider calls
- No assumptions without documentation

## Stop Condition
End by asking:
> “AI Graph design complete. Should I proceed to implementation skeleton?”
