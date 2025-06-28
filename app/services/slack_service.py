from app.utils.slack import send_slack_message

async def notify_channel_about_event(event_data: dict):
    event = event_data.get("event", {})
    user = event.get("user")
    text = event.get("text")
    channel = event.get("channel")
    ts = event.get("ts")

    if user and text:
        reply_text = (
            f":robot_face: Hey <@{user}>! I received your message:\n"
            f"> {text}\n\n"
            f"_If this message is related to a task or project, please reply with details!_"
        )

        return await send_slack_message(channel=channel, text=reply_text, thread_ts=ts)
