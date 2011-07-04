import unittest
import etc.arara_settings
import logging
import arara

# Common Test Sets for all tests
class AraraTestBase(unittest.TestCase):
    def setUp(self, use_bot = False, use_database = True):
        self.use_bot = use_bot
        self.use_database = use_database

        # Overwrite Bot-related configuration
        self.org_BOT_ENABLED = etc.arara_settings.BOT_ENABLED
        etc.arara_settings.BOT_ENABLED = use_bot

        # Set Logger
        logging.basicConfig(level=logging.ERROR)

        # Initialize Database
        if use_database:
            arara.model.init_test_database()
            self.engine = arara.arara_engine.ARAraEngine()
        else:
            self.engine = None

    def tearDown(self):
        if self.use_database:
            self.engine.shutdown()
            arara.model.clear_test_database()

        etc.arara_settings.BOT_ENABLED = self.org_BOT_ENABLED
