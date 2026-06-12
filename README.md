# edicao_pdf

Ferramenta Python para edição de arquivos PDF: mesclar, separar, reordenar páginas, OCR com Tesseract, conversão para Markdown e geração de PDF a partir de arquivos ZIP.

## Funcionalidades

| Comando CLI        | Função Python         | Descrição |
|--------------------|-----------------------|-----------|
| `merge`            | `merge_pdfs`          | Mescla múltiplos PDFs em um único arquivo |
| `split`            | `split_pdf`           | Separa um PDF em páginas individuais ou intervalos |
| `reorder`          | `reorder_pages`       | Reordena (ou ordena) as páginas de um PDF |
| `ocr`              | `ocr_pdf`             | OCR via [Tesseract](https://github.com/tesseract-ocr/tesseract) |
| `to-markdown`      | `pdf_to_markdown`     | Converte PDF para Markdown (via PyMuPDF) |
| `zip-to-pdf`       | `zip_to_pdf`          | Converte e mescla arquivos de um ZIP em um único PDF |

## Instalação

```bash
pip install -e .
```

> **Dependência de sistema (OCR):** o comando `ocr` requer o [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) instalado no sistema.
> ```bash
> # Ubuntu/Debian
> sudo apt install tesseract-ocr tesseract-ocr-por
> # macOS
> brew install tesseract
> ```

## Uso (linha de comando)

### Mesclar PDFs

```bash
edicao-pdf merge a.pdf b.pdf c.pdf -o saida.pdf
```

### Separar PDF

```bash
# Uma página por arquivo
edicao-pdf split doc.pdf -o partes/

# Por intervalos
edicao-pdf split doc.pdf -o partes/ -r 1-3 -r 4-6
```

### Reordenar páginas

```bash
# Página 3 primeiro, depois 1, depois 2
edicao-pdf reorder doc.pdf 3 1 2 -o reordenado.pdf
```

### OCR com Tesseract

```bash
edicao-pdf ocr scan.pdf -o texto.txt --lang por --dpi 400
```

### Converter para Markdown

```bash
edicao-pdf to-markdown doc.pdf -o doc.md
```

### ZIP → PDF

Extrai os arquivos do ZIP (PDFs, imagens e `.txt`), converte cada um e mescla tudo em um único PDF:

```bash
edicao-pdf zip-to-pdf documentos.zip -o resultado.pdf

# Preservar a ordem interna do ZIP (sem ordenar por nome)
edicao-pdf zip-to-pdf fotos.zip -o album.pdf --no-sort

# Arquivos .txt com outra codificação
edicao-pdf zip-to-pdf legado.zip -o resultado.pdf --encoding latin-1
```

**Tipos suportados dentro do ZIP:** `.pdf`, `.jpg`/`.jpeg`, `.png`, `.bmp`, `.gif`, `.tiff`/`.tif`, `.webp`, `.txt`.

## Uso como biblioteca

```python
from edicao_pdf import (
    merge_pdfs,
    split_pdf,
    reorder_pages,
    ocr_pdf,
    pdf_to_markdown,
    zip_to_pdf,
)

# Mesclar
merge_pdfs(["a.pdf", "b.pdf"], "saida.pdf")

# Separar
split_pdf("doc.pdf", "partes/")
split_pdf("doc.pdf", "partes/", page_ranges=[(1, 3), (4, 6)])

# Reordenar
reorder_pages("doc.pdf", "reordenado.pdf", order=[3, 1, 2])

# OCR
texto = ocr_pdf("scan.pdf", lang="por", dpi=300)

# Markdown
md = pdf_to_markdown("doc.pdf", output_path="doc.md")

# ZIP → PDF
zip_to_pdf("documentos.zip", "resultado.pdf")
```

## Desenvolvimento

```bash
pip install -e ".[dev]"
pytest
```

## Licença

MIT — veja [LICENSE](LICENSE).
