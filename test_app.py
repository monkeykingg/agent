import unittest
from agent import app, db
from agent.models import Agent, User
from agent.commands import forge, initdb
from datetime import datetime, timedelta

class WatchlistTestCase(unittest.TestCase):

    def setUp(self):
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )

        db.create_all()

        user = User(username='Test')
        user.set_password('123')
        agent = Agent(name='Test Title', time=str(datetime.now()), info='{"Access":"0", "URI":"shelter", "Port":"default", "Address":"localhost", "Status":"inactive", "Capacity":"100"}', onto='http://ontology.eil.utoronto.ca/tove/shelter.owl')

        db.session.add_all([user, agent])
        db.session.commit()

        self.client = app.test_client() 
        self.runner = app.test_cli_runner()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_app_exist(self):
        self.assertIsNotNone(app)

    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)

    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Test\'s agent', data)
        self.assertEqual(response.status_code, 200)
    
    def login(self):
        self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)

if __name__ == '__main__':
    unittest.main()