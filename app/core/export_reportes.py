"""
Utilidades de exportacion para reportes (CSV, XLSX y PDF).
"""
from __future__ import annotations

import csv
from io import BytesIO, StringIO
from typing import Iterable, List, Dict, Any
from datetime import datetime, timezone, time

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def ExportarCSV(filas: Iterable[Dict[str, Any]], columnas: List[str], encabezados: List[str]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(encabezados)
    for fila in filas:
        writer.writerow([fila.get(col, "") for col in columnas])
    return buffer.getvalue()


def ExportarXLSX(
    filas: Iterable[Dict[str, Any]],
    columnas: List[str],
    encabezados: List[str],
    nombre_hoja: str = "Reporte",
) -> bytes:
    workbook = Workbook()
    hoja = workbook.active
    hoja.title = nombre_hoja[:31] or "Reporte"
    hoja.append(encabezados)
    for fila in filas:
        hoja.append([_valor_para_xlsx(fila.get(col, "")) for col in columnas])

    for idx, head in enumerate(encabezados, start=1):
        hoja.column_dimensions[chr(64 + min(idx, 26))].width = max(len(str(head)) + 4, 14)

    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


def ExportarPDFTabla(
    titulo: str,
    subtitulo: str,
    filas: Iterable[Dict[str, Any]],
    columnas: List[str],
    encabezados: List[str],
) -> bytes:
    filas_lista = list(filas)
    es_tabla_ancha = len(encabezados) >= 7
    page_size = landscape(letter) if es_tabla_ancha else letter
    body_font_size = 7 if len(encabezados) >= 10 else (8 if len(encabezados) >= 7 else 9)
    header_font_size = body_font_size + 1

    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=page_size,
        leftMargin=20,
        rightMargin=20,
        topMargin=24,
        bottomMargin=24,
    )
    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(
        "table_cell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=body_font_size,
        leading=body_font_size + 1,
        wordWrap="CJK",
    )
    header_style = ParagraphStyle(
        "table_header",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=header_font_size,
        leading=header_font_size + 1,
        textColor=colors.white,
        wordWrap="CJK",
    )

    elementos = [
        Paragraph(titulo, styles["Title"]),
        Spacer(1, 8),
        Paragraph(subtitulo, styles["Normal"]),
        Spacer(1, 12),
    ]

    tabla_data = [[Paragraph(str(h), header_style) for h in encabezados]]
    for fila in filas_lista:
        tabla_data.append(
            [Paragraph(_valor_para_pdf(fila.get(col)), cell_style) for col in columnas]
        )

    if len(tabla_data) == 1:
        tabla_data.append([Paragraph("Sin datos", cell_style)] + [Paragraph("", cell_style)] * (len(encabezados) - 1))

    col_widths = _calcular_anchos_columna(encabezados, filas_lista, columnas, doc.width)
    tabla = Table(tabla_data, repeatRows=1, colWidths=col_widths)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3C88")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
    ]))
    elementos.append(tabla)
    doc.build(elementos)
    return output.getvalue()


def _valor_para_pdf(valor: Any) -> str:
    if valor is None:
        return ""
    if isinstance(valor, float):
        return f"{valor:.2f}"
    return str(valor)


def _valor_para_xlsx(valor: Any) -> Any:
    if isinstance(valor, datetime):
        # Excel/OpenPyXL no admite datetimes con tzinfo.
        if valor.tzinfo is not None:
            return valor.astimezone(timezone.utc).replace(tzinfo=None)
        return valor
    if isinstance(valor, time) and valor.tzinfo is not None:
        return valor.replace(tzinfo=None)
    return valor


def _calcular_anchos_columna(
    encabezados: List[str],
    filas: List[Dict[str, Any]],
    columnas: List[str],
    ancho_disponible: float,
) -> List[float]:
    pesos: List[float] = []
    for idx, col in enumerate(columnas):
        max_len = len(str(encabezados[idx]))
        for fila in filas:
            valor_len = len(_valor_para_pdf(fila.get(col)))
            if valor_len > max_len:
                max_len = valor_len
        pesos.append(min(max(max_len, 8), 36))

    total_pesos = sum(pesos) or 1
    return [ancho_disponible * (p / total_pesos) for p in pesos]
