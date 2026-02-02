from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.llm import generate_answer
from app.pdf_utils import extract_pdf_text
from app.storage import init_db, list_documents, search_documents, store_document

app = FastAPI(title="Research PDF Agent", version="0.2.0")
templates = Jinja2Templates(directory="app/templates")


class ChatRequest(BaseModel):
    question: str
    top_k: int = 5


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/documents/upload")
async def upload_documents(files: list[UploadFile] = File(...)) -> JSONResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    stored = []
    for upload in files:
        if not upload.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Unsupported file: {upload.filename}")
        content = await upload.read()
        text, page_count = extract_pdf_text(content)
        doc_id = store_document(upload.filename, content, page_count, text)
        stored.append({"id": doc_id, "filename": upload.filename, "pages": page_count})

    return JSONResponse({"stored": stored})


@app.get("/documents")
def get_documents() -> JSONResponse:
    docs = [dict(row) for row in list_documents()]
    return JSONResponse({"documents": docs})


@app.post("/chat")
def chat(request: ChatRequest) -> JSONResponse:
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")
    results = search_documents(request.question, limit=request.top_k)
    context = [(row[0], row[1], row[2]) for row in results]
    answer = generate_answer(request.question, context)
    return JSONResponse({"answer": answer, "matches": context})
