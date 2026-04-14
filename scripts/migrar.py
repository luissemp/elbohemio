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

def generar_html_articulo(archivo_md):
    with open(archivo_md, 'r', encoding='utf-8') as f:
        contenido_md = f.read()
    
    # Extraer título del nombre del archivo
    nombre = os.path.basename(archivo_md)
    match = re.match(r'(\d+)[_\-](.+)\.md', nombre)
    if match:
        numero = int(match.group(1))
        titulo_raw = match.group(2).replace('-', ' ').replace('_', ' ')
        titulo = titulo_raw.title()
        id_articulo = re.sub(r'[^a-z0-9-]', '', titulo_raw.lower().replace(' ', '-'))
    else:
        numero = 999
        titulo = nombre.replace('.md', '').replace('-', ' ').title()
        id_articulo = re.sub(r'[^a-z0-9-]', '', titulo.lower().replace(' ', '-'))
    
    cita, autor_cita = extraer_epigrafe(contenido_md)
    
    # Remover la línea de la cita del contenido
    lineas = contenido_md.split('\n')
    contenido_sin_cita = []
    skip = False
    for i, linea in enumerate(lineas):
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
    
    # HTML final del artículo
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
    """Genera la lista HTML para la barra lateral ordenada por número descendente"""
    articulos_ordenados = sorted(articulos, key=lambda x: x['numero'], reverse=True)
    
    lista_html = '<h3>Mis Artículos</h3>\n<ul>\n'
    for art in articulos_ordenados:
        lista_html += f'        <li><a onclick="loadArticle(\'{art["id"]}\')">{art["numero"]}. {art["titulo"]}</a></li>\n'
    lista_html += '      </ul>'
    
    return lista_html

def main():
    print("=" * 50)
    print("🚀 EL BOHEMIO DIGITAL - MIGRADOR DEFINITIVO")
    print("=" * 50)
    
    # Crear carpetas si no existen
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
        
        # Guardar como archivo HTML independiente
        archivo_html = Path(CARPETA_POSTS) / f"{id_art}.html"
        with open(archivo_html, 'w', encoding='utf-8') as f:
            f.write(html)
        
        articulos.append({
            'id': id_art,
            'titulo': titulo,
            'numero': numero,
            'archivo': md_file.name
        })
        
        print(f"   ✅ {numero} - {titulo} → posts/{id_art}.html")
    
    # Generar lista lateral
    lista_lateral = generar_lista_lateral(articulos)
    
    # Guardar la lista lateral
    with open(Path(CARPETA_SCRIPTS) / "lista_lateral_nueva.txt", 'w', encoding='utf-8') as f:
        f.write(lista_lateral)
    
    print("\n" + "=" * 50)
    print("✅ MIGRACIÓN COMPLETADA")
    print("=" * 50)
    print("\n📋 AHORA DEBES:")
    print("   1. Reemplazar la función loadArticle() en tu index.html")
    print("   2. Reemplazar la lista de la barra lateral con el contenido de:")
    print(f"      {CARPETA_SCRIPTS}\\lista_lateral_nueva.txt")
    print("   3. Eliminar el <div style=\"display: none;\"> con todos los artículos")
    print(f"\n📁 Los artículos están en: {CARPETA_POSTS}")
    print("🚀 ¡Tu blog ahora es liviano y fácil de mantener!")

if __name__ == "__main__":
    main()