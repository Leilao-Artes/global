from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from uuid import uuid4
import logging
import urllib.parse
import json
import os

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

def carregar_leiloes():
    if os.path.exists('leiloes.json'):
        with open('leiloes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_leiloes(leiloes):
    with open('leiloes.json', 'w', encoding='utf-8') as f:
        json.dump(leiloes, f, ensure_ascii=False, indent=4)

def generate_uiavatar_urls(title):
    base = "https://ui-avatars.com/api/"
    encoded = urllib.parse.quote(title)
    return [
        {'url': f"{base}?name={encoded}&background=random&color=fff", 'alt': f"Imagem principal de {title}"},
        {'url': f"{base}?name={encoded}+1&background=random&color=fff", 'alt': f"Imagem detalhada de {title}"},
        {'url': f"{base}?name={encoded}+2&background=random&color=fff", 'alt': f"Imagem detalhada de {title}"},
        {'url': f"{base}?name={encoded}+3&background=random&color=fff", 'alt': f"Imagem detalhada de {title}"}
    ]

# Carrega os leilões do JSON
leiloes = carregar_leiloes()

# Atualiza as imagens e total de lances ao carregar
for l in leiloes:
    l['detalhes_imagens'] = generate_uiavatar_urls(l['titulo'])
    l['total_lances'] = len(l.get('historico_lances', []))

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

# Abre a pagina
@app.route('/login')
def login():
    logging.info('Página de login acessada')
    return render_template('login.html')

@app.route('/signup')
def signup():
    logging.info('Página de cadastro acessada')
    return render_template('sign.html')

@app.route('/')
def dashboard():
    for leilao in leiloes:
        # Ajuste para garantir que esse campo exista, caso o leilão seja novo
        if isinstance(leilao.get('tempo_fim'), str):
            leilao['tempo_fim'] = datetime.strptime(leilao['tempo_fim'], '%Y-%m-%d %H:%M:%S')

        leilao['tempo_fim_str'] = leilao['tempo_fim'].strftime('%Y-%m-%d %H:%M:%S')
        leilao['media_avaliacoes_int'] = int(leilao.get('media_avaliacoes', 5) // 1)
    return render_template('dashboard.html', leiloes=leiloes)

@app.route('/leilao/<leilao_id>', methods=['GET', 'POST'])
def leilao_inspecao(leilao_id):
    leilao = next((l for l in leiloes if l['id'] == leilao_id), None)
    if not leilao:
        flash('Leilão não encontrado.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        lance = request.form.get('price')
        nome_usuario = request.form.get('nome') or 'Usuário Anônimo'

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
                salvar_leiloes(leiloes)
                flash(f'Parabéns, {nome_usuario}! Seu lance de €{lance:,.2f} foi registrado com sucesso.', 'success')
            else:
                flash(f'O lance deve ser superior ao lance atual de €{leilao["lance_atual"]:,.2f}.', 'error')
        except ValueError:
            flash('Valor do lance inválido.', 'error')
        
        return redirect(url_for('leilao_inspecao', leilao_id=leilao_id))
    
    leilao['tempo_fim_str'] = leilao['tempo_fim'].strftime('%Y-%m-%d %H:%M:%S')
    leilao['media_avaliacoes_int'] = int(leilao.get('media_avaliacoes', 5) // 1)
    
    return render_template('index.html', leilao=leilao)

@app.route('/criar-leilao', methods=['GET', 'POST'])
def criar_leilao():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        lance_inicial = request.form.get('lance_inicial')
        descricao = request.form.get('descricao')
        local_de_entrega = request.form.get('local_de_entrega')
        ano_fabricacao = request.form.get('ano_fabricacao')
        condicao = request.form.get('condicao')
        horas = request.form.get('horas')

        try:
            lance_inicial = float(lance_inicial)
            ano_fabricacao = int(ano_fabricacao)
            horas = int(horas) if horas else 5
        except ValueError:
            flash('Por favor, insira valores numéricos válidos para lance inicial, ano de fabricação e horas.', 'error')
            return redirect(url_for('criar_leilao'))

        novo_leilao = {
            'id': str(uuid4()),
            'titulo': titulo,
            'lance_atual': lance_inicial,
            'avaliacoes': 0,
            'media_avaliacoes': 5.0,  # padrão
            'descricao': descricao,
            'tempo_fim': (datetime.now() + timedelta(hours=horas)).strftime('%Y-%m-%d %H:%M:%S'),
            'local_de_entrega': local_de_entrega,
            'ano_fabricacao': ano_fabricacao,
            'condicao': condicao,
            'historico_lances': []
        }

        # Gera imagens e total de lances
        novo_leilao['detalhes_imagens'] = generate_uiavatar_urls(novo_leilao['titulo'])
        novo_leilao['total_lances'] = 0

        leiloes.append(novo_leilao)
        salvar_leiloes(leiloes)

        flash('Leilão criado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('criar_leilao.html')

if __name__ == '__main__':
    app.run(debug=True)
