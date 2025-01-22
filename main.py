from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import os

app = FastAPI()

# Define the input schema
class ServiceInstance(BaseModel):
    serviceId: str
    instances: int

# Define the endpoint
@app.post("/set-instances")
async def set_instances(services: List[ServiceInstance]):
    render_api_url = "https://api.render.com/v1/services/{service_id}/instances"
    render_api_key = os.getenv("RENDER_API_KEY")  # Get the Render API key from environment variables

    if not render_api_key:
        raise HTTPException(status_code=500, detail="Render API key not configured")

    headers = {
        "Authorization": f"Bearer {render_api_key}",
        "Content-Type": "application/json",
    }

    results = []

    for service in services:
        try:
            # Prepare API endpoint and payload
            url = render_api_url.format(service_id=service.serviceId)
            payload = {"numInstances": service.instances}

            # Make the request to Render API
            response = requests.put(url, json=payload, headers=headers)

            # Check the response status
            if response.status_code == 200:
                results.append({"serviceId": service.serviceId, "status": "success"})
            else:
                results.append({
                    "serviceId": service.serviceId,
                    "status": "failure",
                    "error": response.json(),
                })
        except Exception as e:
            results.append({
                "serviceId": service.serviceId,
                "status": "error",
                "error": str(e),
            })

    return {"results": results}
