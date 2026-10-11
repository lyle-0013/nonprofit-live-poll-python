from poll_service import InfraiRealtime, PollRequest, run_poll


if __name__ == "__main__":
    poll = PollRequest(
        channel="nonprofit-session",
        event="donor-priority",
        account_id="demo-account",
        question="Which support should we fund next?",
        options=("meals", "training", "shelter"),
    )
    result = run_poll(InfraiRealtime(), poll, "training")
    print(f"Published {result.event} on {result.channel}; participants={result.participant_count}")
