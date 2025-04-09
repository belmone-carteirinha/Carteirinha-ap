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
def gerar_carteirinha(nome, curso, matricula, validade, foto, logotipo, imagem_fundo):
    buffer = io.BytesIO()
    largura, altura = 85.6 * mm, 53.98 * mm
    c = canvas.Canvas(buffer, pagesize=(largura, altura))

    # Fundo
    if imagem_fundo:
        extensao = imagem_fundo.name.split(".")[-1]
        caminho_fundo = f"fundo_temp.{extensao}"
        with open(caminho_fundo, "wb") as f:
            f.write(imagem_fundo.read())
        try:
            c.drawImage(caminho_fundo, 0, 0, width=largura, height=altura)
        except Exception as e:
            st.error(f"Erro ao usar imagem de fundo: {e}")
        os.remove(caminho_fundo)
    else:
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(0, 0, largura, altura, fill=True, stroke=False)

    # Foto
    if foto:
        caminho_foto = "foto_temp.jpg"
        with open(caminho_foto, "wb") as f:
            f.write(foto.read())
        c.drawImage(caminho_foto, 5 * mm, altura - 30 * mm, width=20 * mm, height=25 * mm)
        os.remove(caminho_foto)

    # Dados
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(30 * mm, altura - 15 * mm, f"Nome: {nome}")
    c.drawString(30 * mm, altura - 22 * mm, f"Curso: {curso}")
    c.drawString(30 * mm, altura - 29 * mm, f"Matrícula: {matricula}")
    c.drawString(30 * mm, altura - 36 * mm, f"Validade: {validade}")

    # QR Code
    dados_qr = f"{nome} | {curso} | {matricula}"
    qr_img = gerar_qrcode(dados_qr)
    qr_path = "qr_temp.png"
    qr_img.save(qr_path)
    c.drawImage(qr_path, largura - 18 * mm, 5 * mm, width=15 * mm, height=15 * mm)
    os.remove(qr_path)

    c.save()
    buffer.seek(0)
    return buffer
# Interface de login/cadastro
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
    st.stop()

else:
    st.title("🎓 Gerador de Carteirinha Estudantil")

    nome = st.text_input("Nome completo")
    curso = st.text_input("Curso")
    matricula = st.text_input("Matrícula")
    validade = st.date_input("Validade")
    foto = st.file_uploader("Foto do aluno", type=["jpg", "jpeg", "png"])
    imagem_fundo = st.file_uploader("Imagem de fundo única (opcional)", type=["jpg", "jpeg", "png"])

    if st.button("Gerar Carteirinha"):
        if nome and curso and matricula and validade and foto:
            pdf = gerar_carteirinha(nome, curso, matricula, validade, foto, imagem_fundo)
            
            st.download_button(
    "📥 Baixar Carteirinha",
    data=pdf,
    file_name="carteirinha.pdf",
    mime="application/pdf"
)
        else:
            st.error("Preencha todos os campos obrigatórios.")
