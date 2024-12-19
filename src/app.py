from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from uuid import uuid4
import urllib.parse

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

def generate_uiavatar_urls(title):
    # Gera 4 imagens diferentes usando o título do item
    # Usamos urllib.parse.quote para URL encode do título.
    base = "https://ui-avatars.com/api/"
    encoded = urllib.parse.quote(title)
    # Podemos variar o background para cada imagem
    # ui-avatars parameters: ?name=John+Doe&background=random&color=fff
    return [
        {'url': f"{base}?name={encoded}&background=random&color=fff", 'alt': f"Imagem principal de {title}"},
        {'url': f"{base}?name={encoded}+1&background=random&color=fff", 'alt': f"Imagem detalhada de {title}"},
        {'url': f"{base}?name={encoded}+2&background=random&color=fff", 'alt': f"Imagem detalhada de {title}"},
        {'url': f"{base}?name={encoded}+3&background=random&color=fff", 'alt': f"Imagem detalhada de {title}"}
    ]

# Dados mockup de artes
leiloes = [
    {
        'id': str(uuid4()),
        'titulo': 'Pintura Impressionista de Claude Monet',
        'lance_atual': 50000.00,
        'avaliacoes': 42,
        'media_avaliacoes': 4.9,
        'descricao': 'Uma rara pintura impressionista de Claude Monet, autêntica, com certificado. Moldura original e excelente estado de conservação.',
        'tempo_fim': datetime.now() + timedelta(hours=6),
        'local_de_entrega': 'Paris, França',
        'ano_fabricacao': 1902,
        'condicao': 'Excelente',
        'historico_lances': [
            {'nome': 'João Silva', 'valor': 49000.00, 'tempo': '15 minutos atrás', 'imagem': 'https://ui-avatars.com/api/?name=Joao+Silva&background=ccc&color=000'},
        ],
    },
    {
        'id': str(uuid4()),
        'titulo': 'Escultura Contemporânea em Bronze',
        'lance_atual': 12000.00,
        'avaliacoes': 18,
        'media_avaliacoes': 4.7,
        'descricao': 'Escultura única em bronze, obra de artista contemporâneo renomado. Inclui documentação e base expositora.',
        'tempo_fim': datetime.now() + timedelta(hours=8),
        'local_de_entrega': 'Lisboa, Portugal',
        'ano_fabricacao': 2019,
        'condicao': 'Como Nova',
        'historico_lances': [
            {'nome': 'Ana Pereira', 'valor': 11500.00, 'tempo': '30 minutos atrás', 'imagem': 'https://ui-avatars.com/api/?name=Ana+Pereira&background=ccc&color=000'},
        ],
    },
    {
        'id': str(uuid4()),
        'titulo': 'Fotografia Fine-Art de Ansel Adams',
        'lance_atual': 3000.00,
        'avaliacoes': 25,
        'media_avaliacoes': 4.8,
        'descricao': 'Fotografia analógica em preto e branco de Ansel Adams, impressa em papel de alta qualidade, estado impecável.',
        'tempo_fim': datetime.now() + timedelta(hours=3),
        'local_de_entrega': 'Nova Iorque, EUA',
        'ano_fabricacao': 1942,
        'condicao': 'Excelente',
        'historico_lances': [
            {'nome': 'Pedro Carvalho', 'valor': 2900.00, 'tempo': '20 minutos atrás', 'imagem': 'https://ui-avatars.com/api/?name=Pedro+Carvalho&background=ccc&color=000'},
        ],
    }
]

# Gerando as imagens usando uiavatars
for l in leiloes:
    l['detalhes_imagens'] = generate_uiavatar_urls(l['titulo'])
    l['total_lances'] = len(l['historico_lances'])

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('sign.html')

@app.route('/')
def dashboard():
    for leilao in leiloes:
        leilao['tempo_fim_str'] = leilao['tempo_fim'].strftime('%Y-%m-%d %H:%M:%S')
        leilao['media_avaliacoes_int'] = int(leilao['media_avaliacoes'] // 1)
    return render_template('dashboard.html', leiloes=leiloes)

@app.route('/leilao/<leilao_id>', methods=['GET', 'POST'])
def leilao_inspecao(leilao_id):
    leilao = next((l for l in leiloes if l['id'] == leilao_id), None)
    if not leilao:
        flash('Leilão não encontrado.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        lance = request.form.get('price')
        nome_usuario = request.form.get('nome')
        nome_usuario = nome_usuario or 'Usuário Anônimo'

        try:
            lance = float(lance)
            if lance > leilao['lance_atual']:
                leilao['lance_atual'] = lance
                leilao['historico_lances'].insert(0, {
                    'nome': nome_usuario,
                    'valor': lance,
                    'tempo': 'Agora',
                    'imagem': f'https://ui-avatars.com/api/?name={urllib.parse.quote(nome_usuario)}&background=ccc&color=000'
                })
                leilao['total_lances'] = len(leilao['historico_lances'])
                flash(f'Parabéns, {nome_usuario}! Seu lance de €{lance:,.2f} foi registrado com sucesso.', 'success')
            else:
                flash(f'O lance deve ser superior ao lance atual de €{leilao["lance_atual"]:,.2f}.', 'error')
        except ValueError:
            flash('Valor do lance inválido.', 'error')
        
        return redirect(url_for('leilao_inspecao', leilao_id=leilao_id))
    
    leilao['tempo_fim_str'] = leilao['tempo_fim'].strftime('%Y-%m-%d %H:%M:%S')
    leilao['media_avaliacoes_int'] = int(leilao['media_avaliacoes'] // 1)
    
    return render_template('index.html', leilao=leilao)

if __name__ == '__main__':
    app.run(debug=True)
