from catstuff import tools

raise NotImplementedError

class Parser(tools.argparser.CSArgParser):
    def __init__(self):
        super().__init__(description='Performs numerous database operations on the catstuff master collection')
        self.add_argument('operation')

