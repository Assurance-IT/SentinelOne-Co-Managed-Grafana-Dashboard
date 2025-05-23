from ..config import S1_XDR_URL, XDR_HEADER
from ..sentinelone_client import fetch_json
from dataclasses import dataclass

@dataclass
class Login_class():
    status: str
    email: str
    ip: str

async def get_logins(cursor=None, accumulated_logins=None):

    if accumulated_logins is None:
        accumulated_logins = []

    params = {
        "queryType":"log",
        "filter":"dataSource.name='Microsoft O365' AND event.type='Logon'",
    }

    if cursor is not None:
        params["continuationToken"] = cursor 
    
    status, data = await fetch_json(
        "GET",
        f"{S1_XDR_URL}/api/query",
        params=params
    )

    for test in data["matches"]:
        attributes = test["attributes"]
        status = attributes.get("status_detail")
        email = attributes.get("actor.user.email_addr")
        ip = attributes.get("src_endpoint.ip")

        if email != None:  
            accumulated_logins.append(
            Login_class(
                status=status,
                email=email,
                ip=ip
            )
        )

    cursor = data.get("continuationToken")
    if cursor:
        return await get_logins(cursor, accumulated_logins)
    return accumulated_logins