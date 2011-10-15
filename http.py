from twisted.web.resource import Resource

class RepositoryRequest(Resource):
    def __init__(self, repository):
        Resource.__init__(self)
        self.repository = repository

    def render_GET(self, request):
        return self.repository

class GitHTTP(Resource):
    def getChild(self, name, request):
        return RepositoryRequest(name)

    def render_GET(self, request):
        return "hello world"
    