# Agent Instructions

Always read and follow:

- `docs/agent_usage_instructions.md`

Note: the `docs/` folder was copied from the bundled Kigumi docs at project initialization
time and may be out of date. The kumiki library installed in `.venv` ships its own docs.
To check for a more recent version, resolve the library path:

  .venv/bin/python3 -c "import kumiki, pathlib; print(pathlib.Path(kumiki.__file__).resolve().parent)"
  (Windows: .venv\Scripts\python.exe)

Then read `<that_path>/docs/agent_usage_instructions.md` for the most up-to-date instructions.

---

## Project Workflow Rules

### 1. Conversation & Design Log (`<structure_name>_conversation_log.md`)
For any design/structure worked on (e.g., `<structure_name>.py`), maintain a companion markdown log file `<structure_name>_conversation_log.md` in the project root:

1. **Header Metadata**:
   - `Session Started`: Timestamp of session start (with timezone).
   - `Agent Harness`: Agent environment/harness being used (e.g. Antigravity, Claude Code, Cursor, Copilot, etc.).
   - `Model`: LLM model name being used (e.g. Gemini 3.7 Flash, Claude 3.7 Sonnet, etc.).
   - If the user switches harness/model or begins a new session, record a new header/session entry.

2. **Entry Structure**:
   - **Prompts are emphasized**: Format user queries prominently using numbered section headers and bold blockquotes.
   - **No assistant response dumping**: DO NOT copy full assistant responses into the log.
   - **Super brief change summaries**: Underneath each prompt, provide only concise bullet points of what got created, added, or modified, formatted in small text (`<small>...</small>`).
