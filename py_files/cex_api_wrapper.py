import hmac
import hashlib
import time
import requests

BASE_URL = 'https://cex.io/api/%s/'

PUBLIC_COMMANDS = {
    'currency_limits',
    'ticker',
    'last_price',
    'last_prices',
    'convert',
    'price_stats',
    'order_book',
    'trade_history'
}


class Api:
    """
    Python wrapper for CEX.IO
    """

    def __init__(self, username, api_key, api_secret):
        self.username = username
        self.api_key = api_key
        self.api_secret = api_secret

    @property
    def __nonce(self):
        return str(int(time.time() * 1000))

    def __signature(self, nonce):
        message = nonce + self.username + self.api_key
        signature = hmac.new(bytearray(self.api_secret.encode('utf-8')), message.encode('utf-8'),
                             digestmod=hashlib.sha256).hexdigest().upper()
        return signature

    def api_call(self, command, param=None, action=''):
        """
        :param command: Query command for getting info
        :type commmand: str
        :param param: Extra options for query
        :type options: dict
        :return: JSON response from CEX.IO
        :rtype : dict
        """
        if param is None:
            param = {}

        if command not in PUBLIC_COMMANDS:
            nonce = self.__nonce
            param.update({
                'key': self.api_key,
                'signature': self.__signature(nonce),
                'nonce': nonce
            })

        request_url = (BASE_URL % command) + action
        result = self.__post(request_url, param)

        return result

    def historical_OHLCV_chart(self, date, market='ETH/GBP'):

        return self.api_call('ohlcv/hd', None, date + '/' + market)

    def last_price(self, market='ETH/GBP'):
        return self.api_call('last_price', None, market)

    def ticker(self, market='ETH/GBP'):
        """
        :param market: String literal for the market (ex: BTC/ETH)
        :type market: str
        :return: Current values for given market in JSON
        :rtype : dict
        """
        return self.api_call('ticker', None, market)

    @property
    def balance(self):
        return self.api_call('balance')

    @property
    def get_myfee(self):
        return self.api_call('get_myfee')

    @property
    def currency_limits(self):
        return self.api_call('currency_limits')

    def convert(self, amount=1, market='ETH/GBP'):
        """
        Converts any amount of the currency to any other currency by multiplying the amount
        by the last price of the chosen pair according to the current exchange rate.
        :param amount: Convertible amount
        :type amount: float
        :return: Amount in the target currency
        :rtype: dict
        """
        return self.api_call('convert', {'amnt': amount}, market)


    def order_book(self, depth=1, market='ETH/GBP'):
        return self.api_call('order_book', None, market + '/?depth=' + str(depth))

    def trade_history(self, since=1, market='ETH/GBP'):
        return self.api_call('trade_history', None, market + '/?since=' + str(since))

    def __post(self, url, param):
        result = requests.post(url, data=param, headers={'User-agent': 'bot-cex.io-' + self.username}).json()
        return result


class cex_dataframe_online_saver:
    """
        Converter of  cex.io api ticker to dataframe
    """
    def __init__(self, name):
        self.name = name
        self.counter = 0

    def cex_transform_dict_to_df(self, dictionary):

        for x, y in dictionary.items():

            if x == 'timestamp':
                dictionary[x] = [pd.to_datetime((dictionary[x]), unit='s')]

            elif x != 'pair':
                dictionary[x] = [float(dictionary[x])]

            else:
                dictionary[x] = [dictionary[x]]

        return pd.DataFrame(dictionary)

    def cex_ticker_save(self, dictionary):
        df = self.cex_transform_dict_to_df(dictionary)

        if self.counter:
            df.to_csv(self.name + '.csv', mode='a', header=False)

        else:
            df.to_csv(self.name + '.csv', mode='a')
            self.counter = 1

