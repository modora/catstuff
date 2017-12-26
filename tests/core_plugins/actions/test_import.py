from tests.classes import CSDBBaseTest
from catstuff.core_plugins.actions.import_ import Import

class Test_dir_1(CSDBBaseTest):
    def setup(self):
        self.obj = Import()

    def test_file_list(self):
        self.obj.main()