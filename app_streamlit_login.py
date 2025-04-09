import streamlit as st
# Inicialização segura do estado
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "usuarios" not in st.session_state:
    st.session_state.usuarios = {"admin": "1234"}
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image
import qrcode
import io
import os

# Tamanho padrão da carteirinha (cartão de crédito)
IDCARD = (85.6 * mm, 54 * mm)

def gerar_qrcode(dados):
    qr = qrcode.QRCode(box_size=2, border=2)
    qr.add_data(dados)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")
    
def gerar_carteirinha(nome, curso, matricula, validade, foto):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=IDCARD)
    largura, altura = IDCARD

    # Fundo da carteirinha
    try:
        c.drawImage("fundo_padrao.jpg", 0, 0, width=largura, height=altura)
    except:
        c.setFillColorRGB(0.8, 1, 0.8)
        c.rect(0, 0, largura, altura, fill=True, stroke=False)

    # Foto do aluno
    if foto:
        caminho_foto = "foto_temp.jpg"
        imagem = Image.open(foto)

        # Corrigir rotação automática
        try:
            from PIL import ImageOps
            imagem = ImageOps.exif_transpose(imagem)
        except Exception:
            pass

        imagem = imagem.resize((int(20 * mm), int(25 * mm)))
        imagem.save(caminho_foto)

        c.drawImage(
            caminho_foto,
            5 * mm,
            altura / 12 - -10 * mm,
            width=20 * mm,
            height=25 * mm
        )
        os.remove(caminho_foto)

    # Dados do aluno
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(0, 0, 0)
    base_y = altura - 25 * mm
    linha_altura = 4 * mm

    c.drawString(30 * mm, base_y, f"Nome: {nome}")
    c.drawString(30 * mm, base_y - linha_altura, f"Curso: {curso}")
    c.drawString(30 * mm, base_y - 2 * linha_altura, f"Matrícula: {matricula}")
    c.drawString(30 * mm, base_y - 3 * linha_altura, f"Validade: {validade}")

    # QR Code
    dados_qr = f"Nome: {nome}\nCurso: {curso}\nMatrícula: {matricula}"
    qr_img = gerar_qrcode(dados_qr)
    qr_path = "qr_temp.png"
    qr_img.save(qr_path)

    c.drawImage(
        qr_path,
        largura -22 * mm,
        6 * mm,
        width=17 * mm,
        height=17 * mm
    )
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
    
    if st.button("Gerar Carteirinha"):
        if nome and curso and matricula and validade and foto:
            pdf = gerar_carteirinha(
                nome,
                curso,
                matricula,
                validade.strftime("%d/%m/%Y"),
                foto
            )
            st.download_button(
                "📥 Baixar Carteirinha",
                data=pdf,
                file_name="carteirinha.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Preencha todos os campos obrigatórios.")
