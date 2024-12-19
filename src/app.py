from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from uuid import uuid4

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Dados mockup aprimorados para múltiplos leilões
leiloes = [
    {
        'id': str(uuid4()),
        'titulo': 'Rolex Daytona Cosmograph Ouro',
        'lance_atual': 35000.00,
        'avaliacoes': 18,
        'media_avaliacoes': 4.9,
        'descricao': 'Rolex Daytona Cosmograph em ouro 18k, modelo 116508. Mostrador verde, movimento automático, cronógrafo. Condição impecável, com certificado de autenticidade e caixa original.',
        'tempo_fim': datetime.now() + timedelta(hours=6, minutes=30),
        'historico_lances': [
            {'nome': 'João Silva', 'valor': 34500.00, 'tempo': '15 minutos atrás', 'imagem': 'https://i.pravatar.cc/40?img=1'},
        ],
        'detalhes_imagens': [
            {'url': 'https://content.rolex.com/dam/2022/upright-bba-with-shadow/m116508-0013.png', 'alt': 'Rolex Daytona Cosmograph Ouro'},
            {'url': 'https://content.rolex.com/dam/2022/upright-bba-with-shadow/m116508-0013_modelpage_front_facing_landscape.png', 'alt': 'Vista frontal do Rolex Daytona'},
            {'url': 'https://content.rolex.com/dam/2022/upright-bba-with-shadow/m116508-0013_modelpage_laying_down_landscape.png', 'alt': 'Detalhe do mostrador do Rolex Daytona'},
            {'url': 'https://content.rolex.com/dam/2022/upright-bba-with-shadow/m116508-0013_modelpage_side_view_landscape.png', 'alt': 'Vista lateral do Rolex Daytona'},
        ]
    },
    {
        'id': str(uuid4()),
        'titulo': 'Bolsa Hermès Birkin 30',
        'lance_atual': 22000.00,
        'avaliacoes': 15,
        'media_avaliacoes': 4.8,
        'descricao': 'Hermès Birkin 30 em couro Togo preto, hardware em paládio. Feita à mão na França, ano 2022. Inclui dust bag, caixa e cartão de autenticidade. Condição nova, nunca usada.',
        'tempo_fim': datetime.now() + timedelta(hours=8, minutes=45),
        'historico_lances': [
            {'nome': 'Ana Pereira', 'valor': 21500.00, 'tempo': '30 minutos atrás', 'imagem': 'https://i.pravatar.cc/40?img=5'},
        ],
        'detalhes_imagens': [
            {'url': 'https://assets.hermes.com/is/image/hermesproduct/birkin-30-bag--072001CK89-front-1-300-0-850-850_b.jpg', 'alt': 'Hermès Birkin 30 em preto'},
            {'url': 'https://assets.hermes.com/is/image/hermesproduct/birkin-30-bag--072001CK89-front-2-300-0-850-850_b.jpg', 'alt': 'Vista frontal da Birkin 30'},
            {'url': 'https://assets.hermes.com/is/image/hermesproduct/birkin-30-bag--072001CK89-back-1-300-0-850-850_b.jpg', 'alt': 'Vista traseira da Birkin 30'},
            {'url': 'https://assets.hermes.com/is/image/hermesproduct/birkin-30-bag--072001CK89-worn-5-300-0-850-850_b.jpg', 'alt': 'Detalhe do fecho da Birkin 30'},
        ]
    },
    {
        'id': str(uuid4()),
        'titulo': 'iPhone 14 Pro Max (1TB)',
        'lance_atual': 1800.00,
        'avaliacoes': 32,
        'media_avaliacoes': 4.9,
        'descricao': 'iPhone 14 Pro Max, 1TB de armazenamento, cor Roxo-profundo. Tela Super Retina XDR de 6,7", câmera tripla de 48MP, chip A16 Bionic. Desbloqueado, na caixa, com todos os acessórios originais.',
        'tempo_fim': datetime.now() + timedelta(hours=4, minutes=15),
        'historico_lances': [
            {'nome': 'Pedro Carvalho', 'valor': 1750.00, 'tempo': '20 minutos atrás', 'imagem': 'https://i.pravatar.cc/40?img=7'},
        ],
        'detalhes_imagens': [
            {'url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-14-pro-finish-select-202209-6-7inch-deeppurple?wid=5120&hei=2880&fmt=p-jpg&qlt=80&.v=1663703841896', 'alt': 'iPhone 14 Pro Max Roxo-profundo'},
            {'url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-14-pro-model-unselect-gallery-1-202209?wid=5120&hei=2880&fmt=p-jpg&qlt=80&.v=1660753619946', 'alt': 'Tela do iPhone 14 Pro Max'},
            {'url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-14-pro-model-unselect-gallery-2-202209_GEO_US?wid=5120&hei=2880&fmt=p-jpg&qlt=80&.v=1660753617560', 'alt': 'Câmeras do iPhone 14 Pro Max'},
            {'url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-14-pro-storage-select-202209-6-7inch-deeppurple?wid=5120&hei=2880&fmt=p-jpg&qlt=80&.v=1660886450413', 'alt': 'iPhone 14 Pro Max de lado'},
        ]
    },
    {
        'id': str(uuid4()),
        'titulo': 'MacBook Pro 16" M2 Max',
        'lance_atual': 3800.00,
        'avaliacoes': 22,
        'media_avaliacoes': 4.8,
        'descricao': 'MacBook Pro 16" (2023) com chip M2 Max, 32GB de RAM, SSD de 1TB. Tela Liquid Retina XDR, Magic Keyboard com Touch ID. Cor Cinza Espacial, na caixa com todos os acessórios originais.',
        'tempo_fim': datetime.now() + timedelta(hours=5, minutes=20),
        'historico_lances': [
            {'nome': 'Luana Faria', 'valor': 3700.00, 'tempo': '45 minutos atrás', 'imagem': 'https://i.pravatar.cc/40?img=9'},
        ],
        'detalhes_imagens': [
            {'url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp16-spacegray-select-202301?wid=904&hei=840&fmt=jpeg&qlt=90&.v=1671304673202', 'alt': 'MacBook Pro 16" M2 Max'},
            {'url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp16-spacegray-gallery1-202301?wid=2000&hei=1536&fmt=jpeg&qlt=95&.v=1670625020727', 'alt': 'Tela do MacBook Pro 16"'},
            {'url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp16-spacegray-gallery2-202301?wid=2000&hei=1536&fmt=jpeg&qlt=95&.v=1670625019635', 'alt': 'Teclado do MacBook Pro 16"'},
            {'url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp16-spacegray-gallery3-202301?wid=2000&hei=1536&fmt=jpeg&qlt=95&.v=1670625016797', 'alt': 'Portas do MacBook Pro 16"'},
        ]
    },
    {
        'id': str(uuid4()),
        'titulo': 'Bicicleta Elétrica Specialized Turbo Vado SL 5.0 EQ',
        'lance_atual': 4500.00,
        'avaliacoes': 14,
        'media_avaliacoes': 4.7,
        'descricao': 'Bicicleta elétrica Specialized Turbo Vado SL 5.0 EQ, modelo 2023. Motor SL 1.1, bateria de 320Wh com autonomia de até 130km. Quadro de alumínio, freios a disco hidráulicos, transmissão Shimano XT de 12 velocidades.',
        'tempo_fim': datetime.now() + timedelta(hours=7, minutes=50),
        'historico_lances': [
            {'nome': 'Carlos Oliveira', 'valor': 4400.00, 'tempo': '1 hora atrás', 'imagem': 'https://i.pravatar.cc/40?img=12'},
        ],
        'detalhes_imagens': [
            {'url': 'https://assets.specialized.com/i/specialized/96220-10_VADO-SL-5-0-STEP-THROUGH-EQ-BLK-DMND-BLK_HERO?bg=rgb(241,241,241)&w=1600&h=900&fmt=auto', 'alt': 'Specialized Turbo Vado SL 5.0 EQ'},
            {'url': 'https://assets.specialized.com/i/specialized/96220-10_VADO-SL-5-0-STEP-THROUGH-EQ-BLK-DMND-BLKFRAM1?bg=rgb(241,241,241)&w=1600&h=900&fmt=auto', 'alt': 'Quadro da Turbo Vado SL'},
            {'url': 'https://assets.specialized.com/i/specialized/96220-10_VADO-SL-5-0-STEP-THROUGH-EQ-BLK-DMND-BLKCOMP1?bg=rgb(241,241,241)&w=1600&h=900&fmt=auto', 'alt': 'Motor da Turbo Vado SL'},
            {'url': 'https://assets.specialized.com/i/specialized/96220-10_VADO-SL-5-0-STEP-THROUGH-EQ-BLK-DMND-BLKDET1?bg=rgb(241,241,241)&w=1600&h=900&fmt=auto', 'alt': 'Detalhes da Turbo Vado SL'},
        ]
    }
]

# O resto do código permanece o mesmo

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

        try:
            lance = float(lance)
            if lance > leilao['lance_atual']:
                leilao['lance_atual'] = lance
                leilao['historico_lances'].insert(0, {
                    'nome': nome_usuario or 'Usuário Anônimo',
                    'valor': lance,
                    'tempo': 'Agora',
                    'imagem': 'https://via.placeholder.com/40'
                })
                flash(f'Parabéns, {nome_usuario or "Usuário Anônimo"}! Seu lance de €{lance:,.2f} foi registrado com sucesso.', 'success')
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
