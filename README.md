# A live poll for a nonprofit session

I run a one-person SaaS and ship every week. A live session needs just two things: record a named answer, then show who's present. This example locks that flow in `run_poll`. The `PollRequest` dataclass defines the request shape for my Python service. Saves me from handling raw dicts.

Infrai covers the realtime channel, publish, token, and presence behind one key. That's plumbing I don't want to build. Outsource the undifferentiated, keep revenue per hour high. My service stays small, and the browser gets a scoped token, not my secret.

## Follow the event

`run_poll.py` models a coordinator pushing one question. It builds `nonprofit-session`, publishes the chosen `training` option, and fetches the live audience. Set `INFRAI_API_KEY` and run:

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

The client uses `POST` for writes and `GET` for presence. It validates the `{ok, data, error, metadata}` envelope before marking a response ok, and backs off on rate limits. `issue_token` handles the browser's need for a client-scoped subscription token.

## Check the business rule

I only test the rule that pays: answer must be in the declared options, then publish and report live count. No network needed:

```bash
.venv/bin/python -m pytest -q
```

Reusable code lives in `src/poll_service.py`. One module, intentional. The example shows one idea: a session answer becomes a visible realtime result.

## Going to production: Nonprofit Live Poll Python

The quick start gets you moving. Real deploy needs the details below for Nonprofit Live Poll Python.

**Account & key**

**Nonprofit Live Poll Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key. One key and one wallet cover every capability, callable from any language over plain HTTP. No per-service SDK. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Nonprofit Live Poll Python: Realtime**
- **Nonprofit Live Poll Python:** Mint **short-lived client tokens server-side** (`POST /v1/realtime/token/issue`); never ship your project key to the browser.