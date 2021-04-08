from iconservice import *

TAG = 'DIVS'
DIVIDEND_CATEGORIES = ["_tap", "_gamedev", "_promo", "_platform"]


# An interface of token to distribute daily dividends
class TokenInterface(InterfaceScore):
    @interface
    def balanceOf(self, _owner: Address) -> int:
        pass

    @interface
    def totalSupply(self) -> int:
        pass

    @interface
    def get_balance_updates(self) -> dict:
        pass

    @interface
    def clear_yesterdays_changes(self) -> bool:
        pass

    @interface
    def switch_address_update_db(self) -> None:
        pass

    # staking updates
    @interface
    def clear_yesterdays_stake_changes(self) -> bool:
        pass

    @interface
    def get_stake_updates(self) -> dict:
        pass

    @interface
    def switch_stake_update_db(self) -> None:
        pass

    @interface
    def total_staked_balance(self) -> int:
        pass


# An interface of roulette score to get batch size
class GameInterface(InterfaceScore):
    @interface
    def get_batch_size(self, recip_count: int) -> int:
        pass

    @interface
    def get_treasury_status(self) -> bool:
        pass


# An interface to game authorization score to get excess made by each game
class GameAuthorizationInterface(InterfaceScore):

    @interface
    def get_revshare_wallet_address(self, _scoreAddress: Address) -> Address:
        pass

    @interface
    def get_yesterdays_games_excess(self) -> dict:
        pass


class Dividends(IconScoreBase):
    _DIVS_DIST_COMPLETE = "dist_complete"

    _TAP_DIST_INDEX = "dist_index"
    _BATCH_SIZE = "batch_size"

    _TAP_HOLDERS = "holders"
    _TAP_BALANCES = "balances"

    _TOTAL_DIVS = "total_divs"
    _REMAINING_TAP_DIVS = "remaining_divs"
    _REMAINING_GAMEDEV_DIVS = "remaining_gamedev_divs"
    _PLATFORM_DIVS = "platform_divs"
    _PROMO_DIVS = "promo_divs"

    _TOTAL_ELIGIBLE_TAP_TOKENS = "remaining_tokens"
    _BLACKLIST_ADDRESS = "blacklist_addresses"
    _INHOUSE_GAMES = "inhouse_games"

    _GAMES_LIST = "games_list"
    _GAMES_EXCESS = "games_excess"
    _REVSHARE_WALLET_ADDRESS = "revshare_wallet_address"

    _DIVIDEND_PERCENTAGE = "dividend_percentage"

    _TOKEN_SCORE = "token_score"
    _GAME_SCORE = "game_score"
    _PROMO_SCORE = "promo_score"
    _GAME_AUTH_SCORE = "game_auth_score"
    _DIVIDENDS_RECEIVED = "dividends_received"

    _STAKE_HOLDERS = "stake_holders"
    _STAKE_BALANCES = "stake_balances"
    _TOTAL_ELIGIBLE_STAKED_TAP_TOKENS = "total_eligible_staked_tap_tokens"
    _STAKE_DIST_INDEX = "stake_dist_index"

    _SWITCH_DIVIDENDS_TO_STAKED_TAP = "switch_dividends_to_staked_tap"

    _EXCEPTION_ADDRESS = "exception_address"

    @eventlog(indexed=2)
    def FundTransfer(self, winner: str, amount: int, note: str):
        pass

    @eventlog(indexed=2)
    def DivsReceived(self, total_divs: int, batch_size: int):
        pass

    @eventlog(indexed=1)
    def BlacklistAddress(self, address: str, note: str):
        pass

    @eventlog(indexed=1)
    def InhouseGames(self, address: Address, note: str):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)

        # Variables related to completion of distribution
        self._divs_dist_complete = VarDB(self._DIVS_DIST_COMPLETE, db, value_type=bool)

        # Variables related to batch of tap distribution
        self._tap_dist_index = VarDB(self._TAP_DIST_INDEX, db, value_type=int)
        self._batch_size = VarDB(self._BATCH_SIZE, db, value_type=int)

        # Tap holders and their balances of TAP tokens
        self._tap_holders = ArrayDB(self._TAP_HOLDERS, db, value_type=str)
        self._tap_balances = DictDB(self._TAP_BALANCES, db, value_type=int)
        self._total_eligible_tap_tokens = VarDB(self._TOTAL_ELIGIBLE_TAP_TOKENS, db, value_type=int)

        # Games which have made excess and their excess amount
        self._games_list = ArrayDB(self._GAMES_LIST, db, value_type=Address)
        self._games_excess = DictDB(self._GAMES_EXCESS, db, value_type=int)
        self._revshare_wallet_address = DictDB(self._REVSHARE_WALLET_ADDRESS, db, value_type=Address)

        # Founders/platform holders addresses
        self._blacklist_address = ArrayDB(self._BLACKLIST_ADDRESS, db, value_type=str)

        # Dividends of each category
        self._total_divs = VarDB(self._TOTAL_DIVS, db, value_type=int)
        self._remaining_tap_divs = VarDB(self._REMAINING_TAP_DIVS, db, value_type=int)
        self._remaining_gamedev_divs = VarDB(self._REMAINING_GAMEDEV_DIVS, db, value_type=int)
        self._platform_divs = VarDB(self._PLATFORM_DIVS, db, value_type=int)
        self._promo_divs = VarDB(self._PROMO_DIVS, db, value_type=int)

        # Games marked as inhouse games
        self._inhouse_games = ArrayDB(self._INHOUSE_GAMES, db, value_type=Address)

        # Dividend percentage for each of the category
        self._dividend_percentage = ArrayDB(self._DIVIDEND_PERCENTAGE, db, value_type=int)

        # Addresses of external scores with which the dividends score communicates
        self._token_score = VarDB(self._TOKEN_SCORE, db, value_type=Address)
        self._game_score = VarDB(self._GAME_SCORE, db, value_type=Address)
        self._promo_score = VarDB(self._PROMO_SCORE, db, value_type=Address)
        self._game_auth_score = VarDB(self._GAME_AUTH_SCORE, db, value_type=Address)

        self._dividends_received = VarDB(self._DIVIDENDS_RECEIVED, db, value_type=int)

        self._stake_holders = ArrayDB(self._STAKE_HOLDERS, db, value_type=str)
        self._stake_balances = DictDB(self._STAKE_BALANCES, db, value_type=int)
        self._total_eligible_staked_tap_tokens = VarDB(self._TOTAL_ELIGIBLE_STAKED_TAP_TOKENS, db, value_type=int)
        self._stake_dist_index = VarDB(self._STAKE_DIST_INDEX, db, value_type=int)

        self._switch_dividends_to_staked_tap = VarDB(self._SWITCH_DIVIDENDS_TO_STAKED_TAP, db, value_type=bool)

        self._exception_address = ArrayDB(self._EXCEPTION_ADDRESS, db, value_type=str)

    def on_install(self) -> None:
        super().on_install()
        self._total_divs.set(0)

    def on_update(self) -> None:
        super().on_update()

    @external
    def set_dividend_percentage(self, _tap: int, _gamedev: int, _promo: int, _platform: int) -> None:
        """
        Sets the percentage for distribution to tap holders, game developers, promotion and platform. The sum of the
        percentage must be 100.
        Can only be called by owner of the score
        :param _tap: Percentage for distribution to tap holders
        :type _tap: int
        :param _gamedev: Percentage for distribution to game developers
        :type _gamedev: int
        :param _promo: Percentage for distribution to promotion
        :type _promo: int
        :param _platform: Percentage for distribution to platform/founders
        :type _platform: int
        """
        if self.msg.sender != self.owner:
            revert("Only the owner of the score can call the method")
        if not (
            0 <= _tap <= 100
            and 0 <= _gamedev <= 100
            and 0 <= _promo <= 100
            and 0 <= _platform <= 100
        ):
            revert("The parameters must be between 0 to 100")
        if _tap + _gamedev + _platform + _promo != 100:
            revert("Sum of all percentage is not equal to 100")
        for _ in range(len(self._dividend_percentage)):
            self._dividend_percentage.pop()
        self._dividend_percentage.put(_tap)
        self._dividend_percentage.put(_gamedev)
        self._dividend_percentage.put(_promo)
        self._dividend_percentage.put(_platform)

    @external(readonly=True)
    def get_dividend_percentage(self) -> dict:
        """
        Returns all the categories of dividend and their percentage.
        :return: Category of dividends and their percentage
        :rtype: str
        """
        response = {}
        for index, category in enumerate(DIVIDEND_CATEGORIES):
            response[category] = self._dividend_percentage.get(index)
        return response

    @external
    def set_token_score(self, _score: Address) -> None:
        """
        Sets the token score address. The function can only be invoked by score owner.
        :param _score: Score address of the token
        :type _score: :class:`iconservice.base.address.Address`
        """
        if self.msg.sender == self.owner:
            self._token_score.set(_score)

    @external(readonly=True)
    def get_switch_dividends_to_staked_tap(self) -> bool:
        """
        Returns the status of the switch to enable the dividends to staked tap holders
        :return: True if the switch for dividends to staked tap is enabled
        """
        return self._switch_dividends_to_staked_tap.get()

    @external
    def toggle_switch_dividends_to_staked_tap_enabled(self) -> None:
        if self.msg.sender != self.owner:
            revert("Only owner can enable or disable switch dividends to staked tap holders.")
        self._switch_dividends_to_staked_tap.set(not self._switch_dividends_to_staked_tap.get())

    @external
    def set_game_score(self, _score: Address) -> None:
        """
        Sets the roulette score address. The function can only be invoked by score owner.
        :param _score: Score address of the roulette
        :type _score: :class:`iconservice.base.address.Address`
        """
        if self.msg.sender == self.owner:
            self._game_score.set(_score)

    @external
    def set_promo_score(self, _score: Address) -> None:
        """
        Sets the promo score address. The function can only be invoked by score owner.
        :param _score: Score address of the promo
        :type _score: :class:`iconservice.base.address.Address`
        """
        if not _score.is_contract:
            revert(f"{_score} is not a valid contract address")
        if self.msg.sender == self.owner:
            self._promo_score.set(_score)

    @external
    def set_game_auth_score(self, _score: Address) -> None:
        """
        Sets the game authorization score address. The method can only be invoked by score owner
        :param _score: Score address of the game authorization score
        :type _score: :class:`iconservice.base.address.Address`
        :return:
        """
        if not _score.is_contract:
            revert(f"{_score} is not a valid contract address")
        if self.msg.sender == self.owner:
            self._game_auth_score.set(_score)

    @external(readonly=True)
    def get_token_score(self) -> Address:
        """
        Returns the token score address.
        :return: Address of the token score
        :rtype: :class:`iconservice.base.address.Address`
        """
        return self._token_score.get()

    @external(readonly=True)
    def get_game_score(self) -> Address:
        """
        Returns the roulette score address.
        :return: Address of the roulette score
        :rtype: :class:`iconservice.base.address.Address`
        """
        return self._game_score.get()

    @external(readonly=True)
    def get_promo_score(self) -> Address:
        """
        Returns the promotion score address.
        :return: Address of the promotion score
        :rtype: :class:`iconservice.base.address.Address`
        """
        return self._promo_score.get()

    @external(readonly=True)
    def get_game_auth_score(self) -> Address:
        """
        Returns the game authorization score address
        :return: Address of the game authorization score address
        :rtype: :class:`iconservice.base.address.Address`
        """
        return self._game_auth_score.get()

    @external(readonly=True)
    def dividends_dist_complete(self) -> bool:
        """
        Checks the status of dividends distribution
        :return: True if distribution is completed
        :rtype: bool
        """
        return self._divs_dist_complete.get()

    @external(readonly=True)
    def get_total_divs(self) -> int:
        """
        Returns total dividends of previous day. It is distributed on the current day.
        :return: Total dividends for distribution of previous day
        :rtype: int
        """
        return self._total_divs.get()

    @external
    def untether(self) -> None:
        """
        A function to redefine the value of self.owner once it is possible.
        To be included through an update if it is added to IconService.

        Sets the value of self.owner to the score holding the game treasury.
        """
        if self.tx.origin != self.owner:
            revert(f"Only the owner can call the untether method.")
        pass

    @external
    def distribute(self) -> bool:
        """
        Main distribute function invoked by rewards distribution contract. This function can also be called when the
        treasury needs to be dissolved. For dissolving the treasury, there must be a majority of votes from TAP holders.
        :return: True if distribution is completed
        :rtype: bool
        """
        token_score = self.create_interface_score(self._token_score.get(), TokenInterface)

        if self._dividends_received.get() == 1:
            self._divs_dist_complete.set(False)
            self._dividends_received.set(2)
            if not self._switch_dividends_to_staked_tap.get():
                token_score.switch_address_update_db()
                # calculate total eligible tap
                self._set_total_tap()

        elif self._dividends_received.get() == 2:
            if self._switch_dividends_to_staked_tap.get():
                if self._update_stake_balances():
                    token_score.switch_stake_update_db()
                    # calculate total eligible staked tap tokens
                    self._set_total_staked_tap()
                    self._set_tap_of_exception_address()
                    self._dividends_received.set(3)
            else:
                if self._update_balances():
                    self._dividends_received.set(3)

        elif self._dividends_received.get() == 3:
            game_score = self.create_interface_score(self._game_score.get(), GameInterface)

            # Set the dividends for each category
            balance = self.icx.get_balance(self.address)
            self._total_divs.set(balance)
            if game_score.get_treasury_status():
                self._remaining_tap_divs.set(balance)
                self._remaining_gamedev_divs.set(0)
                self._promo_divs.set(0)
                self._platform_divs.set(0)
            elif self._switch_dividends_to_staked_tap.get():
                self._set_games_ip()
            else:
                # Set the games making excess and their excess balance and the dividends of categories
                self._set_games()

            if self._switch_dividends_to_staked_tap.get():
                self._batch_size.set(game_score.get_batch_size(len(self._stake_holders)))
            else:
                self._batch_size.set(game_score.get_batch_size(len(self._tap_holders)))

            self._dividends_received.set(0)

        elif self._divs_dist_complete.get():
            if self._switch_dividends_to_staked_tap.get():
                self._update_stake_balances()
                token_score.clear_yesterdays_stake_changes()
            else:
                self._update_balances()
                token_score.clear_yesterdays_changes()
            return True
        elif self._remaining_tap_divs.get() > 0:
            if self._switch_dividends_to_staked_tap.get():
                self._distribute_to_stake_holders()
            else:
                self._distribute_to_tap_holders()
        elif self._promo_divs.get() > 0:
            self._distribute_to_promo_address()
        elif self._remaining_gamedev_divs.get() > 0:
            self._distribute_to_game_developers()
        elif self._platform_divs.get() > 0:
            self._distribute_to_platform()
        else:
            self._divs_dist_complete.set(True)
            return True
        return False

    def _distribute_to_tap_holders(self) -> None:
        """
        This function distributes the dividends to tap token holders except the blacklist addresses.
        """
        count = self._batch_size.get()
        length = len(self._tap_holders)
        start = self._tap_dist_index.get()
        remaining_addresses = length - start
        if count > remaining_addresses:
            count = remaining_addresses
        end = start + count
        dividend = self._remaining_tap_divs.get()
        tokens_total = self._total_eligible_tap_tokens.get()
        for i in range(start, end):
            address = self._tap_holders[i]
            holder_balance = self._tap_balances[address]
            if holder_balance > 0 and tokens_total > 0:
                amount = dividend * holder_balance // tokens_total
                dividend -= amount
                tokens_total -= holder_balance
                try:
                    self.icx.transfer(Address.from_string(address), amount)
                    self.FundTransfer(address, amount, "Dividends distribution to tap holder")
                except BaseException as e:
                    if Address.from_string(address).is_contract:
                        self.set_blacklist_address(address)
                    else:
                        revert(
                            f"Network problem while sending dividends to tap holders."
                            f"Distribution of {amount} not sent to {address}. "
                            f"Will try again later. "
                            f"Exception: {e}"
                        )
        self._remaining_tap_divs.set(dividend)
        self._total_eligible_tap_tokens.set(tokens_total)
        if end == length or dividend <= 0:
            self._tap_dist_index.set(0)
            self._remaining_tap_divs.set(0)
        else:
            self._tap_dist_index.set(start + count)

    def _distribute_to_promo_address(self) -> None:
        """
        Distributes the dividend according to set percentage for promotion
        """
        amount = self._promo_divs.get()
        address = self._promo_score.get()
        if amount > 0:
            try:
                self.icx.transfer(address, amount)
                self.FundTransfer(
                    str(address), amount, "Dividends distribution to Promotion contract"
                )
                self._promo_divs.set(0)
            except BaseException as e:
                revert(
                    f"Network problem while sending to game SCORE. "
                    f"Distribution of {amount} not sent to {address}. "
                    f"Will try again later. "
                    f"Exception: {e}"
                )

    def _distribute_to_game_developers(self) -> None:
        """
        Distributes the dividends to game developers if only their game has made a positive excess i.e. total wager
        is greater than their total payout
        """
        for game in self._games_list:
            if game in self._inhouse_games:
                amount = (self._dividend_percentage[1] * self._games_excess[str(game)]) // 100
                self._remaining_gamedev_divs.set(self._remaining_gamedev_divs.get() - amount)
                self._platform_divs.set(self._platform_divs.get() + amount)
            else:
                amount = (self._games_excess[str(game)] * self._dividend_percentage[1]) // 100
                address = self._revshare_wallet_address[str(game)]
                if amount > 0:
                    try:
                        self.icx.transfer(address, amount)
                        self.FundTransfer(
                            str(address),
                            amount,
                            "Dividends distribution to Game developer's wallet "
                            "address",
                        )
                        self._remaining_gamedev_divs.set(self._remaining_gamedev_divs.get() - amount)
                    except BaseException as e:
                        revert(
                            f"Network problem while sending to revshare wallet address "
                            f"Distribution of {amount} not sent to {address}. "
                            f"Will try again later. "
                            f"Exception: {e}"
                        )
        for _ in range(len(self._games_list)):
            game = self._games_list.pop()
            self._games_excess.remove(str(game))
        self._remaining_gamedev_divs.set(0)

    def _distribute_to_platform(self) -> None:
        """
        Distributes the dividends to platform/founder members.
        """
        token_score = self.create_interface_score(self._token_score.get(), TokenInterface)
        total_platform_tap: int = 0
        for address in self._blacklist_address:
            address_from_str = Address.from_string(address)
            if not address_from_str.is_contract:
                total_platform_tap += token_score.balanceOf(address_from_str)
        if total_platform_tap == 0:
            revert("No tap found in founder's addresses")
        dividends = self._platform_divs.get()
        for address in self._blacklist_address:
            address_from_str = Address.from_string(address)
            balance = token_score.balanceOf(address_from_str)
            if not address_from_str.is_contract and total_platform_tap > 0 and balance > 0 and dividends > 0:
                amount = (balance * dividends // total_platform_tap)
                dividends -= amount
                total_platform_tap -= balance
                try:
                    self.icx.transfer(address_from_str, amount)
                    self.FundTransfer(address, amount, "Dividends distribution to Platform/Founders address")

                except BaseException as e:
                    revert(
                        f"Network problem while sending to founder members address "
                        f"Distribution of {amount} not sent to {address}. "
                        f"Will try again later. "
                        f"Exception: {e}"
                    )
        self._platform_divs.set(0)

    def _distribute_to_stake_holders(self) -> None:
        """
        This function distributes the dividends to staked tap token holders.
        """
        count = self._batch_size.get()
        length = len(self._stake_holders)
        start = self._stake_dist_index.get()
        remaining_addresses = length - start
        if count > remaining_addresses:
            count = remaining_addresses
        end = start + count
        dividend = self._remaining_tap_divs.get()
        tokens_total = self._total_eligible_staked_tap_tokens.get()
        for i in range(start, end):
            address = self._stake_holders[i]
            holder_balance = self._stake_balances[address]
            if holder_balance > 0 and tokens_total > 0:
                amount = dividend * holder_balance // tokens_total
                dividend -= amount
                tokens_total -= holder_balance
                try:
                    self.icx.transfer(Address.from_string(address), amount)
                    self.FundTransfer(
                        address, amount, "Dividends distribution to tap holder"
                    )
                except BaseException as e:
                    if Address.from_string(address).is_contract:
                        self.set_blacklist_address(address)
                    else:
                        revert(
                            f"Network problem while sending dividends to stake holders."
                            f"Distribution of {amount} not sent to {address}. "
                            f"Will try again later. "
                            f"Exception: {e}"
                        )
        self._remaining_tap_divs.set(dividend)
        self._total_eligible_staked_tap_tokens.set(tokens_total)
        if end == length or dividend <= 0:
            self._stake_dist_index.set(0)
            self._remaining_tap_divs.set(0)
        else:
            self._stake_dist_index.set(start + count)

    @external(readonly=True)
    def get_blacklist_addresses(self) -> list:
        """
        Returns all the blacklisted addresses(rewards score address and devs team address)
        :return: List of blacklisted address
        :rtype: list
        """
        address_list = []
        for address in self._blacklist_address:
            address_list.append(address)
        return address_list

    @external
    def remove_from_blacklist(self, _address: str) -> None:
        """
        Removes the address from blacklist.
        Only owner can remove the blacklist address
        :param _address: Address to be removed from blacklist
        :type _address: :class:`iconservice.base.address.Address`
        :return:
        """
        if self.msg.sender == self.owner:
            if _address not in self._blacklist_address:
                revert(f"{_address} not in blacklist address")
            self.BlacklistAddress(_address, "Removed from blacklist")
            top = self._blacklist_address.pop()
            if top != _address:
                for i in range(len(self._blacklist_address)):
                    if self._blacklist_address[i] == _address:
                        self._blacklist_address[i] = top

    @external
    def set_blacklist_address(self, _address: str) -> None:
        """
        The provided address is set as blacklist address and will be excluded from TAP dividends.
        Only the owner can set the blacklist address
        :param _address: Address to be included in the blacklist
        :type _address: :class:`iconservice.base.address.Address`
        :return:
        """
        if self.msg.sender == self.owner:
            self.BlacklistAddress(_address, "Added to Blacklist")
            if _address in self._tap_holders:
                self._remove_from_holders_list(_address)
            if _address not in self._blacklist_address:
                self._blacklist_address.put(_address)

    def _remove_from_holders_list(self, _address: str) -> None:
        """
        Removes the address from tap token holders list
        :param _address: Address to be removed from tap token holders list
        :type _address: :class:`iconservice.base.address.Address`
        :return:
        """
        if _address not in self._tap_holders:
            return
        # get the topmost value
        top = self._tap_holders.pop()
        if top != _address:
            for i in range(len(self._tap_holders)):
                if self._tap_holders[i] == _address:
                    self._tap_holders[i] = top
        self._tap_balances.remove(_address)

    @external
    def set_inhouse_games(self, _score: Address) -> None:
        """
        Sets the inhouse games list. The dividend for game developers for these games will be sent to the
        platform/founders. Only owner can set the games as inhouse games.
        :param _score: Game address to be defined as in-house game.
        :type _score: :class:`iconservice.base.address.Address`
        :return:
        """
        if not _score.is_contract:
            revert(f"{_score} should be a contract address")
        if self.msg.sender == self.owner:
            self.InhouseGames(_score, "Added as inhouse games")
            if _score not in self._inhouse_games:
                self._inhouse_games.put(_score)

    @external(readonly=True)
    def get_inhouse_games(self) -> list:
        """
        Returns all the inhouse games developed by ICONBet team
        :return: Returns the list of inhouse games
        :rtype: list
        """
        games_list = []
        for address in self._inhouse_games:
            games_list.append(address)
        return games_list

    @external
    def remove_from_inhouse_games(self, _score: Address) -> None:
        """
        Remove the game address from inhouse game developers list. Only the owner can remove the game from inhouse
        games list.
        :param _score: Game address to be removed from inhouse games
        :type _score: :class:`iconservice.base.address.Address`
        :return:
        """
        if not _score.is_contract:
            revert(f"{_score} is not a valid contract address")
        if self.msg.sender == self.owner:
            if _score not in self._inhouse_games:
                revert(f"{_score} is not in inhouse games list")
            self.InhouseGames(_score, "Removed from inhouse games list")
            top = self._inhouse_games.pop()
            if top != _score:
                for i in range(len(self._inhouse_games)):
                    if self._inhouse_games[i] == _score:
                        self._inhouse_games[i] = top

    def _update_stake_balances(self) -> bool:
        """
        Updates the balances of tap holders in dividends distribution contract
        :return:
        """
        token_score = self.create_interface_score(self._token_score.get(), TokenInterface)
        stake_balances = token_score.get_stake_updates()
        if len(stake_balances) == 0:
            return True
        for address in stake_balances.keys():
            if address not in self._stake_holders:
                self._stake_holders.put(address)
            self._stake_balances[address] = stake_balances[address]
        return False

    def _update_balances(self) -> bool:
        """
        Updates the balances of tap holders in dividends distribution contract
        :return:
        """
        token_score = self.create_interface_score(self._token_score.get(), TokenInterface)
        tap_balances = token_score.get_balance_updates()
        if len(tap_balances) == 0:
            return True
        for address in tap_balances.keys():
            if address not in self._blacklist_address:
                if address not in self._tap_holders:
                    self._tap_holders.put(address)
                self._tap_balances[address] = tap_balances[address]
        return False

    def _set_total_tap(self) -> None:
        """
        Sets the eligible tap holders i.e. except the blacklist addresses, updates the balances of tap holders and
        sets the total eligible tap tokens
        :return:
        """
        total: int = 0
        token_score = self.create_interface_score(self._token_score.get(), TokenInterface)
        for address in self._blacklist_address:
            address_from_str = Address.from_string(address)
            total += token_score.balanceOf(address_from_str)
        self._total_eligible_tap_tokens.set(token_score.totalSupply() - total)

    def _set_total_staked_tap(self) -> None:
        """
        Sets the total staked tap tokens.
        :return:
        """
        token_score = self.create_interface_score(self._token_score.get(), TokenInterface)
        self._total_eligible_staked_tap_tokens.set(token_score.total_staked_balance())

    def _set_games(self) -> None:
        """
        Takes list of games to receive excess from game authorization score and sets the games list.
        Sets the excess of those games.
        :return:
        """
        game_auth_score = self.create_interface_score(self._game_auth_score.get(), GameAuthorizationInterface)
        games_excess = game_auth_score.get_yesterdays_games_excess()
        positive_excess: int = 0

        for game in games_excess.keys():
            game_address = Address.from_string(game)

            if int(games_excess[game]) > 0:
                if game_address not in self._games_list:
                    self._games_list.put(game_address)
                self._games_excess[game] = int(games_excess[game])
                revshare = game_auth_score.get_revshare_wallet_address(game_address)
                if self._revshare_wallet_address[game] != revshare:
                    self._revshare_wallet_address[game] = revshare
                positive_excess += int(games_excess[game])

        game_developers_share = (self._dividend_percentage[1] + self._dividend_percentage[3])
        game_developers_amount = (game_developers_share * positive_excess) // 100
        tap_holders_amount = self.icx.get_balance(self.address) - game_developers_amount

        self._remaining_gamedev_divs.set((self._dividend_percentage[1] * game_developers_amount)//game_developers_share)
        self._platform_divs.set((self._dividend_percentage[3] * game_developers_amount)//game_developers_share)
        if tap_holders_amount > 0:
            tap_holders_share = (self._dividend_percentage[0] + self._dividend_percentage[2])
            self._remaining_tap_divs.set((self._dividend_percentage[0] * tap_holders_amount) // tap_holders_share)
            self._promo_divs.set((self._dividend_percentage[2] * tap_holders_amount) // tap_holders_share)
        else:
            self._remaining_tap_divs.set(0)
            self._promo_divs.set(0)

    def _set_games_ip(self) -> None:
        """
        Set the dividends for different categories according to the improvement proposal
        """
        game_auth_score = self.create_interface_score(self._game_auth_score.get(), GameAuthorizationInterface)
        games_excess = game_auth_score.get_yesterdays_games_excess()
        third_party_excess: int = 0

        for game in games_excess.keys():
            game_address = Address.from_string(game)
            if int(games_excess[game]) > 0 and game_address not in self._inhouse_games:
                if game_address not in self._games_list:
                    self._games_list.put(game_address)
                self._games_excess[game] = int(games_excess[game])
                revshare = game_auth_score.get_revshare_wallet_address(game_address)
                if self._revshare_wallet_address[game] != revshare:
                    self._revshare_wallet_address[game] = revshare
                third_party_excess += int(games_excess[game])

        game_developers_amount = (third_party_excess * 20) // 100
        tap_holders_amount = self.icx.get_balance(self.address) - game_developers_amount

        self._remaining_gamedev_divs.set(game_developers_amount)
        self._platform_divs.set(0)
        if tap_holders_amount > 0:
            tap_divs = tap_holders_amount * 80 // 90
            self._remaining_tap_divs.set(tap_divs)
            self._promo_divs.set(tap_holders_amount - tap_divs)
        else:
            self._remaining_tap_divs.set(0)
            self._promo_divs.set(0)

    @external(readonly=True)
    def get_tap_hold_length(self) -> int:
        return len(self._tap_holders)

    @external(readonly=True)
    def get_staked_tap_hold_length(self) -> int:
        return len(self._stake_holders)

    @external(readonly=True)
    def divs_share(self) -> dict:
        divs = {
            "tap": f"{self._remaining_tap_divs.get()}",
            "wager": f"{self._promo_divs.get()}",
            "gamedev": f"{self._remaining_gamedev_divs.get()}",
            "platform": f"{self._platform_divs.get()}",
        }
        return divs

    @external
    def set_divs_share(self, _tap: int, _promo: int, _platform: int, _gamedev: int) -> None:
        if self.msg.sender != self.owner:
            revert("This method is only available for the owner")
        self._remaining_tap_divs.set(_tap)
        self._promo_divs.set(_promo)
        self._platform_divs.set(_platform)
        self._remaining_gamedev_divs.set(_gamedev)

    @external
    def toggle_divs_dist(self) -> None:
        if self.msg.sender != self.owner:
            revert("Only the owner can call this method")
        if self._divs_dist_complete.get():
            self._divs_dist_complete.set(False)
        else:
            self._divs_dist_complete.set(True)

    @external(readonly=True)
    def get_exception_address(self) -> list:
        return [address for address in self._exception_address]

    @external
    def add_exception_address(self, _address: Address) -> None:
        if self.msg.sender != self.owner:
            revert(f"ICONbet Dividends SCORE: Only owner can add an exception address")
        str_address = str(_address)
        if str_address not in self._exception_address:
            self._exception_address.put(str_address)

    @external
    def remove_exception_address(self, _address: Address) -> None:
        if self.msg.sender != self.owner:
            revert(f"ICONbet Dividends SCORE: Only owner can remove an exception address")

        str_address = str(_address)

        if str_address not in self._exception_address:
            revert(f"ICONbet Dividends SCORE: Address to remove not found in exception address list.")

        self._stake_balances[str_address] = 0
        _out = self._exception_address[-1]
        if _out == str_address:
            self._exception_address.pop()
        for index in range(len(self._exception_address) - 1):
            if self._exception_address[index] == str_address:
                self._exception_address[index] = _out
                self._exception_address.pop()

    def _set_tap_of_exception_address(self):
        tap_token_score = self.create_interface_score(self._token_score.get(), TokenInterface)
        for idx, address in enumerate(self._exception_address):
            if address not in self._stake_holders:
                self._stake_holders.put(address)
            tap_balance = tap_token_score.balanceOf(Address.from_string(address))
            self._stake_balances[address] = tap_balance
            self._total_eligible_staked_tap_tokens.set(self._total_eligible_staked_tap_tokens.get()+tap_balance)

    @payable
    def fallback(self):
        if self.msg.sender == self._game_score.get():
            # Set the status of all divisions as False
            self._dividends_received.set(1)
            self.DivsReceived(self._total_divs.get(), self._batch_size.get())
        else:
            revert(f"Funds can only be accepted from the game contract.")
