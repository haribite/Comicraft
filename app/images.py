from pathlib import Path
from PIL import Image, ImageDraw
import re

def make_image(panel, job, outdir):
    outdir=Path(outdir); outdir.mkdir(parents=True, exist_ok=True)
    path=outdir/f"{job}_{panel.panel_number}.png"
    im=Image.new("RGB",(900,600),(244,239,250))
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((15,15,885,585),radius=30,outline=(100,70,150),width=6)
    d.text((45,45),f"COMICCRAFT — PANEL {panel.panel_number}",fill=(60,40,90))
    d.text((45,100),panel.title[:80],fill=(30,25,40))
    words=panel.scene_description.split()
    line=""; y=170
    for w in words:
        test=(line+" "+w).strip()
        if len(test)>65:
            d.text((45,y),line,fill=(50,45,60)); y+=35; line=w
        else: line=test
    if line: d.text((45,y),line,fill=(50,45,60))
    d.text((45,520),"Test artwork mode — no image model required.",fill=(90,70,120))
    im.save(path)
    return "/static/panels/"+path.name
