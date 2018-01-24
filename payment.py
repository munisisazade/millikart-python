"""
    Author Munis Isazade Django payments
    E-Commerce gateway for merchants
    Transaction registration
    Request
    Test system
    Production system
    Parameters
    Name Description
    Mid = Merchant ID
    Amount = Transaction amount (Integer: $50.25 = 5025)
    Currency =  Transaction currency code (ISO 4217)
    Description = Transaction description (Can be used for item assigenment)
    Reference = Transaction reference (unique transaction value set by merchant)
    Language = Language (az/en/ru)
    Signature = MD5 hash of concatenated parameter length + value with secret key
"""
from django.conf import settings
import requests, hashlib, random, string
import xml.etree.ElementTree as ET


class Payment(object):
    def __init__(self, amount,description):
        self.mid = settings.MID
        self.amount = amount
        self.currency = '944'
        self.description = description
        self.reference = self.generate_code()
        self.language = 'az'
        self.signature = ''

    def run(self):
        # create signature
        self.create_signature()
        payment_url = self.get_base_payment_url()
        return payment_url

    def generate_code(self, size=20, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def check_status(self, refer):
        """
            In this XML response <RC>response code </RC>
            is transaction response code
            :return: <RC>response code </RC>
        """
        status_check_url = settings.MILLI_KART_PAYMENT_STATUS
        base_params = '?mid=%s&reference=%s' % (settings.MID, refer)
        send_status = requests.get(status_check_url + base_params)
        result = {}
        if send_status.status_code == 200:
            result['status_code'] = send_status.text
        result['data'] = send_status.text
        check_payment = self.xml_parser_data(send_status.text)
        result['status'] = check_payment['payment_status']
        return result

    def xml_parser_data(self, data_xml):
        """
            Base xml parser response data
            :param data_xml:
            :return:
        """
        try:
            pars_data = ET.fromstring(data_xml)
            statistic = {}
            if pars_data.find('RC').text == '000':
                statistic['payment_status'] = True
                statistic['payment_description'] = 'OK'
            else:
                statistic['payment_status'] = False
                statistic['payment_description'] = 'Failed'
            return statistic
        except:
            statistic = {}
            statistic['payment_status'] = False
            statistic['payment_description'] = 'Failed'
            return statistic

    def create_signature(self):
        """
            Signature must be Uppercase and
            MD5 hash of concatenated parameter
            length + value with secret key
            :return: signature
        """
        non_hash = str(len(self.mid)) + str(self.mid) + \
                   str(len(str(self.amount))) + str(self.amount) + \
                   str(len(str(self.currency))) + str(self.currency) + \
                   str(len(self.description)) + str(self.description) + \
                   str(len(self.reference)) + str(self.reference) + \
                   str(len(self.language)) + str(self.language) + \
                   str(settings.PAYMENT_SECRET_KEY)

        self.signature = hashlib.md5(non_hash.encode()).hexdigest().upper()

    def get_base_payment_url(self):
        params = dict(mid=self.mid, amount=self.amount,
                      currency=self.currency, description=self.description,
                      reference=self.reference, language=self.language,
                      signature=self.signature, redirect=1)

        last = self.params_url_encode(params)
        return settings.MILLI_KART_PAYMENT + last

    def params_url_encode(self, item):
        encode_url = ""
        for key, value in item.items():
            encode_url += str(key) + "=" + str(value) + "&"
        encode_url = "?%s" % encode_url[:-1]
        return encode_url
