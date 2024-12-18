from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from uuid import uuid4

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Necessário para usar sessões e flash

# Dados mockup para múltiplos leilões
leiloes = [
    {
        'id': str(uuid4()),
        'titulo': 'Relógio de Luxo Vintage',
        'lance_atual': 15000.00,  # Valor em euros
        'avaliacoes': 12,
        'media_avaliacoes': 5.0,
        'descricao': 'Um relógio raro e elegante dos anos 60, perfeito para colecionadores. Este exemplar único combina o charme vintage com a precisão moderna, oferecendo não apenas um acessório de luxo, mas uma peça da história da relojoaria.',
        'tempo_fim': datetime.now() + timedelta(hours=2, minutes=30),
        'historico_lances': [
            {
                'nome': 'Anibal',
                'valor': 14500.00,
                'tempo': '5 minutos atrás',
                'imagem': 'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/271deea8-e28c-41a3-aaf5-2913f5f48be6/de7834s-6515bd40-8b2c-4dc6-a843-5ac1a95a8b55.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzI3MWRlZWE4LWUyOGMtNDFhMy1hYWY1LTI5MTNmNWY0OGJlNlwvZGU3ODM0cy02NTE1YmQ0MC04YjJjLTRkYzYtYTg0My01YWMxYTk1YThiNTUuanBnIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.BopkDn1ptIwbmcKHdAOlYHyAOOACXW0Zfgbs0-6BY-E'
            },
            {
                'nome': 'Gonçalo',
                'valor': 14000.00,
                'tempo': '10 minutos atrás',
                'imagem': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
            },
            {
                'nome': 'Simão',
                'valor': 13500.00,
                'tempo': '15 minutos atrás',
                'imagem': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
            },
        ],
        'detalhes_imagens': [
            {
                'url': 'https://images.unsplash.com/photo-1523170335258-f5ed11844a49?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
                'alt': 'Vista frontal do relógio'
            },
            {
                'url': 'https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
                'alt': 'Detalhe do mostrador'
            },
            {
                'url': 'https://images.unsplash.com/photo-1618220179428-22790b461013?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
                'alt': 'Vista lateral do relógio'
            },
            {
                'url': 'https://images.unsplash.com/photo-1619946794135-5bc917a27793?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
                'alt': 'Detalhe da pulseira'
            },
        ]
    },
    {
        'id': str(uuid4()),
        'titulo': 'Bolsa de Grife Exclusiva',
        'lance_atual': 8000.00,
        'avaliacoes': 8,
        'media_avaliacoes': 4.8,
        'descricao': 'Uma bolsa de grife exclusiva, modelo limitado. Feita com materiais de alta qualidade e design sofisticado, esta bolsa é ideal para quem valoriza estilo e elegância.',
        'tempo_fim': datetime.now() + timedelta(hours=1, minutes=45),
        'historico_lances': [
            {
                'nome': 'Ana Pereira',
                'valor': 7500.00,
                'tempo': '10 minutos atrás',
                'imagem': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
            },
            {
                'nome': 'Carlos Mendes',
                'valor': 7000.00,
                'tempo': '20 minutos atrás',
                'imagem': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
            },
        ],
        'detalhes_imagens': [
            {
                'url': 'https://images.unsplash.com/photo-1523170335258-f5ed11844a49?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
                'alt': 'Vista frontal da bolsa'
            },
            {
                'url': 'https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
                'alt': 'Detalhe do material'
            },
            {
                'url': 'https://images.unsplash.com/photo-1618220179428-22790b461013?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
                'alt': 'Vista lateral da bolsa'
            },
            {
                'url': 'https://images.unsplash.com/photo-1619946794135-5bc917a27793?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
                'alt': 'Detalhe da alça'
            },
        ]
    },
    # Adicione mais leilões conforme necessário
]

@app.route('/')
def dashboard():
    # Atualize os tempos finais para cada leilão e preprocessar 'media_avaliacoes' para inteiro
    for leilao in leiloes:
        leilao['tempo_fim_str'] = leilao['tempo_fim'].strftime('%Y-%m-%d %H:%M:%S')
        leilao['media_avaliacoes_int'] = int(leilao['media_avaliacoes'] // 1)  # Floor division
    return render_template('dashboard.html', leiloes=leiloes)

@app.route('/leilao/<leilao_id>', methods=['GET', 'POST'])
def leilao_inspecao(leilao_id):
    # Encontre o leilão correspondente
    leilao = next((l for l in leiloes if l['id'] == leilao_id), None)
    if not leilao:
        flash('Leilão não encontrado.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        lance = request.form.get('price')
        nome_usuario = request.form.get('nome')  # Supondo que o usuário envia o nome

        try:
            lance = float(lance)
            if lance > leilao['lance_atual']:
                leilao['lance_atual'] = lance
                leilao['historico_lances'].insert(0, {
                    'nome': nome_usuario or 'Usuário Anônimo',
                    'valor': lance,
                    'tempo': 'Agora',
                    'imagem': 'https://via.placeholder.com/40'  # Placeholder para imagem do usuário
                })
                flash(f'Parabéns, {nome_usuario or "Usuário Anônimo"}! Seu lance de €{lance:,.2f} foi registrado com sucesso.', 'success')
            else:
                flash(f'O lance deve ser superior ao lance atual de €{leilao["lance_atual"]:,.2f}.', 'error')
        except ValueError:
            flash('Valor do lance inválido.', 'error')
        
        return redirect(url_for('leilao_inspecao', leilao_id=leilao_id))
    
    # Formatar o tempo final como string
    leilao['tempo_fim_str'] = leilao['tempo_fim'].strftime('%Y-%m-%d %H:%M:%S')
    
    # Preprocessar 'media_avaliacoes' para inteiro
    leilao['media_avaliacoes_int'] = int(leilao['media_avaliacoes'] // 1)  # Floor division
    
    return render_template('index.html', leilao=leilao)

if __name__ == '__main__':
    app.run(debug=True)
