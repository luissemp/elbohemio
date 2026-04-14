import os
import re
import markdown
from datetime import datetime
from pathlib import Path

# ========== CONFIGURACIÓN ==========
CARPETA_MD = r"C:\Users\Usuario\Documents\elbohemio\articulos_md"
CARPETA_SCRIPTS = r"C:\Users\Usuario\Documents\elbohemio\scripts"

# ========== FUNCIONES ==========

def extraer_epigrafe(contenido_md):
    """Extrae la primera cita del Markdown (formato > cita o > cita\n> — Autor)"""
    lineas = contenido_md.split('\n')
    cita = ""
    autor = ""
    
    for i, linea in enumerate(lineas):
        if linea.startswith('> '):
            # Limpiar la cita
            cita = linea[2:].strip()
            # Buscar si la siguiente línea tiene el autor
            if i + 1 < len(lineas) and lineas[i + 1].startswith('> —'):
                autor = lineas[i + 1][3:].strip()
            elif '—' in cita:
                partes = cita.split('—', 1)
                cita = partes[0].strip()
                autor = partes[1].strip()
            break
    
    return cita, autor

def generar_html_articulo(archivo_md):
    """Convierte un archivo Markdown a HTML con el formato de El Bohemio"""
    
    with open(archivo_md, 'r', encoding='utf-8') as f:
        contenido_md = f.read()
    
    # Extraer metadatos del nombre del archivo
    nombre = os.path.basename(archivo_md)
    # Formato: 01_titulo-corto.md o 01-titulo-corto.md
    match = re.match(r'(\d+)[_\-](.+)\.md', nombre)
    if match:
        numero = int(match.group(1))
        titulo_raw = match.group(2).replace('-', ' ').replace('_', ' ')
        titulo = titulo_raw.title()
    else:
        numero = 999
        titulo = nombre.replace('.md', '').replace('-', ' ').title()
    
    # Extraer epígrafe (cita)
    cita, autor_cita = extraer_epigrafe(contenido_md)
    
    # Remover la línea de la cita del contenido principal
    lineas = contenido_md.split('\n')
    contenido_sin_cita = []
    skip_next = False
    for i, linea in enumerate(lineas):
        if linea.startswith('> '):
            skip_next = True
            continue
        if skip_next and linea.startswith('> —'):
            skip_next = False
            continue
        if skip_next:
            skip_next = False
        contenido_sin_cita.append(linea)
    
    contenido_limpio = '\n'.join(contenido_sin_cita).strip()
    
    # Convertir Markdown a HTML
    html_contenido = markdown.markdown(contenido_limpio, extensions=['extra'])
    
    # Reemplazar <hr /> (que es --- en Markdown) por <div class="sep"></div>
    html_contenido = html_contenido.replace('<hr />', '<div class="sep"></div>')
    
    # Generar el ID del artículo (sin números ni caracteres especiales)
    id_articulo = re.sub(r'[^a-z0-9]', '', titulo.lower().replace(' ', ''))[:30]
    
    # Construir el HTML final del artículo
    html_articulo = f"""<div id="{id_articulo}-content" class="article-container">
      <h1 class="article-title">{titulo}</h1>
      <p class="article-author">Por Luis Semprún Jurado</p>
      <div class="quote-container">
        <p class="article-quote">"{cita}"</p>
        <span class="quote-author">{autor_cita if autor_cita else "ANACLETO"}</span>
      </div>
      {html_contenido}
    </div>"""
    
    return {
        'numero': numero,
        'titulo': titulo,
        'id': id_articulo,
        'html': html_articulo
    }

def generar_lista_articulos(articulos):
    """Genera la lista HTML para la barra lateral (ordenada descendente)"""
    # Ordenar por número descendente (mayor = más reciente)
    articulos_ordenados = sorted(articulos, key=lambda x: x['numero'], reverse=True)
    
    lista_html = ""
    for art in articulos_ordenados:
        lista_html += f'        <li><a onclick="loadArticle(\'{art["id"]}\')">{art["numero"]}. {art["titulo"]}</a></li>\n'
    
    return lista_html

def main():
    print("=" * 50)
    print("📝 EL BOHEMIO DIGITAL - PUBLICADOR AUTOMÁTICO")
    print("=" * 50)
    
    # Crear carpeta si no existe
    Path(CARPETA_MD).mkdir(parents=True, exist_ok=True)
    
    # Buscar archivos .md
    archivos_md = list(Path(CARPETA_MD).glob("*.md"))
    
    if not archivos_md:
        print(f"\n❌ No se encontraron archivos .md en:")
        print(f"   {CARPETA_MD}")
        print("\n📌 Creá un archivo .md con el formato:")
        print("   01_mi-primer-articulo.md")
        print("\n   Y dentro escribí:")
        print("   > Esta es mi cita")
        print("   > — Mi Autor")
        print("   Luego el contenido...")
        return
    
    # Procesar cada archivo
    articulos = []
    print(f"\n📄 Procesando {len(archivos_md)} archivo(s):\n")
    
    for md_file in sorted(archivos_md):
        print(f"   ▶ Leyendo: {md_file.name}")
        articulo = generar_html_articulo(md_file)
        articulos.append(articulo)
        print(f"      ✅ Generado: {articulo['id']} - {articulo['titulo']}")
    
    # Generar la lista de artículos
    lista_html = generar_lista_articulos(articulos)
    
    # Generar el bloque completo para pegar en <div style="display: none;">
    bloque_articulos = "\n".join([art['html'] for art in articulos])
    
    # Mostrar resultados
    print("\n" + "=" * 50)
    print("📋 RESULTADOS")
    print("=" * 50)
    
    print("\n1️⃣ COPIA ESTE BLOQUE DE ARTÍCULOS dentro del <div style=\"display: none;\">:")
    print("-" * 50)
    print(bloque_articulos)
    print("-" * 50)
    
    print("\n2️⃣ REEMPLAZA LA LISTA DE LA BARRA LATERAL por esto:")
    print("-" * 50)
    print(lista_html)
    print("-" * 50)
    
    print("\n3️⃣ GUARDA estos archivos en tu carpeta MD como respaldo:")
    for art in articulos:
        print(f"   - {art['numero']:02d}_{art['id']}.md")
    
    print("\n" + "=" * 50)
    print("✅ PROCESO COMPLETADO")
    print("=" * 50)
    
    # Guardar resultados en archivos
    with open(Path(CARPETA_SCRIPTS) / "bloque_articulos.txt", 'w', encoding='utf-8') as f:
        f.write(bloque_articulos)
    
    with open(Path(CARPETA_SCRIPTS) / "lista_lateral.txt", 'w', encoding='utf-8') as f:
        f.write(lista_html)
    
    print(f"\n📁 Los resultados también se guardaron en:")
    print(f"   {CARPETA_SCRIPTS}\\bloque_articulos.txt")
    print(f"   {CARPETA_SCRIPTS}\\lista_lateral.txt")

if __name__ == "__main__":
    main()