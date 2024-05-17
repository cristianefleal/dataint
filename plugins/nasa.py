import requests

class nasa:
    def __init__(self):
        pass

    def teste(self):

        texto = 'ola'
        print(texto)
        return texto
    
    def rover(self, api_key):

        url = f"https://api.nasa.gov/mars-photos/api/v1/rovers?api_key={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            print(data)
            return data
        else:
            print("Erro ao acessar a API")
            return "Erro"
