"""
Mock Confluence PDF Generator.
Creates a realistic sample requirements document for testing the pipeline.
Run this script to generate tests/sample_requirements.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem,
    Table, TableStyle, HRFlowable
)
from pathlib import Path


def create_sample_pdf():
    """Generate a mock Confluence-exported requirements PDF."""

    output_dir = Path(__file__).resolve().parent
    output_path = output_dir / "sample_requirements.pdf"

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=22,
        textColor=HexColor('#1a1a2e'),
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#2d3436'),
        spaceBefore=20,
        spaceAfter=8,
    )

    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=HexColor('#636e72'),
        spaceBefore=14,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=8,
    )

    # Build content
    story = []

    # ── Title ──
    story.append(Paragraph("User Management System — Requirements Specification", title_style))
    story.append(Paragraph("Project: Enterprise Portal v3.0 | Confluence Space: PROJ", body_style))
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#dfe6e9')))
    story.append(Spacer(1, 12))

    # ── Section 1: User Registration ──
    story.append(Paragraph("1. User Registration", heading_style))
    story.append(Paragraph(
        "The system shall allow new users to register for an account. "
        "Users can sign up using their email address or social login providers.",
        body_style
    ))

    story.append(Paragraph("1.1 Registration Fields", subheading_style))
    bullets = [
        "Full name (first and last name)",
        "Email address",
        "Password",
        "Phone number (optional)",
        "Company name",
        "Role selection",
    ]
    for b in bullets:
        story.append(Paragraph(f"• {b}", body_style))

    story.append(Paragraph("1.2 Validation Rules", subheading_style))
    story.append(Paragraph(
        "Email must be unique in the system. Password must meet security requirements. "
        "The system should validate all inputs.",
        body_style
    ))

    # ── Section 2: Password Reset ──
    story.append(Paragraph("2. Password Reset", heading_style))
    story.append(Paragraph(
        "User can reset password. The system sends a reset link to the user's email. "
        "User clicks the link and enters a new password.",
        body_style
    ))

    story.append(Paragraph("2.1 Reset Flow", subheading_style))
    reset_steps = [
        "User clicks 'Forgot Password' on login page",
        "User enters their email address",
        "System sends reset email",
        "User clicks reset link",
        "User enters new password",
        "System confirms password change",
    ]
    for i, step in enumerate(reset_steps, 1):
        story.append(Paragraph(f"{i}. {step}", body_style))

    # ── Section 3: User Profile ──
    story.append(Paragraph("3. User Profile Management", heading_style))
    story.append(Paragraph(
        "Users should be able to update their profile information. "
        "The profile page should display user details and allow editing.",
        body_style
    ))

    profile_fields = [
        "Display name",
        "Avatar/profile picture",
        "Bio/description",
        "Contact information",
        "Notification preferences",
        "Language settings",
    ]

    story.append(Paragraph("Editable fields:", body_style))
    for f in profile_fields:
        story.append(Paragraph(f"• {f}", body_style))

    # ── Section 4: Role-Based Access ──
    story.append(Paragraph("4. Role-Based Access Control", heading_style))
    story.append(Paragraph(
        "The system must support different user roles with varying permissions. "
        "Administrators can manage roles and permissions.",
        body_style
    ))

    # Role table
    table_data = [
        ['Role', 'Permissions', 'Description'],
        ['Admin', 'Full access', 'System administrators'],
        ['Manager', 'Read, Write, Approve', 'Team managers'],
        ['User', 'Read, Write', 'Standard users'],
        ['Viewer', 'Read only', 'External stakeholders'],
    ]

    table = Table(table_data, colWidths=[1.5 * inch, 2 * inch, 2.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2d3436')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#dfe6e9')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f5f6fa'), HexColor('#ffffff')]),
    ]))
    story.append(Spacer(1, 8))
    story.append(table)

    # ── Section 5: Notifications ──
    story.append(Paragraph("5. Notifications", heading_style))
    story.append(Paragraph(
        "The system should notify users about important events. "
        "Users can configure their notification preferences.",
        body_style
    ))

    notif_types = [
        "Account-related notifications (registration, password change)",
        "System notifications (maintenance, updates)",
        "Activity notifications (mentions, assignments)",
        "Email and in-app notification channels",
    ]
    for n in notif_types:
        story.append(Paragraph(f"• {n}", body_style))

    # ── Section 6: Audit Logging ──
    story.append(Paragraph("6. Audit Logging", heading_style))
    story.append(Paragraph(
        "All user actions should be logged for compliance. "
        "The audit log should be searchable and exportable.",
        body_style
    ))

    # ── Confluence Footer (noise) ──
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#dfe6e9')))
    story.append(Paragraph(
        "Powered by Atlassian Confluence | Exported on 2025-01-15 | Space: PROJ",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=HexColor('#b2bec3'))
    ))

    # Build PDF
    doc.build(story)
    print(f"Sample PDF created: {output_path}")
    return output_path


if __name__ == "__main__":
    create_sample_pdf()
