# TokenLens Core

Local JSON Schema validation, provider adapters and SQLite metadata storage.
Requires Python 3.11+. Install with `pip install .`.

The wheel and source distribution contain only the core. The optional dashboard,
launchers and machine-specific data are not part of this package.

`tokenlens validate` reads one normalized JSON event from stdin.
`tokenlens ingest --db telemetry/tokenlens.sqlite3` validates before storing.
Raw transcripts must never be supplied to these commands.

Unsupported data stays null. All objects reject additional fields and model names
use a public allowlist. This is a technical boundary, not a proof of universal
anonymity: numeric usage metadata can still reveal work patterns.
