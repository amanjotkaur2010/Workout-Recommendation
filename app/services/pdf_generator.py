import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_workout_pdf(user, plan):
    """
    Generates a professional PDF report of the active workout program.
    Returns a BytesIO stream containing the PDF data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom colors
    primary_color = colors.HexColor('#6366f1')
    secondary_color = colors.HexColor('#1a1a1e')
    text_color = colors.HexColor('#2d3748')
    bg_light = colors.HexColor('#f7fafc')
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#718096'),
        spaceAfter=20
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=16,
        leading=20,
        textColor=secondary_color,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor=text_color
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )
    
    # Header Section
    story.append(Paragraph(f"AI Workout Recommendation Program", title_style))
    story.append(Paragraph(f"Generated for {user.username} | Goal: {plan.goal} | Split: {plan.frequency} Days per Week", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Profile & Nutrition Targets Table
    profile = user.profile
    if profile:
        targets_data = [
            [
                Paragraph("<b>Height:</b>", body_style), Paragraph(f"{profile.height} cm", body_style),
                Paragraph("<b>Calorie Target:</b>", body_style), Paragraph(f"{int(profile.calorie_target or 2000)} kcal", body_style)
            ],
            [
                Paragraph("<b>Weight:</b>", body_style), Paragraph(f"{profile.weight} kg", body_style),
                Paragraph("<b>Water Target:</b>", body_style), Paragraph(f"{int(profile.water_target or 2500)} ml", body_style)
            ],
            [
                Paragraph("<b>Fitness Level:</b>", body_style), Paragraph(f"{profile.fitness_level}", body_style),
                Paragraph("<b>Activity Level:</b>", body_style), Paragraph(f"{profile.activity_level}", body_style)
            ]
        ]
        targets_table = Table(targets_data, colWidths=[100, 150, 120, 150])
        targets_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_light),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 8),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        story.append(targets_table)
        story.append(Spacer(1, 20))
        
    # Group plan exercises by day of the week
    weekly_schedule = {}
    for pe in plan.plan_exercises:
        day = pe.day_of_week
        if day not in weekly_schedule:
            weekly_schedule[day] = []
        weekly_schedule[day].append(pe)
        
    day_order = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
    sorted_days = sorted(list(weekly_schedule.keys()), key=lambda d: day_order.get(d, 8))
    
    # Exercise listing for each day
    for day in sorted_days:
        story.append(Paragraph(f"{day} Workout", section_heading))
        
        # Columns: Exercise, Target Muscle, Sets, Reps, Rest, Description
        table_data = [[
            Paragraph("Exercise", table_header_style),
            Paragraph("Target Muscle", table_header_style),
            Paragraph("Sets", table_header_style),
            Paragraph("Reps", table_header_style),
            Paragraph("Rest", table_header_style),
            Paragraph("Instructions Summary", table_header_style)
        ]]
        
        for pe in weekly_schedule[day]:
            exc = pe.exercise
            # Truncate description slightly for PDF fit
            desc = exc.description or ""
            if len(desc) > 100:
                desc = desc[:97] + "..."
                
            table_data.append([
                Paragraph(f"<b>{exc.name}</b>", body_style),
                Paragraph(exc.target_muscle, body_style),
                Paragraph(str(pe.sets), body_style),
                Paragraph(str(pe.reps), body_style),
                Paragraph(f"{pe.rest_time}s", body_style),
                Paragraph(desc, body_style)
            ])
            
        # Table Layout sizes: Total letter page width width = 612. Margin left/right is 40. Usable width is 532.
        day_table = Table(table_data, colWidths=[100, 80, 40, 40, 40, 232])
        day_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), primary_color),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 6),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e0')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ]))
        
        story.append(day_table)
        story.append(Spacer(1, 15))
        
    # Build Document
    doc.build(story)
    buffer.seek(0)
    return buffer
