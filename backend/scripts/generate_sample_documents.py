"""Generate realistic pharmaceutical complaint documents for the demo.

Creates sample_data/*.pdf, *.eml and *.txt covering the cases worth showing:
a critical particulate complaint, a labeling error, a documentation/CoA query,
a duplicate of the first one, and a deliberately incomplete email (to show the
Completeness Checker asking follow-up questions).

Run:  python scripts/generate_sample_documents.py
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).resolve().parent.parent / "sample_data"
OUT.mkdir(exist_ok=True)

CRITICAL_PARTICULATE = """CUSTOMER COMPLAINT NOTIFICATION

To: Quality Assurance, Vertexa Pharma Ltd (API Division)
From: Quality Control, Nordwell Formulations GmbH
Complaint Date: 2026-03-04
Complaint Source: Email

Product Name: Metformin Hydrochloride IP
Product Strength / Grade: USP Grade, D90 45 um
Batch / Lot Number: MTF-2509-118
Manufacturing Date: 2025-11-18
Expiry Date: 2027-11-17
Quantity Affected: 125 kg (5 drums of 25 kg)

Description of Complaint:
During dispensing of the above batch our operators observed black fibrous particulate
matter in two of the five HDPE drums received. The particulate is visible against the
white powder bed and was found on the surface as well as approximately 40 mm into the
powder. The material is intended for a sterile-adjacent oral solid dosage line and the
affected batch has been quarantined. One intermediate blend prepared before detection
has also been placed on hold pending your investigation.

We consider this a critical quality defect and request your investigation report,
including a review of the drum liner supplier and the milling area, within 10 working days.
Photographs and a retained sample of the particulate are available on request.

Regards,
Dr. Anke Feld
Head of Quality Control, Nordwell Formulations GmbH
"""

LABELING_ERROR = """CUSTOMER COMPLAINT FORM

Customer Name: Meridian Health Distributors Pvt Ltd
Complaint Source: Distributor
Complaint Date: 04/03/2026

Product Name: Atorvastatin Calcium Tablets
Product Strength: 20 mg
Batch Number: ATV-2601-044
Mfg Date: 2026-01-09
Expiry Date: 2028-01-08
Quantity Affected: 1200 packs

Complaint Details:
The secondary carton for the above batch shows the storage statement
"Store below 25 C" while the blister foil printed on the same batch states
"Store below 30 C". Retail pharmacists in two districts have queried the
discrepancy. There is no impact on tablet appearance, count or identity.
No adverse events have been reported. We have stopped further dispatch of the
batch from our Nagpur warehouse and request a corrected artwork confirmation
and a plan for the stock already in trade.

Reported by: Sanjay Rao, Regulatory Affairs, Meridian Health Distributors
"""

COA_QUERY = """From: qa@brightline-labs.com
To: complaints@vertexa-pharma.com
Subject: CoA discrepancy - Paracetamol IP batch PCM-2512-207
Date: Mon, 02 Mar 2026 09:41:00 +0530

Dear Quality Assurance team,

We received Paracetamol IP (API), batch PCM-2512-207, manufactured on 2025-12-14
with expiry 2028-12-13, quantity 500 kg.

The Certificate of Analysis issued with the consignment reports residual solvent
(isopropyl alcohol) as "Not more than 0.5%" whereas the specification in our approved
supplier dossier states "Not more than 0.1%". The assay and related substances results
are within limits. This appears to be a documentation error rather than a product
quality failure, but we cannot release the material against the current CoA.

Please confirm the correct specification and reissue the CoA. Our internal reference is
BL-COMP-2026-018.

Kind regards,
Priya Menon
Quality Assurance Officer, Brightline Labs
"""

DUPLICATE_PARTICULATE = """From: a.feld@nordwell-formulations.de
To: complaints@vertexa-pharma.com
Subject: FOLLOW-UP - black particulate, Metformin HCl batch MTF-2509-118
Date: Fri, 06 Mar 2026 11:05:00 +0100

Dear QA team,

Further to our notification of 4 March 2026 regarding black fibrous particulate matter
found in Metformin Hydrochloride IP batch MTF-2509-118 (125 kg affected, mfg 2025-11-18,
exp 2027-11-17), we have now inspected the remaining three drums and found similar
particles in a third drum. Please treat this as an extension of the same complaint.

Regards,
Dr. Anke Feld
Nordwell Formulations GmbH
"""

INCOMPLETE_EMAIL = """From: warehouse@citycare-pharmacy.in
To: complaints@vertexa-pharma.com
Subject: problem with a recent delivery
Date: Tue, 03 Mar 2026 16:22:00 +0530

Hi,

Some of the bottles in the shipment we got last week are leaking and the labels have
come off. Please advise what to do with them. It is the cough syrup we usually order.

Thanks
Ramesh
"""


def write_pdf(filename: str, title: str, body: str) -> None:
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "body", parent=styles["BodyText"], fontName="Helvetica", fontSize=10, leading=14
    )
    title_style = ParagraphStyle(
        "title", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, spaceAfter=8
    )
    document = SimpleDocTemplate(
        str(OUT / filename),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=title,
    )
    flowables = [Paragraph(title, title_style), Spacer(1, 4)]
    for block in body.strip().split("\n\n"):
        flowables.append(Paragraph(block.replace("\n", "<br/>"), body_style))
        flowables.append(Spacer(1, 8))
    document.build(flowables)


def main() -> None:
    write_pdf("complaint_01_critical_particulate.pdf", "Customer Complaint Notification", CRITICAL_PARTICULATE)
    write_pdf("complaint_02_labeling_error.pdf", "Customer Complaint Form", LABELING_ERROR)
    (OUT / "complaint_03_coa_discrepancy.eml").write_text(COA_QUERY, encoding="utf-8")
    (OUT / "complaint_04_duplicate_particulate.eml").write_text(DUPLICATE_PARTICULATE, encoding="utf-8")
    (OUT / "complaint_05_incomplete_email.txt").write_text(INCOMPLETE_EMAIL, encoding="utf-8")
    for path in sorted(OUT.iterdir()):
        print("wrote", path.relative_to(OUT.parent))


if __name__ == "__main__":
    main()
