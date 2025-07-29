from fastapi import HTTPException
from pydantic import BaseModel
import subprocess

class NetworkingState(BaseModel):
    state: str

async def control_networking(networking_state: NetworkingState):
    command = []
    if networking_state.state == "on":
        command = ["./chain.sh", "ON"]
    elif networking_state.state == "off":
        command = ["./chain.sh", "OFF"]
    else:
        raise HTTPException(status_code=400, detail="Invalid state. Must be 'on' or 'off'.")

    try:
        print("yo yo yo")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("RESult", result)
        return {"message": f"Networking turned {networking_state.state} successfully.", "output": result.stdout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
