"""Command-line interface for edicao_pdf."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from edicao_pdf.merge import merge_pdfs
from edicao_pdf.split import split_pdf
from edicao_pdf.reorder import reorder_pages
from edicao_pdf.ocr import ocr_pdf
from edicao_pdf.to_markdown import pdf_to_markdown
from edicao_pdf.zip_to_pdf import zip_to_pdf


@click.group()
def main() -> None:
    """edicao_pdf — ferramenta de edição de arquivos PDF."""


# ---------------------------------------------------------------------------
# merge
# ---------------------------------------------------------------------------

@main.command("merge")
@click.argument("inputs", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("-o", "--output", required=True, help="Caminho do PDF de saída.")
def cmd_merge(inputs: tuple[str, ...], output: str) -> None:
    """Mescla múltiplos PDFs em um único arquivo.

    \b
    Exemplo:
        edicao-pdf merge a.pdf b.pdf c.pdf -o saida.pdf
    """
    if len(inputs) < 2:
        raise click.UsageError("Informe ao menos dois arquivos PDF para mesclar.")
    result = merge_pdfs(inputs, output)
    click.echo(f"PDF mesclado salvo em: {result}")


# ---------------------------------------------------------------------------
# split
# ---------------------------------------------------------------------------

@main.command("split")
@click.argument("input", type=click.Path(exists=True))
@click.option("-o", "--output-dir", required=True, help="Diretório de saída.")
@click.option(
    "-r",
    "--range",
    "ranges",
    multiple=True,
    metavar="INICIO-FIM",
    help=(
        "Intervalo de páginas no formato INICIO-FIM (1-based, inclusivo). "
        "Pode ser repetido. Omitir extrai cada página individualmente."
    ),
)
def cmd_split(input: str, output_dir: str, ranges: tuple[str, ...]) -> None:
    """Separa um PDF em múltiplos arquivos.

    \b
    Exemplos:
        edicao-pdf split doc.pdf -o partes/
        edicao-pdf split doc.pdf -o partes/ -r 1-3 -r 4-6
    """
    page_ranges = None
    if ranges:
        page_ranges = []
        for r in ranges:
            try:
                start_str, end_str = r.split("-", 1)
                page_ranges.append((int(start_str), int(end_str)))
            except ValueError:
                raise click.BadParameter(
                    f"Intervalo inválido '{r}'. Use o formato INICIO-FIM (ex: 1-3)."
                )

    files = split_pdf(input, output_dir, page_ranges)
    for f in files:
        click.echo(str(f))
    click.echo(f"\n{len(files)} arquivo(s) gerado(s) em: {output_dir}")


# ---------------------------------------------------------------------------
# reorder
# ---------------------------------------------------------------------------

@main.command("reorder")
@click.argument("input", type=click.Path(exists=True))
@click.argument("order", nargs=-1, required=True, type=int)
@click.option("-o", "--output", required=True, help="Caminho do PDF de saída.")
def cmd_reorder(input: str, order: tuple[int, ...], output: str) -> None:
    """Reordena (ou ordena) as páginas de um PDF.

    ORDER é a lista de números de página (1-based) na ordem desejada.

    \b
    Exemplo (colocar página 3 primeiro, depois 1, depois 2):
        edicao-pdf reorder doc.pdf 3 1 2 -o reordenado.pdf
    """
    result = reorder_pages(input, output, list(order))
    click.echo(f"PDF reordenado salvo em: {result}")


# ---------------------------------------------------------------------------
# ocr
# ---------------------------------------------------------------------------

@main.command("ocr")
@click.argument("input", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Arquivo de texto de saída (.txt).")
@click.option("--lang", default="por+eng", show_default=True, help="Idioma(s) do Tesseract.")
@click.option("--dpi", default=300, show_default=True, type=int, help="DPI para rasterização.")
@click.option(
    "-p",
    "--page",
    "pages",
    multiple=True,
    type=int,
    help="Número(s) de página a processar (1-based). Repita para múltiplas páginas.",
)
@click.option("--tesseract-cmd", default=None, help="Caminho para o executável tesseract.")
def cmd_ocr(
    input: str,
    output: str | None,
    lang: str,
    dpi: int,
    pages: tuple[int, ...],
    tesseract_cmd: str | None,
) -> None:
    """Executa OCR em um PDF usando Tesseract.

    \b
    Exemplos:
        edicao-pdf ocr scan.pdf
        edicao-pdf ocr scan.pdf -o texto.txt --lang por --dpi 400
        edicao-pdf ocr scan.pdf -p 1 -p 3
    """
    text = ocr_pdf(
        input,
        output_path=output,
        lang=lang,
        pages=list(pages) if pages else None,
        dpi=dpi,
        tesseract_cmd=tesseract_cmd,
    )
    if output:
        click.echo(f"Texto OCR salvo em: {output}")
    else:
        click.echo(text)


# ---------------------------------------------------------------------------
# to-markdown
# ---------------------------------------------------------------------------

@main.command("to-markdown")
@click.argument("input", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Arquivo Markdown de saída (.md).")
@click.option(
    "-p",
    "--page",
    "pages",
    multiple=True,
    type=int,
    help="Número(s) de página a converter (1-based).",
)
def cmd_to_markdown(input: str, output: str | None, pages: tuple[int, ...]) -> None:
    """Converte um PDF para Markdown.

    \b
    Exemplos:
        edicao-pdf to-markdown doc.pdf -o doc.md
        edicao-pdf to-markdown doc.pdf -p 1 -p 2
    """
    md = pdf_to_markdown(input, output_path=output, pages=list(pages) if pages else None)
    if output:
        click.echo(f"Markdown salvo em: {output}")
    else:
        click.echo(md)


# ---------------------------------------------------------------------------
# zip-to-pdf
# ---------------------------------------------------------------------------

@main.command("zip-to-pdf")
@click.argument("zip_file", type=click.Path(exists=True))
@click.option("-o", "--output", required=True, help="Caminho do PDF de saída.")
@click.option(
    "--no-sort",
    is_flag=True,
    default=False,
    help="Preservar a ordem interna do ZIP em vez de ordenar por nome.",
)
@click.option(
    "--encoding",
    default="utf-8",
    show_default=True,
    help="Codificação usada para arquivos .txt dentro do ZIP.",
)
def cmd_zip_to_pdf(
    zip_file: str,
    output: str,
    no_sort: bool,
    encoding: str,
) -> None:
    """Converte e mescla os arquivos de um ZIP em um único PDF.

    Tipos suportados dentro do arquivo ZIP: PDF, imagens (JPEG, PNG, BMP,
    GIF, TIFF, WEBP) e arquivos de texto (.txt).

    \b
    Exemplos:
        edicao-pdf zip-to-pdf documentos.zip -o resultado.pdf
        edicao-pdf zip-to-pdf fotos.zip -o album.pdf --no-sort
    """
    result = zip_to_pdf(zip_file, output, sort_names=not no_sort, encoding=encoding)
    click.echo(f"PDF gerado a partir do ZIP salvo em: {result}")


if __name__ == "__main__":
    main()
