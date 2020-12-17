from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import enum, re

app = Flask(__name__)

current_meetings = {}

class Commands():
    R_START= r'^[a-z]+ start$'
    START = 'start'
    R_STOP = r'^[a-z]+ stop$'
    STOP = 'stop'
    R_HELP = r'^usage$'
    HELP = 'usage'
    R_MEETINGS = r'^meetings\?$'
    MEETINGS = 'meetings'
    R_INDV_MEETINGS = r'^[a-z]+\?$'
    INDV_MEETINGS = 'indv_meetings'
    UNKNOWN = 'unknown'

    @staticmethod
    def parse(command):
        print(f"checking [{command}]")
        if re.match(Commands.R_START, command):
            return Commands.START
        elif re.match(Commands.R_STOP, command):
            return Commands.STOP
        elif re.match(Commands.R_HELP, command):
            return Commands.HELP
        elif re.match(Commands.R_MEETINGS, command):
            return Commands.MEETINGS
        elif re.match(Commands.R_INDV_MEETINGS, command):
            return Commands.INDV_MEETINGS
        else:
            return Commands.UNKNOWN


USAGE = """Usage: <name> [start, stop]
    For example:
        YeetMaster start

    send `usage` for more info.
    """

HELP = """
Welcome! I can help you let people know if you're currently in a meeting.

Usage:
    `usage` displays this message
    `<name> start` will register a meeting for <name>.
    `<name> stop` will unregister a meeting for <name>.
    `<name>?` will reply for whether that user is in a meeting.
    `meetings?` will reply with known meetings.
"""

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    body = request.values.get('Body', None).lower()
    print(f"body={body}")
    resp = MessagingResponse()

    if Commands.parse(body) == Commands.START:
        person, action = body.split()
        if not current_meetings.get(person, None):
            current_meetings[person] = Commands.START
            resp.message(f"Hey {person}, you've started a meeting...")
        return str(resp)
    elif Commands.parse(body) == Commands.STOP:
        person, action = body.split()
        if current_meetings.get(person, None):
            del current_meetings[person]
            resp.message(f"Hey {person}, you've ended a meeting...")
        return str(resp)
    elif Commands.parse(body) == Commands.HELP:
        resp.message(HELP)
        return str(resp)
    elif Commands.parse(body) == Commands.INDV_MEETINGS:
        person = body[:-1]
        meeting = current_meetings.get(person, None)
        if not meeting:
            resp.message(
                f"{person} isn't in a meeting"
                f"\N{drooling face}"
            )
        else:
            resp.message(
                f"{person} is still in a meeting"
                f"\N{pensive face}"
            )
        return str(resp)
    elif Commands.parse(body) == Commands.MEETINGS:
        resp.message(
            f"{current_meetings.keys()} are in meetings "
            f"\N{grinning face with smiling eyes}"
        )
        return str(resp)
    else:  # Commands.UNKNOWN
        resp.message(USAGE)
        return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
