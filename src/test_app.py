# tests.py

import os
from datetime import datetime, timedelta
from uuid import uuid4
import random
import urllib.parse

# Importa os objetos do seu aplicativo Flask
from app import app, db, Leilao, Imagem

def generate_uiavatar_urls(title):
    """Gera URLs de avatar utilizando o serviço ui-avatars.com."""
    base = "https://ui-avatars.com/api/"
    encoded = urllib.parse.quote(title)
    return [
        {'url': f"{base}?name={encoded}&background=random&color=fff", 'alt': f"Imagem principal de {title}"},
        {'url': f"{base}?name={encoded}+1&background=random&color=fff", 'alt': f"Imagem detalhada 1 de {title}"},
        {'url': f"{base}?name={encoded}+2&background=random&color=fff", 'alt': f"Imagem detalhada 2 de {title}"},
        {'url': f"{base}?name={encoded}+3&background=random&color=fff", 'alt': f"Imagem detalhada 3 de {title}"}
    ]

def create_leiloes(n=150):
    """
    Cria 'n' leilões com dados fictícios e os adiciona ao banco de dados.
    """
    with app.app_context():
        for i in range(1, n + 1):
            leilao_id = str(uuid4())
            titulo = f"Leilão {i}"
            lance_inicial = round(random.uniform(10.0, 100.0), 2)
            descricao = f"Descrição detalhada para o {titulo}."
            local_de_entrega = f"Cidade {random.randint(1, 100)}"
            ano_fabricacao = random.randint(1990, datetime.now().year)
            condicao = random.choice(['Novo', 'Usado', 'Recondicionado'])
            horas = random.randint(1, 168)  # Até 7 dias
            tempo_fim = datetime.now() + timedelta(hours=horas)

            # Cria uma instância de Leilao
            novo_leilao = Leilao(
                id=leilao_id,
                titulo=titulo,
                lance_atual=lance_inicial,
                avaliacoes=0,
                media_avaliacoes=5.0,
                descricao=descricao,
                tempo_inicio=datetime.utcnow(),
                tempo_fim=tempo_fim,
                local_de_entrega=local_de_entrega,
                ano_fabricacao=ano_fabricacao,
                condicao=condicao,
                total_lances=0,
                user_id='user_id_exemplo'  # Substitua por um ID válido de usuário
            )
            db.session.add(novo_leilao)

            # Gera URLs de imagens usando UI Avatars
            urls_avatar = generate_uiavatar_urls(titulo)

            # Adiciona as imagens ao banco de dados
            for img_data in urls_avatar:
                imagem = Imagem(
                    url=img_data['url'],
                    alt=img_data['alt'],
                    leilao_id=leilao_id
                )
                db.session.add(imagem)
        
        # Salva todas as alterações no banco de dados
        db.session.commit()
        print(f"{n} leilões foram criados com sucesso.")

if __name__ == '__main__':
    create_leiloes()
