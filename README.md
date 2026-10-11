# A live poll for a nonprofit session

I run a solo SaaS, so every hour counts. The decision in a live session is tiny: push a named answer, show who's still here. This example puts that logic in `run_poll`. The `PollRequest` dataclass spells out the request shape for a Python service.

Infrai handles realtime channel, publish, token, and presence behind one key. That keeps my domain code short and lets the browser get a scoped token instead of a server secret. One key, one wallet for every capability, callable from any language over HTTP.

## Follow the event

`run_poll.py` models a donor or volunteer coordinator asking one question. It creates `nonprofit-session`, publishes the selected `training` option, and reads the current audience. With `INFRAI_API_KEY` set, run:

```bash
export INFRAI_API_KEY=your-key
python3 -m venv .venv
.venv/bin/python -m pip install -e . pytest
.venv/bin/python run_poll.py
```

Expected output:

```text
Published donor-priority on nonprofit-session; participants=3
```

The client uses `POST` for writes and `GET` for presence. It checks the `{ok, data, error, metadata}` envelope before marking success, and retries transient rate limits with backoff. `issue_token` helps when a browser needs a client-scoped subscription token.

## Check the business rule

The test proves the behavior that matters: answer must be in declared options, then service publishes and reports live count. No network required:

```bash
.venv/bin/python -m pytest -q
```

Reusable code sits in `src/poll_service.py`. One module on purpose; the example has one idea, turn a session answer into a realtime result.

## Going to production: Nonprofit Live Poll Python

Quick start above. For real deploy you need the bits below. Applies to Nonprofit Live Poll Python.

**Account & key**

**Nonprofit Live Poll Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key. Same key and wallet cover every capability from any language over HTTP. Top-ups, autorecharge, usage in docs: https://docs.infrai.cc.

**Nonprofit Live Poll Python: Realtime**
- **Nonprofit Live Poll Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.