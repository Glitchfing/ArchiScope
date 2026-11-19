"""Generate a compact PDF site climate report."""
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import mm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def create_pdf_report(location, start, end, daily, monthly, insights):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    story = [Paragraph("ArchiScope — Climate Site Analysis", styles["Title"]),
             Paragraph(f"{location.get('name','Selected site')}, {location.get('country','')} | {location['latitude']:.4f}, {location['longitude']:.4f}", styles["Heading2"]),
             Paragraph(f"Analysis period: {start} to {end}", styles["Normal"]), Spacer(1,8)]
    metrics = []
    for col, label, unit, mode in [
        ("mean_temperature_c","Mean temperature","°C","mean"),
        ("mean_relative_humidity_pct","Mean relative humidity","%","mean"),
        ("precipitation_mm","Total precipitation","mm","sum"),
        ("mean_wind_speed_kmh","Mean wind speed","km/h","mean"),
        ("shortwave_radiation_mj_m2","Cumulative shortwave radiation","MJ/m²","sum"),
    ]:
        if col in daily:
            val = daily[col].mean() if mode == "mean" else daily[col].sum()
            metrics.append([label, f"{val:.2f} {unit}"])
    table = Table([["Metric","Value"]] + metrics, colWidths=[95*mm,65*mm])
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#243B53")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.4,colors.grey),("PADDING",(0,0),(-1,-1),6)]))
    story += [table, Spacer(1,10), Paragraph("Monthly climate patterns", styles["Heading1"])]
    plot_cols = [("mean_temperature_c","Monthly mean temperature (°C)"),("precipitation_mm","Monthly precipitation total (mm)"),("mean_relative_humidity_pct","Monthly mean relative humidity (%)")]
    for col, title in plot_cols:
        if col in monthly:
            fig, ax = plt.subplots(figsize=(7,2.2))
            ax.plot(monthly["month_name"], monthly[col], marker="o")
            ax.set_title(title); ax.grid(True, alpha=.25); fig.tight_layout()
            img = BytesIO(); fig.savefig(img, format="png", dpi=130); plt.close(fig); img.seek(0)
            story.append(Image(img, width=165*mm, height=52*mm)); story.append(Spacer(1,5))
    story.append(Paragraph("Preliminary architectural observations", styles["Heading1"]))
    for item in insights:
        story.append(Paragraph(f"<b>{item['parameter']} — {item['measured']}</b>", styles["Heading3"]))
        story.append(Paragraph(f"Rule: {item['rule']}", styles["Italic"]))
        story.append(Paragraph(item["observation"], styles["BodyText"]))
        story.append(Spacer(1,5))
    story += [Spacer(1,8), Paragraph("Data and limitations", styles["Heading1"]),
              Paragraph("Source: Open-Meteo Historical Weather API. Values are historical reanalysis estimates for a grid cell, not on-site sensor readings. Spatial resolution and data availability vary. Shortwave radiation is solar energy and must not be interpreted as sunshine duration. Observations are rule-based screening prompts only; they are not certified climate classification, engineering calculations, building simulation or professional architectural advice.", styles["BodyText"])]
    doc.build(story)
    return buffer.getvalue()
