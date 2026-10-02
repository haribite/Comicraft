from pathlib import Path
import uuid
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.models import ComicRequest
from app.gemini import generate_panels
from app.images import make_image
from app.pdf import make_pdf

Path("static/panels").mkdir(parents=True,exist_ok=True)
Path("static/exports").mkdir(parents=True,exist_ok=True)

app=FastAPI(title="ComicCraft")
app.mount("/static",StaticFiles(directory="static"),name="static")
templates=Jinja2Templates(directory="templates")

@app.get("/",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(request,"index.html",{"error":None})

@app.post("/generate",response_class=HTMLResponse)
def generate(request:Request,prompt:str=Form(...),character_name:str=Form(...),setting:str=Form(...),tone:str=Form(...),art_style:str=Form(...)):
    try:
        req=ComicRequest(prompt=prompt,character_name=character_name,setting=setting,tone=tone,art_style=art_style)
        panels=generate_panels(req)
        job=uuid.uuid4().hex
        result=[]
        for p in panels:
            d=p.model_dump()
            d["image_url"]=make_image(p,job,"static/panels")
            result.append(d)
        comic={"title":f"{req.character_name} — ComicCraft","panels":result}
        comic["pdf_url"]=make_pdf(comic,"static/exports")
        return templates.TemplateResponse(request,"comic.html",{"comic":comic,"error":None})
    except Exception as e:
        return templates.TemplateResponse(request,"index.html",{"error":str(e)},status_code=500)

@app.get("/health")
def health(): return {"status":"ok"}
