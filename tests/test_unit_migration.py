from iconsdk.wallet.wallet import KeyWallet
from iconservice import Address
from iconservice.base.exception import IconScoreException
from tbears.libs.scoretest.score_test_case import ScoreTestCase
from dividends.dividends import Dividends
from tbears.config.tbears_config import TEST_ACCOUNTS


class DividendsUnit(ScoreTestCase):
    def setUp(self):
        super().setUp()
        self.mock_score = Address.from_string(f"cx{'abcd' * 10}")
        self.dividends = self.get_score_instance(Dividends, self.test_account1)
        self.wallet_array = [KeyWallet.load(v) for v in TEST_ACCOUNTS]
        account_info = {Address.from_string(wallet.get_address()): 10 ** 21 for wallet in self.wallet_array}
        self.initialize_accounts(account_info)

    def test_migrate(self):
        self.dividends._batch_size.set(13)
        for wallet in self.wallet_array:
            self.dividends._stake_holders.put(wallet.get_address())

        while not self.dividends._stake_holders_migration_complete.get():
            self.dividends._migrate_stake_holders()

        for idx, wallet in enumerate(self.wallet_array):
            self.assertEqual(idx + 1, self.dividends._stake_holders_index[self.wallet_array[idx].get_address()])
