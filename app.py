import os
import io
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import cm

app = Flask(__name__)

# Configurações fixas baseadas no modelo
INTRODUCAO_TEXTO = """
Este Plano de Trabalho apresenta as etapas e condições comerciais para a implantação e utilização da plataforma Govplan. 
Nosso objetivo é proporcionar eficiência, transparência e conformidade legal em todo o processo de planejamento de compras públicas.
"""

CONTEMPLA_TEXTO = """
<b>Implantação</b><br/>
• Criação da regulamentação do PCA<br/>
• Configurações iniciais e treinamento do sistema<br/>
<b>Elaboração</b><br/>
• Registro das demandas das áreas<br/>
• Análise e unificação das contratações<br/>
• Aprovação e publicação do PCA<br/>
<b>Execução</b><br/>
• Acompanhamento do calendário de contratações<br/>
• Alertas e monitoramento de prazos<br/>
<b>Controle e Gestão</b><br/>
• Monitoramento por dashboards<br/>
• Ajustes durante o exercício<br/>
• Relatórios de riscos<br/>
<b>ETP – Base do Planejamento</b><br/>
• Elaboração de ETP´s completos e guiados com apoio de inteligência artificial
"""

INDICADO_BASICO = "Órgãos com equipe reduzida que precisam estruturar o PCA com segurança, previsibilidade orçamentária e conformidade legal."
INDICADO_PERSONALIZADO = "Órgãos que desejam fortalecer o planejamento desde a origem da demanda, garantindo governança, rastreabilidade e maior tranquilidade para gestores e equipes técnicas."

def add_background(canvas, doc):
    canvas.saveState()
    bg_path = os.path.join(app.root_path, 'static', 'images', 'template.png')
    if os.path.exists(bg_path):
        canvas.drawImage(bg_path, 0, 0, width=A4[0], height=A4[1])
    canvas.restoreState()

def generate_pdf(data):
    buffer = io.BytesIO()
    # Margens ajustadas: topMargin reduzida para subir o título
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=2*cm, 
        leftMargin=2*cm, 
        topMargin=2.5*cm, 
        bottomMargin=2.5*cm
    )
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, spaceAfter=20, fontSize=20, textColor=colors.HexColor('#1a237e'), leading=24)
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], spaceBefore=15, spaceAfter=10, fontSize=16, textColor=colors.HexColor('#1a237e'))
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=12, leading=16, alignment=4)
    
    elements = []

    # --- PÁGINA 1 ---
    # Título (Subido)
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"PLANO DE TRABALHO PARA {data['orgao'].upper()}", title_style))
    
    # Introdução
    elements.append(Paragraph("Introdução", heading_style))
    elements.append(Paragraph(INTRODUCAO_TEXTO, normal_style))
    
    # Cronograma (Embelezado)
    elements.append(Paragraph("CRONOGRAMA", heading_style))
    elements.append(Spacer(1, 0.5*cm))
    
    for i, etapa in enumerate(data['cronograma']):
        # Ícone de círculo preenchido para todas as etapas
        icon = "●"
        
        # Tabela para cada item do cronograma com linha vertical simulada
        item_table = Table([
            [Paragraph(f"<font size=18 color='#7cb342'>{icon}</font>", ParagraphStyle('Bullet', alignment=1)), 
             Paragraph(f"<b>{etapa['data']}</b>", normal_style), 
             Paragraph(etapa['descricao'], normal_style)]
        ], colWidths=[1.2*cm, 3.8*cm, 12*cm])
        
        item_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            # Adiciona uma linha vertical entre os ícones (exceto no último)
            ('LINEBEFORE', (0, 0), (0, 0), 1, colors.HexColor('#7cb342')) if i < len(data['cronograma']) - 1 else ('LINEBEFORE', (0, 0), (0, 0), 0, colors.white),
        ]))
        # Nota: O ReportLab não desenha linhas verticais facilmente entre tabelas separadas, 
        # mas o espaçamento e o ícone maior já dão um visual muito superior.
        elements.append(item_table)

    elements.append(PageBreak())

    # --- PÁGINA 2 ---
    elements.append(Spacer(1, 0.5*cm))
    # Título da seção maior
    elements.append(Paragraph("Cenários para contratação do Govplan:", ParagraphStyle('CenTitle', parent=heading_style, fontSize=18)))
    elements.append(Spacer(1, 0.5*cm))
    
    # Tabela de Cenários (Aumentada)
    col_width = 8.5*cm
    
    # Cabeçalho
    header_table = Table([
        [Paragraph("<b>PLANO BÁSICO</b>", ParagraphStyle('Header', alignment=1, textColor=colors.white, fontSize=14)), 
         Paragraph("<b>VALOR PERSONALIZADO</b>", ParagraphStyle('Header', alignment=1, textColor=colors.white, fontSize=14))]
    ], colWidths=[col_width, col_width])
    
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#1a237e')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#7cb342')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(header_table)

    # Conteúdo (Aumentado e com mais espaçamento)
    cenarios_content = [
        [Paragraph(f"<b>Usuários:</b> {data['basico_usuarios']} usuário", normal_style), 
         Paragraph(f"<b>Usuários:</b> {data['perso_usuarios']} usuários", normal_style)],
        
        [Paragraph(f"<b>Valor anual:</b> R$ {data['basico_valor']}", normal_style), 
         Paragraph(f"<b>Valor anual:</b> {data['perso_valor']}", normal_style)],
        
        [Paragraph("<b>O que contempla:</b><br/>" + CONTEMPLA_TEXTO, ParagraphStyle('Small', parent=normal_style, fontSize=10, leading=13)), 
         Paragraph("<b>O que contempla:</b><br/>" + CONTEMPLA_TEXTO, ParagraphStyle('Small', parent=normal_style, fontSize=10, leading=13))],
        
        [Paragraph(f"<b>Diferenciais:</b><br/>N/A", ParagraphStyle('Small', parent=normal_style, fontSize=10, leading=13)), 
         Paragraph(f"<b>Diferenciais:</b><br/>{data['perso_diferenciais']}", ParagraphStyle('Small', parent=normal_style, fontSize=10, leading=13))],
        
        [Paragraph(f"<b>Indicado para:</b> {INDICADO_BASICO}", ParagraphStyle('Small', parent=normal_style, fontSize=10, leading=13)), 
         Paragraph(f"<b>Indicado para:</b> {INDICADO_PERSONALIZADO}", ParagraphStyle('Small', parent=normal_style, fontSize=10, leading=13))]
    ]
    
    content_table = Table(cenarios_content, colWidths=[col_width, col_width])
    content_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(content_table)

    doc.build(elements, onFirstPage=add_background, onLaterPages=add_background)
    buffer.seek(0)
    return buffer

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = {
            'orgao': request.form.get('orgao'),
            'cliente': request.form.get('cliente'),
            'tipo_orgao': request.form.get('tipo_orgao'),
            'basico_usuarios': request.form.get('basico_usuarios'),
            'basico_valor': request.form.get('basico_valor'),
            'perso_usuarios': request.form.get('perso_usuarios'),
            'perso_valor': request.form.get('perso_valor'),
            'perso_diferenciais': request.form.get('perso_diferenciais'),
            'cronograma': []
        }
        
        datas = request.form.getlist('cron_data[]')
        descricoes = request.form.getlist('cron_desc[]')
        
        for d, desc in zip(datas, descricoes):
            if d and desc:
                data['cronograma'].append({'data': d, 'descricao': desc})
        
        pdf_buffer = generate_pdf(data)
        
        if 'visualizar' in request.form:
            return send_file(pdf_buffer, as_attachment=False, mimetype='application/pdf')
        
        filename = f"Plano_de_Trabalho_{data['orgao'].replace(' ', '_')}.pdf"
        return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
