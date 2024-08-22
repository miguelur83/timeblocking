from fpdf import FPDF
import pandas as pd
import os

def generate_project_colors(project_names):
    # List of pastel colors
    pastel_colors = [
        (200, 220, 255),  # Light Steel Blue
        (200, 255, 200),  # Pale Green
        (255, 215, 160),  # Peach Puff
        (230, 230, 250),  # Lavender
        (255, 240, 200),  # Lemon Chiffon
        (220, 220, 220),  # Gainsboro
        (245, 205, 150),  # Light Goldenrod
        (200, 220, 200),  # Light Mint
        (210, 255, 220),  # Honeydew
        (255, 190, 190),  # Light Coral
        (245, 245, 220),  # Beige
        (240, 200, 200),  # Light Pink
        (230, 240, 200),  # Pale Olive
        (245, 240, 245),  # Lavender Blush
        (255, 180, 180),  # Light Pink
        (245, 245, 220),  # Old Lace
        (220, 180, 180),  # Misty Rose
        (240, 225, 185),  # Light Khaki
        (200, 210, 255),  # Light Sky Blue
        (230, 230, 230),  # Light Gray
    ]
    
    return dict(zip(project_names, pastel_colors[:len(project_names)]))

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Weekly Timetable', 0, 1, 'C')

    def table_header(self, headers, column_widths):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        total_width = sum(column_widths)
        start_x = (210 - total_width) / 2  # Center the table (A4 is 210mm wide)
        self.set_x(start_x)
        for header, width in zip(headers, column_widths):
            self.cell(width, 10, header, 1, 0, 'C', 1)
        self.ln()

    def table_row(self, row, column_widths, project_colors):
        self.set_font('Arial', '', 12)
        total_width = sum(column_widths)
        start_x = (210 - total_width) / 2  # Center the table
        self.set_x(start_x)
        for item, width in zip(row, column_widths):
            color = project_colors.get(item, (255, 255, 255))  # Default to white if no color
            self.set_fill_color(*color)
            self.cell(width, 10, str(item), 1, 0, 'C', 1)
        self.ln()

def generate_pdf(timetable, filename, start_time, end_time, project_names):
    if not isinstance(timetable, pd.DataFrame):
        raise ValueError("Unsupported timetable format")

    pdf = PDF()
    pdf.add_page()

    timetable = timetable.fillna('')

    # Generate time slots
    time_slots = pd.date_range(start=start_time, end=end_time, freq='30min')[:-1].strftime('%H:%M').tolist()

    # Ensure that the number of time slots matches the number of rows in the timetable
    if len(time_slots) != len(timetable):
        raise ValueError("Number of time slots does not match the number of timetable rows")

    # Create a new DataFrame with time slots as the first column
    timetable_with_times = pd.DataFrame({
        'Time': time_slots
    }).join(timetable.reset_index(drop=True))  # Reset index to avoid mismatched rows

    # Generate project colors
    project_colors = generate_project_colors(project_names)

    # Set headers and column widths
    headers = timetable_with_times.columns.tolist()
    column_widths = [180 / len(headers)] * len(headers)

    # Add table header
    pdf.table_header(headers, column_widths)

    # Add table rows
    for _, row in timetable_with_times.iterrows():
        pdf.table_row(row, column_widths, project_colors)

    pdf.output(os.path.join('tmp', filename))
