#!/usr/bin/env python3
"""Genera la versión de la web para jaimetercero.com (GitHub Pages).

Uso: python3 build_sitio.py <carpeta_fuente> <carpeta_repo>
Genera index.html (documento HTML completo), sitemap.xml, robots.txt y CNAME.
Las fotos (gal2/, portada/) se copian aparte.
"""
import datetime, json, os, subprocess, sys, html

src, repo = sys.argv[1], sys.argv[2]
DOMINIO = "https://jaimetercero.com"
tmp = os.path.join(repo, "_cuerpo.html")
subprocess.run([sys.executable, os.path.join(src, "build.py"), src, tmp], check=True)
cuerpo = open(tmp, encoding="utf-8").read()
os.remove(tmp)

# La plantilla empieza con <title>, metas, fuentes y <style>: van al <head>.
fin_head = cuerpo.index("</style>") + len("</style>")
head_plantilla, body = cuerpo[:fin_head], cuerpo[fin_head:]
head_plantilla = head_plantilla.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', "")

data = json.load(open(os.path.join(src, "inmuebles.json"), encoding="utf-8"))
items = [i for i in data["inmuebles"] if not i.get("oculto")]

descripcion = ("Inmobiliaria JAIME III: pisos, áticos, casas y terrenos en venta y alquiler en Palma "
               "y toda Mallorca. Valoramos su propiedad gratis. Passatge Galerías Jaime III, 2, Palma.")
negocio = {
    "@context": "https://schema.org",
    "@type": "RealEstateAgent",
    "name": "Inmobiliaria JAIME III",
    "legalName": "INMOBILIARIA JAIME III, S.C.P.",
    "url": DOMINIO + "/",
    "logo": DOMINIO + "/fuente/logo.png",
    "image": DOMINIO + "/portada/portada-1.jpg",
    "telephone": "+34 691 740 124",
    "email": "miguelp@jaimetercero.com",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Passatge Galerías Jaime III, 2, 5º A",
        "postalCode": "07012",
        "addressLocality": "Palma",
        "addressRegion": "Illes Balears",
        "addressCountry": "ES",
    },
    "areaServed": ["Palma", "Mallorca"],
}
jsonld = json.dumps(negocio, ensure_ascii=False).replace("</", "<\\/")

head = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{html.escape(descripcion)}">
<link rel="canonical" href="{DOMINIO}/">
<link rel="icon" type="image/png" href="fuente/logo.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Inmobiliaria JAIME III">
<meta property="og:title" content="Inmobiliaria JAIME III · Pisos y casas en venta y alquiler en Palma y Mallorca">
<meta property="og:description" content="{html.escape(descripcion)}">
<meta property="og:url" content="{DOMINIO}/">
<meta property="og:image" content="{DOMINIO}/portada/portada-1.jpg">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{jsonld}</script>
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0;font-size:14px}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
"""
head_plantilla = head_plantilla.replace(
    "<title>Inmobiliaria JAIME III</title>",
    "<title>Inmobiliaria JAIME III · Pisos y casas en venta y alquiler en Palma y Mallorca</title>")
pagina = head + head_plantilla + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n"
open(os.path.join(repo, "index.html"), "w", encoding="utf-8").write(pagina)

hoy = datetime.date.today().isoformat()
open(os.path.join(repo, "sitemap.xml"), "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f"  <url><loc>{DOMINIO}/</loc><lastmod>{hoy}</lastmod><changefreq>daily</changefreq></url>\n"
    "</urlset>\n")
open(os.path.join(repo, "robots.txt"), "w", encoding="utf-8").write(
    f"User-agent: *\nAllow: /\nDisallow: /fuente/\nSitemap: {DOMINIO}/sitemap.xml\n")
open(os.path.join(repo, "CNAME"), "w").write("jaimetercero.com\n")
open(os.path.join(repo, ".nojekyll"), "w").write("")
print(f"Sitio generado en {repo}: {len(items)} inmuebles")
