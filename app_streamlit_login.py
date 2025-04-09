import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image
import qrcode
import io
import os

# Usuários pré-cadastrados
USUARIOS = {
    "admin": "1234",
    "adriel": "senha123"
}

if "usuarios" not in st.session_state:
    st.session_state.usuarios = USUARIOS.copy()

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

# Função para gerar QR Code
def gerar_qrcode(dados):
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(dados)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

# Função para gerar carteirinha com imagem de fundo
def gerar_carteirinha(nome, curso, matricula, validade, foto, imagem_fundo):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(85.6 * mm, 53.98 * mm))
    largura, altura = 85.6 * mm, 53.98 * mm

    # Imagem de fundo
    if imagem_fundo:
        caminho_fundo = f"fundo_temp.{imagem_fundo.name.split('.')[-1]}"
        with open(caminho_fundo, "wb") as f:
            f.write(imagem_fundo.read())
        c.drawImage(caminho_fundo, 0, 0, width=largura, height=altura)
        os.remove(caminho_fundo)
    else:
        c.setFillColorRGB(0.8, 1, 0.8)
        c.rect(0, 0, largura, altura, fill=True, stroke=False)

    # # Foto no centro esquerdo
foto_largura = 20 * mm
foto_altura = 25 * mm
x_foto = 5 * mm  # margem da esquerda
y_foto = (altura - foto_altura) / 2  # centralizado
c.drawImage(caminho_foto, x_foto, y_foto, width=foto_largura, height=foto_altura)

    base_y = altura - 15 * mm
linha_altura = 3 * mm  # espaçamento menor

c.drawString(30 * mm, base_y, f"Nome: {nome}")
c.drawString(30 * mm, base_y - linha_altura, f"Curso: {curso}")
c.drawString(30 * mm, base_y - 2 * linha_altura, f"Matrícula: {matricula}")
c.drawString(30 * mm, base_y - 3 * linha_altura, f"Validade: {validade}")

    # QR Code
    dados_qr = f"Nome: {nome}\nCurso: {curso}\nMatrícula: {matricula}"
    qr_img = gerar_qrcode(dados_qr)
    qr_path = "qr_temp.png"
    qr_img.save(qr_path)
    c.drawImage(qr_path, largura - 18 * mm, 5 * mm, width=15 * mm, height=15 * mm)
    os.remove(qr_path)

    c.save()
    buffer.seek(0)
    return buffer

# Interface de login/cadastro
if not st.session_state.autenticado:
    st.title("🔐 Login")
    menu = st.radio("Escolha uma opção:", ["Login", "Cadastrar novo usuário"])

    if menu == "Login":
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            if usuario in st.session_state.usuarios and st.session_state.usuarios[usuario] == senha:
                st.session_state.autenticado = True
                st.success("Login realizado com sucesso!")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos")

    elif menu == "Cadastrar novo usuário":
        novo_usuario = st.text_input("Novo usuário")
        nova_senha = st.text_input("Nova senha", type="password")
        if st.button("Cadastrar"):
            if novo_usuario in st.session_state.usuarios:
                st.warning("Usuário já existe.")
            elif novo_usuario and nova_senha:
                st.session_state.usuarios[novo_usuario] = nova_senha
                st.success("Usuário cadastrado com sucesso!")
            else:
                st.error("Preencha todos os campos.")
else:
    # Interface principal
    st.title("🎓 Gerador de Carteirinha Estudantil")

    nome = st.text_input("Nome completo")
    curso = st.text_input("Curso")
    matricula = st.text_input("Matrícula")
    validade = st.date_input("Validade")
    foto = st.file_uploader("Foto do aluno", type=["jpg", "jpeg", "png"])
    imagem_fundo = st.file_uploader("Imagem de fundo única (opcional)", type=["jpg", "jpeg", "png"])

    if st.button("Gerar Carteirinha"):
        if nome and curso and matricula and validade and foto:
            pdf = gerar_carteirinha(
                nome,
                curso,
                matricula,
                validade.strftime("%d/%m/%Y"),
                foto,
                imagem_fundo
            )
            st.download_button(
                "📥 Baixar Carteirinha",
                data=pdf,
                file_name="carteirinha.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Preencha todos os campos obrigatórios.")
