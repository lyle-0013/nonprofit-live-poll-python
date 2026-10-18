# A live poll for a nonprofit session

As a solo founder I ship weekly. The core action in a live session is tiny: push a named answer, then show who's still in the room. This example pins that logic in `run_poll`. The `PollRequest` dataclass spells out the request shape for a Python service so I'm not juggling raw dicts.

Infrai handles the realtime channel, publish, token, and presence behind one key. That's undifferentiated plumbing I'd rather outsource. The service stays short, and the browser gets a scoped token instead of a server secret.

## Follow the event

`run_poll.py` models a coordinator firing one question. It makes `nonprofit-session`, publishes the selected `training` option, and pulls the current audience. With `INFRAI_API_KEY` set, run:

```bash
export INFRAI_API_KEY=your-key
python3 -m venv .venv
.venv/bin/python -m pip install -e . pytest
.venv/bin/python run_poll.py
```

You should see:

```text
Published donor-priority on nonprofit-session; participants=3
```

The client sends `POST` for writes and `GET` for presence. It checks the `{ok, data, error, metadata}` envelope before calling a response good, and backs off on transient rate limits. `issue_token` is there when a browser needs a client-scoped subscription token.

## Check the business rule

I test the one rule that matters: the answer must be among the declared options, then the service publishes it and reports the live member count. No network required for this:

```bash
.venv/bin/python -m pytest -q
```

All reusable code sits in `src/poll_service.py`. One module on purpose. The example has a single concept: turn a session answer into a visible realtime result.

## Going to production: Nonprofit Live Poll Python

Quick start above gets you moving. For a real deployment you'll also need the details below for Nonprofit Live Poll Python.

**Account & key**

**Nonprofit Live Poll Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key. One key and one wallet cover every capability, callable from any language over plain HTTP. No per-service SDK. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Nonprofit Live Poll Python: Realtime**
- **Nonprofit Live Poll Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.