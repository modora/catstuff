def title(name, symbol='-', border_length=100):
    border(symbol=symbol, border_length=border_length)
    print(name)
    border(symbol=symbol, border_length=border_length)


def border(symbol='-', border_length=100):
    single_instance = symbol * border_length
    print(single_instance[:border_length])  # print up to the specified length
