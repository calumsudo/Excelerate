from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from PyPDF2 import PdfFileReader, PdfFileWriter

import pandas as pd
from datetime import datetime
import os


def dataframe_to_table_style_data(df, font_size=8):
    """Converts a DataFrame to data and style for a reportlab Table with a customizable font size."""
    data = [df.columns.tolist()] + df.values.tolist()
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                6,
            ),  # Adjust padding to ensure smaller text doesn't look too spaced
            ("FONTSIZE", (0, 0), (-1, -1), font_size),  # Apply the font size
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )
    return data, style


def generate_unmatched_merchants_table(info_list, sheet_name):
    """Generate a table for unmatched merchants for a given sheet."""
    data = [["Advance ID", "Merchant Name"]] + [
        [item["advance_id"], item["merchant_name"]]
        for item in info_list
        if item["sheet_name"] == sheet_name
    ]
    if not data[1:]:  # Check if there is no data besides the header
        return None, None
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]
    )
    return data, style


def generate_report(
    kings_pivot_table,
    kings_total_gross_amount,
    kings_total_net_amount,
    kings_total_fee,
    boom_pivot_table,
    boom_total_gross_amount,
    boom_total_net_amount,
    boom_total_fee,
    bhb_pivot_table,
    bhb_total_gross_amount,
    bhb_total_net_amount,
    bhb_total_fee,
    cv_pivot_table,
    cv_total_gross_amount,
    cv_total_net_amount,
    cv_total_fee,
    acs_pivot_table,
    acs_total_gross_amount,
    acs_total_net_amount,
    acs_total_fee,
    VSPR_pivot_table,
    VSPR_total_gross_amount,
    VSPR_total_net_amount,
    VSPR_total_fee,
    selected_file,
    directory,
    portfolio_name,
    detailed_unmatched_info,
):
    """Generates a PDF report with the provided data and saves it to the specified directory."""
    # Create the directory if it doesn't exist
    # Get the current date
    if portfolio_name == 1:
        portfolio_name = "Alder"
    elif portfolio_name == 2:
        portfolio_name = "White Rabbit"

    # Format the date as a string
    today_date = datetime.now().strftime("%m_%d_%Y")

    # Create the output name
    output_name = f"Excelerator_Report_{today_date}.pdf"

    # Specify the directory
    directory = os.path.expanduser(f"{directory}/{portfolio_name}/{today_date}")

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Construct the full path to the output file
    output_path = os.path.join(directory, output_name)

    doc = SimpleDocTemplate(output_path, pagesize=letter)

    elements = []
    styleSheet = getSampleStyleSheet()

    # Title for the report
    elements.append(
        Paragraph(
            f"Excelerator Report for {portfolio_name} week of {today_date}",
            styleSheet["Title"],
        )
    )
    elements.append(Spacer(1, 0.25 * inch))

    # Create a new style for 'Subtitle'
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styleSheet["BodyText"],  # Inherit properties from 'BodyText'
        fontSize=14,
        leading=16,
    )
    # Add the new style to the stylesheet
    styleSheet.add(subtitle_style)

    # Subtitle for selected file
    file_name, _ = selected_file
    elements.append(Paragraph(f"Selected file: {file_name}", styleSheet["Subtitle"]))
    elements.append(Spacer(1, 0.25 * inch))

    # For each DataFrame, convert to Table and add to elements
    for title, df in [
        ("Kings", kings_pivot_table),
        ("Boom", boom_pivot_table),
        ("BHB", bhb_pivot_table),
        ("ClearView", cv_pivot_table),
        ("ACS", acs_pivot_table),
        ("VSPR", VSPR_pivot_table),
    ]:
        elements.append(Paragraph(title, styleSheet["Heading2"]))
        if title == "ACS":
            data, style = dataframe_to_table_style_data(
                df, font_size=6
            )  # Smaller font size for ACS table
        else:
            data, style = dataframe_to_table_style_data(df, font_size=8)
        table = Table(data)
        table.setStyle(style)
        elements.append(table)
        elements.append(Spacer(1, 0.25 * inch))
        if title == "Kings":
            elements.append(
                Paragraph(
                    f"Total Gross Amount: {kings_total_gross_amount}",
                    styleSheet["BodyText"],
                )
            )
            elements.append(
                Paragraph(
                    f"Total Net Amount: {kings_total_net_amount}",
                    styleSheet["BodyText"],
                )
            )
            elements.append(
                Paragraph(f"Total Fee: {kings_total_fee}", styleSheet["BodyText"])
            )
        elif title == "Boom":
            elements.append(
                Paragraph(
                    f"Total Gross Amount: {boom_total_gross_amount}",
                    styleSheet["BodyText"],
                )
            )
            elements.append(
                Paragraph(
                    f"Total Net Amount: {boom_total_net_amount}", styleSheet["BodyText"]
                )
            )
            elements.append(
                Paragraph(f"Total Fee: {boom_total_fee}", styleSheet["BodyText"])
            )
        elif title == "BHB":
            elements.append(
                Paragraph(
                    f"Total Gross Amount: {bhb_total_gross_amount}",
                    styleSheet["BodyText"],
                )
            )
            elements.append(
                Paragraph(
                    f"Total Net Amount: {bhb_total_net_amount}", styleSheet["BodyText"]
                )
            )
            elements.append(
                Paragraph(f"Total Fee: {bhb_total_fee}", styleSheet["BodyText"])
            )
        elif title == "VSPR":
            elements.append(
                Paragraph(
                    f"Total Gross Amount: {VSPR_total_gross_amount}",
                    styleSheet["BodyText"],
                )
            )
            elements.append(
                Paragraph(
                    f"Total Net Amount: {VSPR_total_net_amount}",
                    styleSheet["BodyText"],
                )
            )
            elements.append(
                Paragraph(f"Total Fee: {VSPR_total_fee}", styleSheet["BodyText"])
            )
        elif title == "ClearView":
            elements.append(
                Paragraph(
                    f"Total Gross Amount: {cv_total_gross_amount}",
                    styleSheet["BodyText"],
                )
            )
            elements.append(
                Paragraph(
                    f"Total Net Amount: {cv_total_net_amount}", styleSheet["BodyText"]
                )
            )
            elements.append(
                Paragraph(f"Total Fee: {cv_total_fee}", styleSheet["BodyText"])
            )
        elif title == "ACS":
            elements.append(
                Paragraph(
                    f"Total Gross Amount: {acs_total_gross_amount}",
                    styleSheet["BodyText"],
                )
            )
            elements.append(
                Paragraph(
                    f"Total Net Amount: {acs_total_net_amount}", styleSheet["BodyText"]
                )
            )
            elements.append(
                Paragraph(f"Total Fee: {acs_total_fee}", styleSheet["BodyText"])
            )
        elements.append(Spacer(1, 0.25 * inch))

        unmatched_data, unmatched_style = generate_unmatched_merchants_table(
            detailed_unmatched_info, title
        )
        if unmatched_data:
            elements.append(
                Paragraph(f"{title} Unmatched Merchants", styleSheet["Heading3"])
            )
            unmatched_table = Table(unmatched_data)
            unmatched_table.setStyle(unmatched_style)
            elements.append(unmatched_table)
            elements.append(Spacer(1, 0.25 * inch))

    doc.build(elements)
