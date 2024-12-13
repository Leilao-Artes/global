# Tutorial de Testes Simples em Python

Os testes são uma parte essencial do desenvolvimento de software. Eles ajudam a garantir que o código funcione conforme o esperado. Neste tutorial, vamos criar um teste simples em Python usando a biblioteca `unittest`.

## Passo 1: Instalar o `unittest`

O `unittest` é uma biblioteca padrão do Python, então não é necessário instalá-la separadamente. Ela já vem incluída com a instalação do Python.

## Passo 2: Criar um Arquivo de Teste

Crie um arquivo chamado `test_example.py` no seu diretório de projeto.

## Passo 3: Escrever o Código a Ser Testado

Vamos criar uma função simples para ser testada. Crie um arquivo chamado `example.py` e adicione o seguinte código:

```python
def soma(a, b):
    return a + b
```

## Passo 4: Escrever o Teste

No arquivo `test_example.py`, adicione o seguinte código:

```python
import unittest
from example import soma

class TestSoma(unittest.TestCase):
    def test_soma(self):
        self.assertEqual(soma(1, 2), 3)
        self.assertEqual(soma(-1, 1), 0)
        self.assertEqual(soma(0, 0), 0)

if __name__ == '__main__':
    unittest.main()
```

## Passo 5: Executar o Teste

Para executar o teste, abra o terminal, navegue até o diretório onde o arquivo `test_example.py` está localizado e execute o seguinte comando:

```sh
python -m unittest test_example.py
```

Se tudo estiver correto, você verá uma saída indicando que todos os testes passaram.

## Conclusão

Neste tutorial, aprendemos como criar um teste simples em Python usando a biblioteca `unittest`. Testes são fundamentais para garantir a qualidade do código e devem ser uma prática constante no desenvolvimento de software.