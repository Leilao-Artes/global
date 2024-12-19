from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from uuid import uuid4
import logging
import urllib.parse
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Inicialização do Flask
app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Caminho base e configuração do banco SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'leiloes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do SQLAlchemy e Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Pasta de upload
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # rota de login caso o user não esteja logado
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"

# Modelos
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Leilao(db.Model):
    __tablename__ = 'leiloes'
    id = db.Column(db.String, primary_key=True)
    titulo = db.Column(db.String, nullable=False)
    lance_atual = db.Column(db.Float, nullable=False)
    avaliacoes = db.Column(db.Integer, default=0)
    media_avaliacoes = db.Column(db.Float, default=5.0)
    descricao = db.Column(db.Text, nullable=False)
    tempo_fim = db.Column(db.DateTime, nullable=False)
    local_de_entrega = db.Column(db.String, nullable=False)
    ano_fabricacao = db.Column(db.Integer, nullable=False)
    condicao = db.Column(db.String, nullable=False)
    total_lances = db.Column(db.Integer, default=0)
    historico_lances = db.relationship('Lance', backref='leilao', cascade='all, delete-orphan', lazy=True)
    detalhes_imagens = db.relationship('Imagem', backref='leilao', cascade='all, delete-orphan', lazy=True)


class Lance(db.Model):
    __tablename__ = 'lances'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tempo = db.Column(db.String, nullable=False, default='Agora')
    imagem = db.Column(db.String, nullable=False)
    leilao_id = db.Column(db.String, db.ForeignKey('leiloes.id'), nullable=False)


class Imagem(db.Model):
    __tablename__ = 'imagens'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    alt = db.Column(db.String, nullable=False)
    leilao_id = db.Column(db.String, db.ForeignKey('leiloes.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Funções auxiliares
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_uiavatar_urls(title):
    base = "https://ui-avatars.com/api/"
    encoded = urllib.parse.quote(title)
    return [
        {'url': f"{base}?name={encoded}&background=random&color=fff", 'alt': f"Imagem principal de {title}"},
        {'url': f"{base}?name={encoded}+1&background=random&color=fff", 'alt': f"Imagem detalhada de {title}"},
        {'url': f"{base}?name={encoded}+2&background=random&color=fff", 'alt': f"Imagem detalhada de {title}"},
        {'url': f"{base}?name={encoded}+3&background=random&color=fff", 'alt': f"Imagem detalhada de {title}"}
    ]

def serialize_leilao(leilao):
    return {
        'id': leilao.id,
        'titulo': leilao.titulo,
        'lance_atual': leilao.lance_atual,
        'avaliacoes': leilao.avaliacoes,
        'media_avaliacoes': leilao.media_avaliacoes,
        'descricao': leilao.descricao,
        'tempo_fim': leilao.tempo_fim.strftime('%Y-%m-%d %H:%M:%S'),
        'local_de_entrega': leilao.local_de_entrega,
        'ano_fabricacao': leilao.ano_fabricacao,
        'condicao': leilao.condicao,
        'total_lances': leilao.total_lances
    }

# Rotas de autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    logging.info('Página de login acessada')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    logging.info('Página de cadastro acessada')
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('As senhas não conferem.', 'error')
            return redirect(url_for('register'))

        user_exist = User.query.filter_by(email=email).first()
        if user_exist:
            flash('Já existe um usuário com este email.', 'error')
            return redirect(url_for('register'))

        new_user = User(name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

# Rotas principais
@app.route('/')
def dashboard():
    leiloes = Leilao.query.all()
    for leilao in leiloes:
        leilao.tempo_fim_str = leilao.tempo_fim.strftime('%Y-%m-%d %H:%M:%S')
        leilao.media_avaliacoes_int = int(leilao.media_avaliacoes)
    leiloes_data = [serialize_leilao(l) for l in leiloes]
    return render_template('dashboard.html', leiloes=leiloes, leiloes_data=leiloes_data)

@app.route('/leilao/<leilao_id>', methods=['GET', 'POST'])
@login_required
def leilao_inspecao(leilao_id):
    leilao = Leilao.query.filter_by(id=leilao_id).first()
    if not leilao:
        flash('Leilão não encontrado.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        lance = request.form.get('price')
        nome_usuario = current_user.name if current_user.is_authenticated else 'Usuário Anônimo'
        try:
            lance = float(lance)
            if lance > leilao.lance_atual:
                leilao.lance_atual = lance
                novo_lance = Lance(
                    nome=nome_usuario,
                    valor=lance,
                    tempo='Agora',
                    imagem=f'https://ui-avatars.com/api/?name={urllib.parse.quote(nome_usuario)}&background=ccc&color=000',
                    leilao=leilao
                )
                db.session.add(novo_lance)
                leilao.total_lances += 1
                db.session.commit()
                flash(f'Parabéns, {nome_usuario}! Seu lance de €{lance:,.2f} foi registrado com sucesso.', 'success')
            else:
                flash(f'O lance deve ser superior ao lance atual de €{leilao.lance_atual:,.2f}.', 'error')
        except ValueError:
            flash('Valor do lance inválido.', 'error')
        
        return redirect(url_for('leilao_inspecao', leilao_id=leilao_id))
    
    leilao.tempo_fim_str = leilao.tempo_fim.strftime('%Y-%m-%d %H:%M:%S')
    leilao.media_avaliacoes_int = int(leilao.media_avaliacoes)
    return render_template('index.html', leilao=leilao)

@app.route('/criar-leilao', methods=['GET', 'POST'])
@login_required
def criar_leilao():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        lance_inicial = request.form.get('lance_inicial')
        descricao = request.form.get('descricao')
        local_de_entrega = request.form.get('local_de_entrega')
        ano_fabricacao = request.form.get('ano_fabricacao')
        condicao = request.form.get('condicao')
        horas = request.form.get('horas', '5')

        try:
            lance_inicial = float(lance_inicial)
            ano_fabricacao = int(ano_fabricacao)
            horas = int(horas) if horas else 5
        except ValueError:
            flash('Por favor, insira valores numéricos válidos para lance inicial, ano de fabricação e horas.', 'error')
            return redirect(url_for('criar_leilao'))
        
        novo_leilao_id = str(uuid4())
        
        # Upload das imagens
        imagens_upload = request.files.getlist('imagens')
        imagens_salvas = []
        for img in imagens_upload:
            if img and allowed_file(img.filename):
                extensao = img.filename.rsplit('.', 1)[1].lower()
                filename = f"{novo_leilao_id}_{uuid4()}.{extensao}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                img.save(filepath)
                imagem = Imagem(
                    url=url_for('static', filename='uploads/' + filename),
                    alt=f"Imagem de {titulo}",
                    leilao_id=novo_leilao_id
                )
                db.session.add(imagem)
                imagens_salvas.append(imagem)
        
        # Caso não haja imagens enviadas, gera imagens via avatar
        if not imagens_salvas:
            urls_avatar = generate_uiavatar_urls(titulo)
            for img_data in urls_avatar:
                imagem = Imagem(
                    url=img_data['url'],
                    alt=img_data['alt'],
                    leilao_id=novo_leilao_id
                )
                db.session.add(imagem)
        
        novo_leilao = Leilao(
            id=novo_leilao_id,
            titulo=titulo,
            lance_atual=lance_inicial,
            avaliacoes=0,
            media_avaliacoes=5.0,
            descricao=descricao,
            tempo_fim=datetime.now() + timedelta(hours=horas),
            local_de_entrega=local_de_entrega,
            ano_fabricacao=ano_fabricacao,
            condicao=condicao,
            total_lances=0
        )
        db.session.add(novo_leilao)
        db.session.commit()

        flash('Leilão criado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('criar_leilao.html')


# Criação das tabelas
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
