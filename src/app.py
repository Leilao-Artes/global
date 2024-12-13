from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    # Dados mockup para o leilão
    leilao = {
        'titulo': 'Relógio de Luxo Vintage',
        'lance_atual': '€ 15.000',
        'avaliacoes': 12,
        'media_avaliacoes': 5.0,
        'descricao': 'Um relógio raro e elegante dos anos 60, perfeito para colecionadores. Este exemplar único combina o charme vintage com a precisão moderna, oferecendo não apenas um acessório de luxo, mas uma peça de história horológica.',
        'tempo_restante': '02:30:00',
        'historico_lances': [
            {
                'nome': 'João Silva',
                'valor': '€ 14.500',
                'tempo': '5 minutos atrás',
                'imagem': 'https://images.unsplash.com/photo-1519345182560-3f2917c472ef?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
            },
            {
                'nome': 'Luis Santos',
                'valor': '€ 14.500',
                'tempo': '5 minutos atrás',
                'imagem': 'https://images.unsplash.com/photo-1519345182560-3f2917c472ef?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
            },
            {
                'nome': 'Maria Santos',
                'valor': '€ 14.000',
                'tempo': '15 minutos atrás',
                'imagem': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
            },
            # Adicione mais lances conforme necessário
        ],
        'detalhes_imagens': [
            {
                'url': 'https://images.unsplash.com/photo-1523170335258-f5ed11844a49?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
                'alt': 'Detalhe 1'
            },
            {
                'url': 'https://images.unsplash.com/photo-1587836374828-4dbafa94cf0e?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
                'alt': 'Detalhe 2'
            },
            {
                'url': 'https://images.unsplash.com/photo-1618220179428-22790b461013?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
                'alt': 'Detalhe 3'
            },
            {
                'url': 'https://images.unsplash.com/photo-1619946794135-5bc917a27793?ixlib=rb-1.2.1&auto=format&fit=crop&w=300&q=80',
                'alt': 'Detalhe 4'
            },
            # Adicione mais imagens detalhadas conforme necessário
        ]
    }

    return render_template('index.html', leilao=leilao)

if __name__ == '__main__':
    app.run(debug=True)
