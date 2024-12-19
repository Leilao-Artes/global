import unittest
from flask_testing import TestCase
from app import app, db, User

class TestApp(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        return app

    def setUp(self):
        db.create_all()
        self.client = app.test_client()

        # Create a test user
        self.user = User(name="Test User", email="test@example.com")
        self.user.set_password("password")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, email, password):
        return self.client.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def test_landing_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('landingpage.html')

    def test_login(self):
        response = self.login('test@example.com', 'password')
        self.assertIn(b'Login realizado com sucesso!', response.data)

    def test_invalid_login(self):
        response = self.login('wrong@example.com', 'password')
        self.assertIn(b'Credenciais inválidas. Tente novamente.', response.data)
        self.assertIn('Credenciais inválidas. Tente novamente.'.encode('utf-8'), response.data)
    def test_register(self):
        response = self.client.post('/register', data=dict(
            name="New User",
            email="new@example.com",
            password="password",
            confirm_password="password"
        ), follow_redirects=True)
        self.assertIn(b'Conta criada com sucesso! Faça login.', response.data)
        self.assertIn('Conta criada com sucesso! Faça login.'.encode('utf-8'), response.data)
    def test_logout(self):
        self.login('test@example.com', 'password')
        response = self.logout()
        self.assertIn(b'Você saiu da sua conta.', response.data)
        self.assertIn('Você saiu da sua conta.'.encode('utf-8'), response.data)
    def test_dashboard_access(self):
        self.login('test@example.com', 'password')
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('dashboard.html')

    def test_create_leilao(self):
        self.login('test@example.com', 'password')
        response = self.client.post('/criar-leilao', data=dict(
            titulo="Leilao Teste",
            lance_inicial="100.0",
            descricao="Descricao do leilao",
            local_de_entrega="Local",
            ano_fabricacao="2020",
            condicao="Novo",
            horas="5"
        ), follow_redirects=True)
        self.assertIn(b'Leilão criado com sucesso!', response.data)
        self.assertIn('Leilão criado com sucesso!'.encode('utf-8'), response.data)
    def test_meus_lances(self):
        self.login('test@example.com', 'password')
        response = self.client.get('/meus-lances')
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('meus_lances.html')

if __name__ == '__main__':
    unittest.main()