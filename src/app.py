from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from uuid import uuid4
import logging
import urllib.parse
import os

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import (LoginManager, login_user, current_user, logout_user, 
                         login_required, UserMixin)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Configuração do Banco de Dados SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'leiloes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização do SQLAlchemy e Migrate
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Inicialização do SocketIO para comunicação em tempo real
socketio = SocketIO(app, cors_allowed_origins='*')

# Configuração da pasta de upload
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Configuração de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Rota de login caso o usuário não esteja logado
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"

# Modelos
class User(UserMixin, db.Model):
    """Modelo para os usuários do sistema."""
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    
    # Relação com lances
    lances = db.relationship('Lance', backref='user', lazy=True)

    def set_password(self, password):
        """Define o hash da senha para o usuário."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha fornecida corresponde ao hash armazenado."""
        return check_password_hash(self.password_hash, password)


class Leilao(db.Model):
    """Modelo para os leilões."""
    __tablename__ = 'leiloes'
    id = db.Column(db.String, primary_key=True)
    titulo = db.Column(db.String, nullable=False)
    lance_atual = db.Column(db.Float, nullable=False)
    avaliacoes = db.Column(db.Integer, default=0)
    media_avaliacoes = db.Column(db.Float, default=5.0)
    descricao = db.Column(db.Text, nullable=False)
    tempo_inicio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Novo Campo
    tempo_fim = db.Column(db.DateTime, nullable=False)
    local_de_entrega = db.Column(db.String, nullable=False)
    ano_fabricacao = db.Column(db.Integer, nullable=False)
    condicao = db.Column(db.String, nullable=False)
    total_lances = db.Column(db.Integer, default=0)
    # Novo campo para identificar o usuário criador do leilão
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)

    historico_lances = db.relationship('Lance', backref='leilao', cascade='all, delete-orphan', lazy=True)
    detalhes_imagens = db.relationship('Imagem', backref='leilao', cascade='all, delete-orphan', lazy=True)


class Lance(db.Model):
    """Modelo para os lances nos leilões."""
    __tablename__ = 'lances'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tempo = db.Column(db.String, nullable=False, default='Agora')
    imagem = db.Column(db.String, nullable=False)
    leilao_id = db.Column(db.String, db.ForeignKey('leiloes.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=True)


class Imagem(db.Model):
    """Modelo para as imagens associadas aos leilões."""
    __tablename__ = 'imagens'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    alt = db.Column(db.String, nullable=False)
    leilao_id = db.Column(db.String, db.ForeignKey('leiloes.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    """Carrega o usuário a partir do ID."""
    return User.query.get(user_id)

# Funções auxiliares
def allowed_file(filename):
    """Verifica se o arquivo possui uma extensão permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_uiavatar_urls(title):
    """Gera URLs de avatar utilizando o serviço ui-avatars.com."""
    base = "https://ui-avatars.com/api/"
    encoded = urllib.parse.quote(title)
    return [
        {'url': f"{base}?name={encoded}&background=random&color=fff", 'alt': f"Imagem principal de {title}"},
        {'url': f"{base}?name={encoded}+1&background=random&color=fff", 'alt': f"Imagem detalhada de {title}"},
        {'url': f"{base}?name={encoded}+2&background=random&color=fff", 'alt': f"Imagem detalhada de {title}"},
        {'url': f"{base}?name={encoded}+3&background=random&color=fff", 'alt': f"Imagem detalhada de {title}"}
    ]

def serialize_leilao(leilao):
    """Serializa os dados de um leilão para JSON."""
    return {
        'id': leilao.id,
        'titulo': leilao.titulo,
        'lance_atual': leilao.lance_atual,
        'avaliacoes': leilao.avaliacoes,
        'media_avaliacoes': leilao.media_avaliacoes,
        'descricao': leilao.descricao,
        'tempo_inicio': leilao.tempo_inicio.strftime('%Y-%m-%d %H:%M:%S'),
        'tempo_fim': leilao.tempo_fim.strftime('%Y-%m-%d %H:%M:%S'),
        'local_de_entrega': leilao.local_de_entrega,
        'ano_fabricacao': leilao.ano_fabricacao,
        'condicao': leilao.condicao,
        'total_lances': leilao.total_lances
    }

# Rotas de autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota para login de usuários.
    GET: Exibe o formulário de login.
    POST: Processa as credenciais e autentica o usuário.
    """
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
    """
    Rota para registro de novos usuários.
    GET: Exibe o formulário de registro.
    POST: Processa os dados e cria um novo usuário.
    """
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
    """
    Rota para logout de usuários.
    """
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

# Rotas principais
@app.route('/')
def landing_page():
    """
    Rota da página inicial que exibe os 4 primeiros leilões ativos.
    """
    agora = datetime.utcnow()
    leiloes_ativos = Leilao.query.filter(Leilao.tempo_fim > agora).order_by(Leilao.tempo_fim.asc()).limit(4).all()
    
    return render_template('landingpage.html', leiloes=leiloes_ativos, agora=agora)

#rota documentacao
@app.route('/documentacao')
def documentacao():
    """
    Rota da página de documentação.
    """
    return render_template('doc.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Rota do dashboard que exibe os leilões com opções de pesquisa, filtros, paginação e seleção dinâmica de layout.
    """
    # Parâmetros de pesquisa e filtro
    q = request.args.get('q', '').strip()
    ano_fabricacao = request.args.get('ano_fabricacao', '').strip()
    condicao = request.args.get('condicao', '').strip()
    ordenar = request.args.get('ordenar', '').strip()
    status = request.args.get('status', 'all').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 18  # Número de leilões por página
    cards_per_row = request.args.get('cards_per_row', 3, type=int)  # Número de cards por linha

    query = Leilao.query

    # Filtro por pesquisa de título
    if q:
        query = query.filter(Leilao.titulo.ilike(f"%{q}%"))
    
    # Filtro por ano de fabricação
    if ano_fabricacao:
        try:
            ano_fabricacao_int = int(ano_fabricacao)
            query = query.filter(Leilao.ano_fabricacao == ano_fabricacao_int)
        except ValueError:
            flash('Ano de fabricação inválido.', 'error')
    
    # Filtro por condição
    if condicao:
        query = query.filter(Leilao.condicao == condicao)
    
    # Filtro por status
    agora = datetime.utcnow()
    if status == 'active':
        query = query.filter(Leilao.tempo_fim > agora)
    elif status == 'finished':
        query = query.filter(Leilao.tempo_fim <= agora)
    elif status == 'participated':
        # Filtra os leilões nos quais o usuário atual participou
        leilao_ids = [l.leilao_id for l in current_user.lances]
        query = query.filter(Leilao.id.in_(leilao_ids))

    # Ordenações
    if ordenar == 'lance':
        query = query.order_by(Leilao.lance_atual.asc())
    elif ordenar == 'tempo':
        query = query.order_by(Leilao.tempo_fim.asc())
    else:
        query = query.order_by(Leilao.tempo_fim.desc())  # Ordenação padrão

    # Limitar o número de cards por linha (máximo 6)
    if cards_per_row not in [1, 2, 3, 4, 5, 6]:
        cards_per_row = 3

    # Paginação
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    leiloes = pagination.items

    # Anos disponíveis para filtros
    anos_disponiveis = [str(ano) for ano in range(1900, datetime.utcnow().year + 1)]

    # Serialização dos leilões para JavaScript
    leiloes_data = [serialize_leilao(l) for l in leiloes]

    return render_template(
        'dashboard.html',
        leiloes=leiloes,
        leiloes_data=leiloes_data,
        anos_disponiveis=anos_disponiveis,
        agora=agora,
        pagination=pagination,
        status=status,
        q=q,
        ano_fabricacao=ano_fabricacao,
        condicao=condicao,
        ordenar=ordenar,
        cards_per_row=cards_per_row
    )



@app.route('/leilao/<leilao_id>', methods=['GET', 'POST'])
@login_required
def leilao_inspecao(leilao_id):
    """
    Rota para inspecionar um leilão específico.
    GET: Exibe os detalhes do leilão.
    POST: Processa um novo lance.
    """
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
                    leilao=leilao,
                    user_id=current_user.id
                )
                db.session.add(novo_lance)
                leilao.total_lances += 1
                db.session.commit()
                flash(f'Parabéns, {nome_usuario}! Seu lance de €{lance:,.2f} foi registrado com sucesso.', 'success')
                
                # Emite atualização em tempo real
                socketio.emit('new_bid', {
                    'leilao_id': leilao.id,
                    'lance_atual': leilao.lance_atual,
                    'nome': nome_usuario
                }, room=leilao.id)
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
    """
    Rota para criação de novos leilões.
    """
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
            tempo_inicio=datetime.utcnow(),
            tempo_fim=datetime.utcnow() + timedelta(hours=horas),
            local_de_entrega=local_de_entrega,
            ano_fabricacao=ano_fabricacao,
            condicao=condicao,
            total_lances=0,
            user_id=current_user.id # Associa o leilão ao usuário logado
        )
        db.session.add(novo_leilao)
        db.session.commit()

        flash('Leilão criado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('criar_leilao.html')

@app.route('/meus-lances')
@login_required
def meus_lances():
    """
    Rota que exibe todos os lances do usuário atual.
    """
    meus_lances = Lance.query.filter_by(user_id=current_user.id).all()
    lances_info = []
    for lance in meus_lances:
        leilao = Leilao.query.filter_by(id=lance.leilao_id).first()
        if not leilao:
            continue
        status = "Ganhando" if lance.valor == leilao.lance_atual else "Ultrapassado"
        if datetime.utcnow() > leilao.tempo_fim:
            status = "Leilão Encerrado"
        lances_info.append({
            'titulo': leilao.titulo,
            'valor': lance.valor,
            'tempo': lance.tempo,
            'leilao_id': leilao.id,
            'lance_atual': leilao.lance_atual,
            'status': status
        })
    return render_template('meus_lances.html', lances_info=lances_info)

# Nova rota "Os meus leilões"
@app.route('/meus-leiloes')
@login_required
def meus_leiloes():
    """
    Rota que exibe todos os leilões criados pelo usuário atual.
    """
    agora = datetime.utcnow()
    # Filtra os leilões criados pelo usuário atual
    leiloes_do_usuario = Leilao.query.filter_by(user_id=current_user.id).all()

    leiloes_info = []
    for leilao in leiloes_do_usuario:
        encerrado = leilao.tempo_fim < agora
        ganhador = None
        if encerrado:
            # Determina o vencedor: lance com valor == lance_atual
            vencedor_lance = Lance.query.filter_by(leilao_id=leilao.id, valor=leilao.lance_atual).first()
            if vencedor_lance:
                ganhador = vencedor_lance.nome

        leiloes_info.append({
            'id': leilao.id,
            'titulo': leilao.titulo,
            'lance_atual': leilao.lance_atual,
            'encerrado': encerrado,
            'ganhador': ganhador
        })

    return render_template('meus_leiloes.html', leiloes=leiloes_info)


# Eventos SocketIO
@socketio.on('join_leilao')
def on_join(data):
    """
    Evento para um usuário entrar em uma sala de leilão.
    """
    leilao_id = data['leilao_id']
    join_room(leilao_id)
    emit('room_joined', {'msg': f'Entrou no leilão {leilao_id}'}, room=leilao_id)

@socketio.on('leave_leilao')
def on_leave(data):
    """
    Evento para um usuário sair de uma sala de leilão.
    """
    leilao_id = data['leilao_id']
    leave_room(leilao_id)
    emit('room_left', {'msg': f'Saiu do leilão {leilao_id}'}, room=leilao_id)

@socketio.on('request_update')
def handle_request_update(data):
    """
    Evento para solicitar uma atualização dos dados de um leilão.
    """
    leilao_id = data.get('leilao_id')
    if not leilao_id:
        emit('update_error', {'msg': 'ID do leilão não fornecido.'})
        return

    leilao = Leilao.query.filter_by(id=leilao_id).first()
    if not leilao:
        emit('update_error', {'msg': 'Leilão não encontrado.'})
        return

    leilao_data = serialize_leilao(leilao)
    emit('update_leilao', leilao_data)

@app.context_processor
def inject_favicon():
    return {
        'favicon': """
            <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,
            <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='orange'>
                <circle cx='10' cy='10' r='8'/>
            </svg>">
        """
    }

    
with app.app_context():
        db.create_all()
    
if __name__ == '__main__':
        logging.debug('Iniciando o servidor...')
        socketio.run(app, debug=True)
        logging.debug('Servidor encerrado.')
