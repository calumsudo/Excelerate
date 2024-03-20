from parsers.kings_parser import parse_kings
from parsers.boom_parser import parse_boom
from parsers.bhb_parser import parse_bhb
from parsers.cv_parser import parse_cv
from parsers.acs_parser import parse_acs


from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from parsers.kings_parser import parse_kings
from parsers.boom_parser import parse_boom
from parsers.bhb_parser import parse_bhb
from parsers.cv_parser import parse_cv
from parsers.acs_parser import parse_acs

import pandas as pd

def dataframe_to_table_style_data(df, font_size=8):
    """Converts a DataFrame to data and style for a reportlab Table with a customizable font size."""
    data = [df.columns.tolist()] + df.values.tolist()
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  # Adjust padding to ensure smaller text doesn't look too spaced
        ('FONTSIZE', (0, 0), (-1, -1), font_size),  # Apply the font size
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    return data, style

def parse_csv_data(kings_csv_file, boom_csv_file, bhb_csv_file, acs_csv_file, cv_csv_files, selected_file):
    # Call the all parsing functions and capture its outputs
    kings_pivot_table, kings_total_gross_amount, kings_total_net_amount, kings_total_fee = parse_kings(kings_csv_file)
    boom_pivot_table, boom_total_gross_amount, boom_total_net_amount, boom_total_fee = parse_boom(boom_csv_file)
    bhb_pivot_table, bhb_total_gross_amount, bhb_total_net_amount, bhb_total_fee = parse_bhb(bhb_csv_file)
    cv_pivot_table, cv_total_gross_amount, cv_total_net_amount, cv_total_fee = parse_cv(cv_csv_files)
    acs_pivot_table, acs_total_gross_amount, acs_total_net_amount, acs_total_fee = parse_acs(acs_csv_file)


    # Setup the PDF
    doc = SimpleDocTemplate("parsed_data_output.pdf", pagesize=letter)
    elements = []
    styleSheet = getSampleStyleSheet()
    
    # Title for selected file
    elements.append(Paragraph(f"Selected file: {selected_file}", styleSheet['Title']))
    elements.append(Spacer(1, 0.25 * inch))
    
    # For each DataFrame, convert to Table and add to elements
    for title, df in [("Kings", kings_pivot_table), ("Boom", boom_pivot_table),
                      ("BHB", bhb_pivot_table), ("ClearView", cv_pivot_table), ("ACS", acs_pivot_table)]:
        elements.append(Paragraph(title, styleSheet['Heading2']))
        data, style = dataframe_to_table_style_data(df, font_size=8)
        table = Table(data)
        table.setStyle(style)
        elements.append(table)
        elements.append(Spacer(1, 0.25 * inch))

    doc.build(elements)


    return {
        "kings_pivot_table": kings_pivot_table,
        "kings_total_gross_amount": kings_total_gross_amount,
        "kings_total_net_amount": kings_total_net_amount,
        "kings_total_fee": kings_total_fee,
        "boom_pivot_table": boom_pivot_table,
        "boom_total_gross_amount": boom_total_gross_amount,
        "boom_total_net_amount": boom_total_net_amount,
        "boom_total_fee": boom_total_fee,
        "bhb_pivot_table": bhb_pivot_table,
        "bhb_total_gross_amount": bhb_total_gross_amount,
        "bhb_total_net_amount": bhb_total_net_amount,
        "bhb_total_fee": bhb_total_fee,
        "cv_pivot_table": cv_pivot_table,
        "cv_total_gross_amount": cv_total_gross_amount,
        "cv_total_net_amount": cv_total_net_amount,
        "cv_total_fee": cv_total_fee,
        "acs_pivot_table": acs_pivot_table,
        "acs_total_gross_amount": acs_total_gross_amount,
        "acs_total_net_amount": acs_total_net_amount,
        "acs_total_fee": acs_total_fee
    }

    

    

# Example usage
# kings_csv_file = 'csv/kings.csv'
# boom_csv_file = 'csv/boom.csv'
# bhb_csv_file = 'csv/bhb.csv'
# acs_csv_file = 'csv/acs.csv'
# cv_csv_files = [
#     'csv/dailies_cv/monday.csv',
#     'csv/dailies_cv/tuesday.csv',
#     'csv/dailies_cv/wednesday.csv',
#     'csv/dailies_cv/thursday.csv',
#     'csv/dailies_cv/friday.csv'
# ]

# run_and_print(kings_csv_file, boom_csv_file, bhb_csv_file, acs_csv_file, cv_csv_files)