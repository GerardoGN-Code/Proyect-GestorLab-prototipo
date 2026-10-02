from fpdf import FPDF
import unicodedata

class PDFInstitucional(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Tecnologico de Estudios Superiores de Chimalhuacan', ln=True, align='C')
        
        self.set_font('Arial', 'B', 12)
        self.cell(0, 8, 'Division de Ingenieria en Sistemas Computacionales', ln=True, align='C')
        
        self.set_font('Arial', 'I', 10)
        self.cell(0, 8, 'Horario de Laboratorios Asignados', ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def limpiar_texto_pdf(texto):

    if not texto:
        return ""
    texto = str(texto).replace('\n', ' ').replace('\r', ' ').strip()
    texto = unicodedata.normalize('NFKD', texto).encode('latin-1', 'ignore').decode('latin-1')
    return texto

def exportar_horario_pdf(datos, ruta_salida, titulo_documento, nombre_docente=""):
    pdf = PDFInstitucional(orientation='L', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    if nombre_docente:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 10, f'Docente: {limpiar_texto_pdf(nombre_docente)}', ln=True, align='L')
    
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, limpiar_texto_pdf(titulo_documento), ln=True, align='C')
    pdf.ln(2)
    
    anchos = [20, 95, 30, 20, 20, 85]
    cabeceras = ['Grupo', 'Materia', 'Dia', 'Inicio', 'Fin', 'Laboratorio']
    
    def imprimir_cabecera_tabla():
        pdf.set_font('Arial', 'B', 10)
        pdf.set_fill_color(200, 220, 255)
        for i in range(len(cabeceras)):
            pdf.cell(anchos[i], 10, cabeceras[i], 1, 0, 'C', 1)
        pdf.ln()

    imprimir_cabecera_tabla()
    
    pdf.set_font('Arial', '', 9)
    for fila in datos:

        if pdf.get_y() > 175:
            pdf.add_page()
            imprimir_cabecera_tabla()
            pdf.set_font('Arial', '', 9)

        pdf.cell(anchos[0], 10, limpiar_texto_pdf(fila[0])[:15], 1, 0, 'C')
        pdf.cell(anchos[1], 10, limpiar_texto_pdf(fila[1])[:50], 1, 0, 'L')
        pdf.cell(anchos[2], 10, limpiar_texto_pdf(fila[2])[:15], 1, 0, 'C')
        pdf.cell(anchos[3], 10, limpiar_texto_pdf(fila[3])[:10], 1, 0, 'C')
        pdf.cell(anchos[4], 10, limpiar_texto_pdf(fila[4])[:10], 1, 0, 'C')
        pdf.cell(anchos[5], 10, limpiar_texto_pdf(fila[5])[:45], 1, 0, 'C')
        
        pdf.ln()
        
    pdf.output(ruta_salida)