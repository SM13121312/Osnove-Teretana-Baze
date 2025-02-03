from datetime import date, timedelta


datum = date.today()
pre_mesec = datum - timedelta(days=365)
print(datum, pre_mesec)

