import json
import os
import qrcode
from datetime import datetime
from PIL import Image, ImageOps
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# Caminhos
USUARIOS_PATH = "usuarios.json"
PENDENTES_PATH = "pendentes.json"
CADASTROS_PATH = "cadastros.json"

# ---------- USUÁRIOS ----------

def carregar_usuarios():
    if os.path.exists(USUARIOS_PATH):
        with open(USUARIOS_PATH, "r") as f:
            return json.load(f)
    return {}

def salvar_usuarios(dados):
    with open(USUARIOS_PATH, "w") as f:
        json.dump(dados, f, indent=2)

# ---------- PENDENTES ----------

def carregar_pendentes():
    if os.path.exists(PENDENTES_PATH):
        with open(PENDENTES_PATH, "r") as f:
            return json.load(f)
    return {}

def salvar_pendentes(dados):
    with open(PENDENTES_PATH, "w") as f:
        json.dump(dados, f, indent=2)

# ---------- CADASTROS APROVADOS ----------

def carregar_cadastros():
    if os.path.exists(CADASTROS_PATH):
        with open(CADASTROS_PATH, "r") as f:
            return json.load(f)
    return {}

def salvar_cadastro_completo(usuario, nome, curso, matricula):
    cadastros = carregar_cadastros()
    cadastros[usuario] = {
        "nome": nome,
        "curso": curso,
        "matricula": matricula,
        "data_aprovacao": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    with open(CADASTROS_PATH, "w") as f:
        json.dump(cadastros, f, indent=2)

# ---------- GERAÇÃO DE CARTEIRINHA ----------

IDCARD = (85.6 * mm, 54 * mm)

def gerar_qrcode(dados):
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(dados)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def gerar_carteirinha(nome, curso, matricula, validade, foto):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=IDCARD)
    largura, altura = IDCARD

    try:
        c.drawImage("fundo_padrao.jpg", 0, 0, width=largura, height=altura)
    except:
        c.setFillColorRGB(0.8, 1, 0.8)
        c.rect(0, 0, largura, altura, fill=True, stroke=False)

    # Foto
    if foto:
        caminho_foto = "foto_temp.jpg"
        imagem = Image.open(foto)
        try:
            imagem = ImageOps.exif_transpose(imagem)
        except:
            pass
        imagem = imagem.resize((int(20 * 3.78), int(25 * 3.78)), Image.LANCZOS)
        imagem.save(caminho_foto)
        c.drawImage(caminho_foto, 6 * mm, altura / 35 - -16 * mm, width=20 * mm, height=23 * mm)
        os.remove(caminho_foto)

    # Texto
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(0, 0, 0)
    base_y = altura - 21 * mm
    linha = 4.5 * mm
    c.drawString(30 * mm, base_y, f"Nome: {nome}")
    c.drawString(30 * mm, base_y - linha, f"Curso: {curso}")
    c.drawString(30 * mm, base_y - 2 * linha, f"Matrícula: {matricula}")
    c.drawString(30 * mm, base_y - 3 * linha, f"Validade: {validade}")

    # QR Code
    qr_img = gerar_qrcode(f"Nome: {nome}\nCurso: {curso}\nMatrícula: {matricula}")
    qr_path = "qr_temp.png"
    qr_img.save(qr_path)
    c.drawImage(qr_path, largura - 22 * mm, 6 * mm, width=17 * mm, height=17 * mm)
    os.remove(qr_path)

    c.save()
    buffer.seek(0)
    return buffer
