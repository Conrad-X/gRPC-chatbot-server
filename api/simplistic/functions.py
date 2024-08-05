import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def post_leave(args):
    url = os.environ["LEAVE_REQUEST_API"]

    request_payload = {
        "id": -1,
        "memberAttendanceTermUuid": f"{os.environ["MEMBER_ID"]}",
        "type": "",
        "reason": "",
        "closingNote": "",
        "startDate": "",
        "endDate": "",
        "duration": 0,
        "status": "",
        "note": "",
        "weekend": False,
        "publicHoliday": False,
        "forked": False,
    }

    headers = {
        "Authorization": f"{os.environ["AUTH_TOKEN"]}"
    }

    request_payload["type"] = args["type"]
    request_payload["reason"] = args["reason"]
    request_payload["startDate"] = args["start-date"]
    request_payload["endDate"] = args["end-date"]
    request_payload["duration"] = args["duration"]
    response = requests.post(url, json=request_payload, headers=headers)
    return response.status_code
