# Agent Instructions

Always read and follow:

- docs/agent_usage_instructions.md

Note: the `docs/` folder was copied from the bundled Kigumi docs at project initialization
time and may be out of date. The kumiki library installed in `.venv` ships its own docs.
To check for a more recent version, resolve the library path:

  .venv/bin/python3 -c "import kumiki, pathlib; print(pathlib.Path(kumiki.__file__).resolve().parent)"
  (Windows: .venv\Scripts\python.exe)

Then read `<that_path>/docs/agent_usage_instructions.md` for the most up-to-date instructions.
