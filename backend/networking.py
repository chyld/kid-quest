from fastapi import HTTPException
from pydantic import BaseModel
import subprocess

class NetworkingState(BaseModel):
    state: str

async def control_networking(networking_state: NetworkingState):
    command = []
    if networking_state.state == "on":
        command = ["nmcli", "networking", "on"]
    elif networking_state.state == "off":
        command = ["nmcli", "networking", "off"]
    else:
        raise HTTPException(status_code=400, detail="Invalid state. Must be 'on' or 'off'.")

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {"message": f"Networking turned {networking_state.state} successfully.", "output": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
