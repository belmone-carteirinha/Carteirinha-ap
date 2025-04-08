import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import qrcode
from PIL import Image
import os
import io
import time
from datetime import date

USUARIOS = {
    "admin": "1234",
    "adriel": "senha123"
}

if "usuarios" not in st.session_state:
    st.session_state.usuarios = USUARIOS.copy()

def gerar_qrcode(dados):
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(dados)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

pdf = gerar_carteirinha(nome, curso, matricula, validade.strftime("%d/%m/%Y"), foto, logotipo, imagem_fundo)
largura = 85.6 * mm
altura = 53.98 * mm  # Padrão internacional de cartão ID

if imagem_fundo:
        fundo_path = "fundo_temp.jpg"
        with open(fundo_path, "wb") as f:
            f.write(imagem_fundo.read())
        c.drawImage(fundo_path, 0, 0, width=largura, height=altura)
        os.remove(fundo_path)
else:
        c.setFillColorRGB(0.8, 1, 0.8)
        c.rect(0, 0, largura, altura, fill=True, stroke=False)

c = canvas.Canvas(buffer, pagesize=(largura, altura))

    c.setFillColorRGB(0.8, 1, 0.8)
    c.rect(0, 0, largura, altura, fill=True, stroke=False)

    if foto:
        caminho_foto = "foto_temp.jpg"
        with open(caminho_foto, "wb") as f:
            f.write(foto.read())
        c.drawImage(caminho_foto, 5 * mm, altura - 30 * mm, width=20 * mm, height=25 * mm)
        os.remove(caminho_foto)

    dados_qr = f"Nome: {nome}\nCurso: {curso}\nMatrícula: {matricula}"
    qr_img = gerar_qrcode(dados_qr)
    qr_path = "qr_temp.png"
    qr_img.save(qr_path)
    c.drawImage(qr_path, largura - 25 * mm, 5 * mm, width=20 * mm, height=20 * mm)
    os.remove(qr_path)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(30 * mm, altura - 15 * mm, f"Nome: {nome}")
    c.drawString(30 * mm, altura - 22 * mm, f"Curso: {curso}")
    c.drawString(30 * mm, altura - 29 * mm, f"Matrícula: {matricula}")
    c.drawString(30 * mm, altura - 36 * mm, f"Validade: {validade}")

    if logotipo:
        caminho_logo = f"logo_temp.{logotipo.name.split('.')[-1]}"
        with open(caminho_logo, "wb") as f:
            f.write(logotipo.read())
        logo_width = 20 * mm
        logo_height = 15 * mm
        x_central = (largura - logo_width) / 2
        y_base = 5 * mm
        c.drawImage(caminho_logo, x_central, y_base, width=logo_width, height=logo_height)
        c.drawImage(caminho_logo, 5 * mm, y_base, width=logo_width, height=logo_height)
        os.remove(caminho_logo)

    c.save()
    buffer.seek(0)
    return buffer

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Login ou Cadastro")
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
    st.title("🎓 Gerador de Carteirinha Estudantil")

    nome = st.text_input("Nome completo")
    curso = st.text_input("Curso")
    matricula = st.text_input("Matrícula")
    validade = st.date_input("Validade", value=date.today())

    foto = st.file_uploader("Foto do aluno", type=["jpg", "jpeg", "png"])
    logotipo = st.file_uploader("Logotipo da instituição (opcional)", type=["jpg", "jpeg", "png"])
    imagem_fundo = st.file_uploader("Imagem de fundo da carteirinha (opcional)", type=["jpg", "jpeg", "png"])

    if st.button("Gerar Carteirinha"):
        if nome and curso and matricula and validade and foto:
            pdf = gerar_carteirinha(nome, curso, matricula, validade.strftime("%d/%m/%Y"), foto, logotipo)
            st.download_button("📥 Baixar Carteirinha (PDF)", data=pdf, file_name="carteirinha.pdf", mime="application/pdf")
        else:
            st.error("Preencha todos os campos obrigatórios.")
