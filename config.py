class Configuration:

    def get(self, scheme, property):
        return {
            'repositoryBasePath': '/home/christophe/Desktop/repositories'
        }[property]

config = Configuration()