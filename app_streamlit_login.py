import json
import streamlit as st
import os
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image
import qrcode
import io

USUARIOS_PATH = "usuarios.json"

Funções de usuário

def carregar_usuarios():
if os.path.exists(USUARIOS_PATH):
with open(USUARIOS_PATH, "r") as f:
return json.load(f)
return {"adriel": "adriel1234"}

def salvar_usuarios(usuarios):
with open(USUARIOS_PATH, "w") as f:
json.dump(usuarios, f)

Inicialização de sessão

if "autenticado" not in st.session_state:
st.session_state.autenticado = False
if "usuarios" not in st.session_state:
st.session_state.usuarios = carregar_usuarios()
if "pagina" not in st.session_state:
st.session_state.pagina = "login"

Geração da carteirinha

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

try:  
    c.drawImage("fundo_padrao.jpg", 0, 0, width=largura, height=altura)  
except:  
    c.setFillColorRGB(0.8, 1, 0.8)  
    c.rect(0, 0, largura, altura, fill=True, stroke=False)  

if foto:  
    caminho_foto = "foto_temp.jpg"  
    imagem = Image.open(foto)  
    try:  
        from PIL import ImageOps  
        imagem = ImageOps.exif_transpose(imagem)  
    except:  
        pass  
    imagem = imagem.resize((int(20 * 3.78), int(25 * 3.78)), Image.LANCZOS)  
    imagem.save(caminho_foto)  
    c.drawImage(caminho_foto, 6 * mm, altura / 35 - -16 * mm, width=20 * mm, height=23 * mm)  
    os.remove(caminho_foto)  

c.setFont("Helvetica-Bold", 9)  
c.setFillColorRGB(0, 0, 0)  
base_y = altura - 21 * mm  
linha = 4.5 * mm  
c.drawString(30 * mm, base_y, f"Nome: {nome}")  
c.drawString(30 * mm, base_y - linha, f"Curso: {curso}")  
c.drawString(30 * mm, base_y - 2 * linha, f"Matrícula: {matricula}")  
c.drawString(30 * mm, base_y - 3 * linha, f"Validade: {validade}")  

qr_img = gerar_qrcode(f"Nome: {nome}\nCurso: {curso}\nMatrícula: {matricula}")  
qr_path = "qr_temp.png"  
qr_img.save(qr_path)  
c.drawImage(qr_path, largura - 22 * mm, 6 * mm, width=17 * mm, height=17 * mm)  
os.remove(qr_path)  

c.save()  
buffer.seek(0)  
return buffer

Interface principal

if not st.session_state.autenticado:
st.title("🔐 Login")

opcao = st.radio("Escolha uma opção:", ["Login", "Cadastrar"])  

if opcao == "Login":  
    usuario = st.text_input("Usuário", key="login_usuario")  
    senha = st.text_input("Senha", type="password", key="login_senha")  
      
    if st.button("Entrar"):  
        if usuario in st.session_state.usuarios and st.session_state.usuarios[usuario] == senha:  
            st.session_state.autenticado = True  
            st.session_state.pagina = "principal"  
            st.success("Login realizado com sucesso!")  
            st.stop()  

elif opcao == "Cadastrar":  
    novo_usuario = st.text_input("Novo usuário", key="cadastro_usuario")  
    nova_senha = st.text_input("Nova senha", type="password", key="cadastro_senha")  
    if st.button("Cadastrar"):  
        if novo_usuario in st.session_state.usuarios:  
            st.warning("Usuário já existe.")  
        elif novo_usuario and nova_senha:  
            st.session_state.usuarios[novo_usuario] = nova_senha  
            salvar_usuarios(st.session_state.usuarios)  
            st.success("Usuário cadastrado com sucesso!")  
        else:  
            st.error("Preencha todos os campos.")

elif st.session_state.autenticado and st.session_state.pagina == "principal":
st.title("🎓 Gerador de Carteirinha Estudantil")

nome = st.text_input("Nome completo")  
curso = st.text_input("Curso")  
matricula = st.text_input("Matrícula")  
validade = st.date_input("Validade")  
foto = st.file_uploader("Foto do aluno", type=["jpg", "jpeg", "png"])  

if st.button("Gerar Carteirinha"):  
    if nome and curso and matricula and validade and foto:  
        pdf = gerar_carteirinha(nome, curso, matricula, validade.strftime("%d/%m/%Y"), foto)  
        st.download_button("📥 Baixar Carteirinha", data=pdf, file_name="carteirinha.pdf", mime="application/pdf")  
    else:  
        st.error("Preencha todos os campos.")  

if st.button("Sair"):  
    st.session_state.autenticado = False  
    st.session_state.pagina = "login"  
    st.stop()
