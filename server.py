"""FastAPI server: auth, chat persistence, SSE streaming."""
import json
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

from claude_agent_sdk import AssistantMessage, TextBlock, ToolUseBlock, ResultMessage
from agents.orchestrator import build_client
import db
import auth

load_dotenv()
if not os.getenv("ANTHROPIC_API_KEY"):
    raise RuntimeError("ANTHROPIC_API_KEY missing — set it in .env or the environment.")

SESSION_SECRET = os.getenv("SESSION_SECRET")
if not SESSION_SECRET:
    secret_file = Path(__file__).resolve().parent / "data" / ".session_secret"
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    if secret_file.exists():
        SESSION_SECRET = secret_file.read_text().strip()
    else:
        SESSION_SECRET = secrets.token_urlsafe(48)
        secret_file.write_text(SESSION_SECRET)

ROOT = Path(__file__).resolve().parent
db.init()

app = FastAPI(title="Nyāya — Indian Legal AI")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    max_age=60 * 60 * 24 * 30,
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


# ---------- Models ----------
class SignupReq(BaseModel):
    email: str
    password: str


class LoginReq(BaseModel):
    email: str
    password: str


class ChatRequest(BaseModel):
    message: str
    chat_id: int | None = None


# ---------- Pages ----------
@app.get("/")
async def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/welcome")
async def landing():
    return FileResponse(ROOT / "static" / "landing.html")


@app.get("/login")
async def login_page():
    return FileResponse(ROOT / "static" / "login.html")


@app.get("/api/health")
async def health():
    return {"ok": True}


# ---------- Auth ----------
@app.post("/api/auth/signup")
async def signup(req: SignupReq, request: Request):
    email = auth.validate_email(req.email)
    pw = auth.validate_password(req.password)
    if db.get_user_by_email(email):
        raise HTTPException(409, "Email already registered")
    uid = db.create_user(email, auth.hash_password(pw))
    request.session["uid"] = uid
    return {"id": uid, "email": email}


@app.post("/api/auth/login")
async def login(req: LoginReq, request: Request):
    email = auth.validate_email(req.email)
    user = db.get_user_by_email(email)
    if not user or not auth.verify_password(req.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    request.session["uid"] = user["id"]
    return {"id": user["id"], "email": user["email"]}


@app.post("/api/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@app.get("/api/auth/me")
async def me(uid: int = Depends(auth.current_user_id)):
    u = db.get_user(uid)
    if not u:
        raise HTTPException(401, "Not authenticated")
    return {"id": u["id"], "email": u["email"]}


# ---------- Chats ----------
@app.get("/api/chats")
async def get_chats(uid: int = Depends(auth.current_user_id)):
    return {"chats": db.list_chats(uid)}


@app.get("/api/chats/{chat_id}")
async def get_chat(chat_id: int, uid: int = Depends(auth.current_user_id)):
    chat = db.get_chat(uid, chat_id)
    if not chat:
        raise HTTPException(404, "Chat not found")
    return {
        "id": chat["id"],
        "title": chat["title"],
        "messages": db.list_messages(chat_id),
    }


@app.delete("/api/chats/{chat_id}")
async def del_chat(chat_id: int, uid: int = Depends(auth.current_user_id)):
    if not db.delete_chat(uid, chat_id):
        raise HTTPException(404, "Chat not found")
    return {"ok": True}


# ---------- Chat (SSE streaming + persistence) ----------
def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request,
               uid: int = Depends(auth.current_user_id)):

    # Get or create chat
    chat_id = req.chat_id
    if chat_id is not None:
        if not db.get_chat(uid, chat_id):
            raise HTTPException(404, "Chat not found")
    else:
        title = req.message.strip().splitlines()[0][:80] or "New chat"
        chat_id = db.create_chat(uid, title)

    # Persist user message immediately
    db.add_message(chat_id, "user", req.message)

    async def stream():
        # tell the client which chat this stream belongs to
        yield sse("chat", {"chat_id": chat_id})
        full_text_parts = []
        agents_used = []
        cost_usd = None
        duration_ms = None
        try:
            async with build_client() as client:
                await client.query(req.message)
                async for msg in client.receive_response():
                    if isinstance(msg, AssistantMessage):
                        for block in msg.content:
                            if isinstance(block, TextBlock):
                                full_text_parts.append(block.text)
                                yield sse("text", {"text": block.text})
                            elif isinstance(block, ToolUseBlock):
                                if block.name == "Task" and isinstance(block.input, dict):
                                    sub = block.input.get("subagent_type")
                                    if sub and sub not in agents_used:
                                        agents_used.append(sub)
                                yield sse("tool", {"name": block.name, "input": block.input})
                    elif isinstance(msg, ResultMessage):
                        cost_usd = getattr(msg, "total_cost_usd", None)
                        duration_ms = getattr(msg, "duration_ms", None)
                        yield sse("done", {
                            "duration_ms": duration_ms,
                            "cost_usd": cost_usd,
                        })
        except Exception as e:
            yield sse("error", {"message": str(e)})
        finally:
            full_text = "".join(full_text_parts).strip()
            if full_text:
                db.add_message(
                    chat_id, "assistant", full_text,
                    agents=",".join(agents_used) if agents_used else None,
                    cost_usd=cost_usd, duration_ms=duration_ms,
                )
                db.touch_chat(chat_id)

    return StreamingResponse(stream(), media_type="text/event-stream")
