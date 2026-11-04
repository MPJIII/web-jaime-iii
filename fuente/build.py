#!/usr/bin/env python3
"""Genera la web de Inmobiliaria JAIME III a partir de inmuebles.json y plantilla.txt.

Uso: python3 build.py <carpeta_src> <salida.html>
Las fotos de cada inmueble se publican como gal2/<id>_<n>.jpg (n desde 0).
"""
import base64, html, json, sys, os, datetime

src = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
out = sys.argv[2] if len(sys.argv) > 2 else "jaime-iii-web.html"

data = json.load(open(os.path.join(src, "inmuebles.json"), encoding="utf-8"))
plantilla = open(os.path.join(src, "plantilla.txt"), encoding="utf-8").read()
logo = base64.b64encode(open(os.path.join(src, "logo.png"), "rb").read()).decode()

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def eur(n):
    return f"{int(n):,}".replace(",", ".") + " €"


def ficha(i, orden):
    e = html.escape
    alq = i["operacion"] == "alquiler"
    precio = eur(i["precio"]) + ("/mes" if alq else "")
    spec = [f'{int(i["m2"]):,}'.replace(",", ".") + " m²"]
    if i.get("hab"):
        spec.append(f'{i["hab"]} dorm.')
    if i.get("banos"):
        spec.append(f'{i["banos"]} baños' if i["banos"] > 1 else "1 baño")
    if i.get("extras"):
        spec.append(i["extras"])
    n = int(i.get("fotos") or 0)
    if n:
        imgs = f'<img src="gal2/{i["id"]}_0.jpg" alt="{e(i["titulo"])}" class="on">' + "".join(
            f'<img data-src="gal2/{i["id"]}_{k}.jpg" alt="">' for k in range(1, n))
        flechas = ('<button type="button" class="gal-flecha izq" aria-label="Foto anterior">‹</button>'
                   '<button type="button" class="gal-flecha der" aria-label="Foto siguiente">›</button>') if n > 1 else ""
        foto = f'<div class="ficha-foto galeria">{imgs}{flechas}<span class="contador-fotos" aria-hidden="true">1 / {n}</span>'
    else:
        foto = f'<div class="ficha-foto"><div class="sinfoto"><img src="data:image/png;base64,{logo}" alt=""></div>'
    if i.get("badge"):
        foto += f'<span class="badge">{e(i["badge"])}</span>'
    foto += "</div>"
    if i.get("origen") == "idealista":
        enlace = f'<a class="ver" href="https://www.idealista.com/inmueble/{i["id"]}/" target="_blank" rel="noopener">Ver anuncio ↗</a>'
    else:
        enlace = f'<a class="ver" href="#inmueble-{i["id"]}">Ver ficha →</a>'
    ref = i["id"] if i.get("origen") != "carpeta" else (i.get("ref") or i["id"])
    busca = " ".join([i["zona"], i["municipio"], i["titulo"], str(ref)]).lower()
    return f'''<article class="ficha" data-id="{i["id"]}" data-op="{i["operacion"]}" data-orden="{orden}" data-precio="{i["precio"]}" data-m2="{i["m2"]}" data-hab="{i.get("hab") or 0}" data-cat="{e(i["cat"])}" data-busca="{e(busca)}">
  {foto}
  <div class="ficha-txt">
    <p class="ficha-zona">{e(i["zona"].upper())} · {e(i["municipio"].upper())} · REF. {e(str(ref))}</p>
    <h3><a href="#inmueble-{i["id"]}">{e(i["titulo"])}</a></h3>
    <p class="ficha-spec">{e(" · ".join(spec))}</p>
    <div class="ficha-pie"><span class="ficha-precio">{precio}</span>{enlace}</div>
  </div>
</article>'''


items = [i for i in data["inmuebles"] if not i.get("oculto")]
fichas = "\n".join(ficha(i, k) for k, i in enumerate(items))
nv = sum(1 for i in items if i["operacion"] == "venta")
na = sum(1 for i in items if i["operacion"] == "alquiler")
f = datetime.date.fromisoformat(data.get("actualizado") or datetime.date.today().isoformat())
fecha = f"{f.day} de {MESES[f.month - 1]} de {f.year}"

CAMPOS = ["id", "operacion", "titulo", "zona", "municipio", "cat", "precio", "m2", "hab", "banos",
          "extras", "fotos", "origen", "ref", "descripcion", "caracteristicas", "ubicacion"]
datos = json.dumps([{k: i.get(k) for k in CAMPOS} for i in items], ensure_ascii=False).replace("</", "<\\/")
page = (plantilla.replace("<!--FICHAS-->", fichas).replace("<!--DATOS-->", datos)
        .replace("{{NVENTA}}", str(nv)).replace("{{NALQ}}", str(na)).replace("{{FECHA}}", fecha))
open(out, "w", encoding="utf-8").write(page)
print(f"OK: {nv} en venta, {na} en alquiler -> {out}")
