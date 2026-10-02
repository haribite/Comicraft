from pathlib import Path
from fpdf import FPDF

def make_pdf(comic, outdir):
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    path=outdir/"comiccraft_comic.pdf"
    pdf=FPDF("P","mm","A4")
    for p in comic["panels"]:
        pdf.add_page()
        pdf.set_font("Helvetica","B",18)
        pdf.multi_cell(0,10,f"Panel {p['panel_number']}: {p['title']}")
        img=Path(p["image_url"].lstrip("/"))
        if img.exists(): pdf.image(str(img),15,35,180)
        pdf.set_y(150); pdf.set_font("Helvetica","",11)
        for label,key in [("Scene", "scene_description"),("Caption","caption"),("Narration","narration"),("Dialogue","dialogue")]:
            value=p.get(key,"")
            if value: pdf.multi_cell(0,7,f"{label}: {value}".encode("latin-1","replace").decode("latin-1"))
            pdf.ln(1)
    pdf.output(str(path))
    return "/static/exports/comiccraft_comic.pdf"
