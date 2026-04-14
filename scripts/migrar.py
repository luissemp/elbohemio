import os
import re
import markdown
from pathlib import Path

# ========== CONFIGURACIÓN ==========
CARPETA_MD = r"C:\Users\Usuario\Documents\elbohemio\articulos_md"
CARPETA_POSTS = r"C:\Users\Usuario\Documents\elbohemio\posts"
CARPETA_SCRIPTS = r"C:\Users\Usuario\Documents\elbohemio\scripts"

def extraer_epigrafe(contenido_md):
    lineas = contenido_md.split('\n')
    cita = ""
    autor = ""
    for i, linea in enumerate(lineas):
        if linea.startswith('> '):
            cita = linea[2:].strip()
            if i + 1 < len(lineas) and lineas[i + 1].startswith('> —'):
                autor = lineas[i + 1][3:].strip()
            elif '—' in cita:
                partes = cita.split('—', 1)
                cita = partes[0].strip()
                autor = partes[1].strip()
            break
    return cita, autor

def extraer_metadatos(contenido_md, nombre_archivo):
    """Extrae titulo, numero e id de los metadatos YAML"""
    titulo = None
    numero = None
    id_articulo = None
    
    # Buscar bloque de metadatos: --- ... ---
    match = re.search(r'^---\s*\n(.*?)\n---\s*\n', contenido_md, re.DOTALL)
    if match:
        metadatos_bloque = match.group(1)
        titulo_match = re.search(r'titulo:\s*["\']?([^"\'\n]+)["\']?', metadatos_bloque)
        if titulo_match:
            titulo = titulo_match.group(1).strip()
        numero_match = re.search(r'numero:\s*(\d+)', metadatos_bloque)
        if numero_match:
            numero = int(numero_match.group(1))
        id_match = re.search(r'id:\s*["\']?([^"\'\n]+)["\']?', metadatos_bloque)
        if id_match:
            id_articulo = id_match.group(1).strip()
    
    # Si no encontró título, usar el nombre del archivo
    if not titulo:
        nombre_sin_extension = nombre_archivo.replace('.md', '')
        nombre_sin_numero = re.sub(r'^\d+[_\-]', '', nombre_sin_extension)
        titulo = nombre_sin_numero.replace('-', ' ').replace('_', ' ').title()
    
    # Si no encontró número, extraer del nombre
    if not numero:
        match_num = re.match(r'(\d+)[_\-]', nombre_archivo)
        numero = int(match_num.group(1)) if match_num else 999
    
    # Si no encontró ID, generarlo del título
    if not id_articulo:
        id_articulo = re.sub(r'[^a-z0-9-]', '', titulo.lower().replace(' ', '-'))
        id_articulo = re.sub(r'-+', '-', id_articulo).strip('-')
        # Limitar longitud del ID a 50 caracteres
        id_articulo = id_articulo[:50]
    
    return titulo, numero, id_articulo

def limpiar_metadatos(contenido_md):
    """Elimina el bloque de metadatos YAML del contenido"""
    return re.sub(r'^---\s*\n.*?\n---\s*\n', '', contenido_md, flags=re.DOTALL)

def generar_html_articulo(archivo_md):
    with open(archivo_md, 'r', encoding='utf-8') as f:
        contenido_md = f.read()
    
    nombre_archivo = os.path.basename(archivo_md)
    
    # Extraer metadatos
    titulo, numero, id_articulo = extraer_metadatos(contenido_md, nombre_archivo)
    
    # Limpiar metadatos del contenido
    contenido_sin_metadatos = limpiar_metadatos(contenido_md)
    
    # Extraer epígrafe
    cita, autor_cita = extraer_epigrafe(contenido_sin_metadatos)
    
    # Remover la línea de la cita del contenido
    lineas = contenido_sin_metadatos.split('\n')
    contenido_sin_cita = []
    skip = False
    for linea in lineas:
        if linea.startswith('> '):
            skip = True
            continue
        if skip and linea.startswith('> —'):
            skip = False
            continue
        if skip:
            skip = False
        contenido_sin_cita.append(linea)
    
    contenido_limpio = '\n'.join(contenido_sin_cita).strip()
    html_contenido = markdown.markdown(contenido_limpio, extensions=['extra'])
    html_contenido = html_contenido.replace('<hr />', '<div class="sep"></div>')
    
    # HTML final
    html_articulo = f"""<div id="{id_articulo}-content" class="article-container">
      <h1 class="article-title">{titulo}</h1>
      <p class="article-author">Por Luis Semprún Jurado</p>
      <div class="quote-container">
        <p class="article-quote">"{cita}"</p>
        <span class="quote-author">{autor_cita if autor_cita else "ANACLETO"}</span>
      </div>
      {html_contenido}
    </div>"""
    
    return id_articulo, titulo, numero, html_articulo

def generar_lista_lateral(articulos):
    articulos_ordenados = sorted(articulos, key=lambda x: x['numero'], reverse=True)
    
    lista_html = '<h3>Mis Artículos</h3>\n<ul>\n'
    for art in articulos_ordenados:
        lista_html += f'        <li><a onclick="loadArticle(\'{art["id"]}\')">{art["numero"]}. {art["titulo"]}</a></li>\n'
    lista_html += '      </ul>'
    
    return lista_html

def main():
    print("=" * 50)
    print("🚀 EL BOHEMIO DIGITAL - MIGRADOR CON IDs MANUALES")
    print("=" * 50)
    
    Path(CARPETA_MD).mkdir(parents=True, exist_ok=True)
    Path(CARPETA_POSTS).mkdir(parents=True, exist_ok=True)
    
    archivos_md = list(Path(CARPETA_MD).glob("*.md"))
    
    if not archivos_md:
        print(f"\n❌ No hay archivos .md en: {CARPETA_MD}")
        return
    
    articulos = []
    print(f"\n📄 Procesando {len(archivos_md)} artículo(s):\n")
    
    for md_file in sorted(archivos_md):
        id_art, titulo, numero, html = generar_html_articulo(md_file)
        
        archivo_html = Path(CARPETA_POSTS) / f"{id_art}.html"
        with open(archivo_html, 'w', encoding='utf-8') as f:
            f.write(html)
        
        articulos.append({
            'id': id_art,
            'titulo': titulo,
            'numero': numero,
            'archivo': md_file.name
        })
        
        print(f"   ✅ {numero} - {titulo[:50]}... → posts/{id_art}.html")
    
    lista_lateral = generar_lista_lateral(articulos)
    
    with open(Path(CARPETA_SCRIPTS) / "lista_lateral_nueva.txt", 'w', encoding='utf-8') as f:
        f.write(lista_lateral)
    
    print("\n" + "=" * 50)
    print("✅ MIGRACIÓN COMPLETADA")
    print("=" * 50)
    print(f"\n📁 Los artículos están en: {CARPETA_POSTS}")
    print("\n📋 Si quieres IDs personalizados, agrega 'id: mi-id-corto' en los metadatos de cada .md")

if __name__ == "__main__":
    main()