import csv


class ExchangeRate:
    
    def __init__(self):
        self._exchange_rates = []

        with open("app/exchange_rates.csv") as file:
            reader = csv.DictReader(file)
            for row in reader:
                exchange_rate = {}
                exchange_rate["source_currency"] = row["currency_from"]
                exchange_rate["target_currency"] = row["currency_to"]
                exchange_rate["exchange_rate"] = float(row["rate"])
                self._exchange_rates.append(exchange_rate)
                                                       
    @property
    def source_currencies(self):
        return list({exchange_rate["source_currency"] for exchange_rate in self._exchange_rates}) 

    @property
    def target_currencies(self):
        return list({exchange_rate["target_currency"] for exchange_rate in self._exchange_rates})  

    def filter_by(self, source_currency=None, target_currency=None):
        for exchange_rate in self._exchange_rates:
            if (exchange_rate["source_currency"], exchange_rate["target_currency"]) == (source_currency, target_currency):
                return exchange_rate["exchange_rate"]  


class ExchangeFee:
    
    def __init__(self):
        self._exchange_fees = []

        with open("app/exchange_fees.csv") as file:
            reader = csv.DictReader(file)
            for row in reader:  
                exchange_fee = {}
                exchange_fee["source_currency"] = row["currency_from"]
                exchange_fee["target_currency"] = row["currency_to"]
                exchange_fee["exchange_fee"] = float(row["fee"])
                self._exchange_fees.append(exchange_fee) 

    def filter_by(self, source_currency=None, target_currency=None):
        for exchange_fee in self._exchange_fees:
            if (exchange_fee["source_currency"], exchange_fee["target_currency"]) == (source_currency, target_currency):
                return exchange_fee["exchange_fee"]                                                                    
