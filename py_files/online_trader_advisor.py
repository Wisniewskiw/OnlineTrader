import abc
from abc import ABCMeta
import py_files.email_sender as es
import pandas as pd
import numpy as np
import json

class OnlineStrategiesCrypto(object):
    """
    Abstract class strategies
    """
    __metaclass__ = ABCMeta

    def __init__(self, parameters_dict):
        """
        Initialize algo with a dictionary.
        """
        self.capital = parameters_dict['capital']  # initial capital value
        self.crypto_initial = parameters_dict['crypto_initial']  # the initial amount of crypto
        self.fees = parameters_dict['fees']
        self.crypto_symbol = parameters_dict['crypto_symbol']
        self.time_resolution_delta = parameters_dict['delta']  # in minutes
        self.send_mail = parameters_dict['send_mail']
        self.positions = []
        self.capital_before_lastbuy = self.capital
        self.capital_floating = self.capital
        if self.send_mail:
            with open('json_files//data.json', 'r') as fp:
                data = json.load(fp)
            self.sender_mail = data['Live_office365_email_sender']
            self.receiver = parameters_dict['receiver_mail_address']
            self.password = data['Live_office365_email_key']
            self.email_sender = es.EmailSender(self.sender_mail, self.password)

    def send_email_order(self, order, capital=''):
        """Check if all papameters in list are set
        """
        if self.send_mail:
            mail_title = 'Algo ' + __class__.__name__ + ' suggests to ' + order['order'] + ' ' + order['symbol']
            mail_content = str(order) + capital
            self.email_sender.send_email(self.receiver, mail_title, mail_content)

    @abc.abstractmethod
    def sell(self, feed):
        """
        Abstract method : sell metaorder
       """

    @abc.abstractmethod
    def buy(self, feed):
        """
        Abstract method : buy metaorder
       """