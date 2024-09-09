from bs4 import BeautifulSoup
import requests


def get_status_code(url):
    status_code = requests.get(url).status_code
    return status_code


def get_values(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    h1 = soup.find('h1').text if soup.find('h1') else ''
    title = soup.find('title').text if soup.find('title') else ''
    description = ''
    metas = soup.find_all('meta')
    for i in metas:
        if i.get('name', '') == 'description':
            description = i['content']
            break
    return (h1, title, description)
