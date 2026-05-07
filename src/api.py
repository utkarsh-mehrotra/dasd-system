import os
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from src.orchestrator import DASDOrchestrator

app = FastAPI(title="DASD API")

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StartRequest(BaseModel):
    global_goal: str
    mode: str = "socratic"

# Global state to hold the current conversation graph
# (In a real app, you'd map session IDs to orchestrators)
current_orchestrator = None
current_initial_state = None

@app.post("/start")
async def start_conversation(req: StartRequest):
    global current_orchestrator, current_initial_state
    
    current_orchestrator = DASDOrchestrator(global_goal=req.global_goal, mode=req.mode)
    current_initial_state = {
        "mode": req.mode,
        "global_goal": req.global_goal,
        "context": "",
        "latest_message": "Let's begin.",
        "sender": "system",
        "turn_count": 0,
        "history": []
    }
    return {"status": "initialized", "mode": req.mode}

async def event_generator():
    global current_orchestrator, current_initial_state
    
    if not current_orchestrator:
        yield {"event": "error", "data": json.dumps({"message": "No conversation initialized."})}
        return

    try:
        # We use .stream() to get incremental updates from LangGraph nodes
        # recursion_limit=100 as configured previously
        collected_messages = []
        for event in current_orchestrator.graph.stream(current_initial_state, {"recursion_limit": 100}):
            # event is typically a dict mapping node_name -> state_updates
            for node_name, state_update in event.items():
                if node_name == "router_node":
                    continue # Skip pass-through
                
                # Format payload for frontend
                sender = state_update.get("sender", "system")
                message = state_update.get("latest_message", "")
                turn = state_update.get("turn_count", 0)
                
                collected_messages.append({"sender": sender, "message": message, "turn": turn})
                
                payload = {
                    "node": node_name,
                    "sender": sender,
                    "message": message,
                    "turn": turn
                }
                
                yield {
                    "event": "message",
                    "data": json.dumps(payload)
                }
                
                # Small sleep to allow frontend to render smoothly
                await asyncio.sleep(0.5)
                
        # Save transcript at the end
        import time
        filename = f"session_{int(time.time())}.md"
        filepath = os.path.join("assets", "transcripts", filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w") as f:
            f.write(f"# DASD Synthesis\n\n**Goal:** {current_initial_state['global_goal']}\n**Mode:** {current_initial_state['mode']}\n\n---\n\n")
            for msg in collected_messages:
                f.write(f"### {msg['sender'].upper()} (Turn {msg['turn']})\n{msg['message']}\n\n---\n\n")

        yield {
            "event": "done",
            "data": json.dumps({"message": "Conversation Complete"})
        }
    except Exception as e:
        yield {
            "event": "error",
            "data": json.dumps({"message": str(e)})
        }

@app.get("/stream")
async def stream_conversation(request: Request):
    return EventSourceResponse(event_generator())

@app.get("/history")
async def get_history():
    history_dir = os.path.join("assets", "transcripts")
    os.makedirs(history_dir, exist_ok=True)
    files = [f for f in os.listdir(history_dir) if f.endswith(".md")]
    files.sort(reverse=True)
    return {"transcripts": files}

@app.get("/history/{filename}")
async def get_transcript(filename: str):
    filepath = os.path.join("assets", "transcripts", filename)
    if not os.path.exists(filepath):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Transcript not found")
    with open(filepath, "r") as f:
        return {"content": f.read()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=8000, reload=True)
