class User:

    def __init__(self, username):
        self.username = username

    def hello(self):
        return "Hello,", self.username