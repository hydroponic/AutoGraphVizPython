import re
import os
import sys
import pkginfo
import requests
import graphviz
import shutil
from bs4 import BeautifulSoup as bs
dot = graphviz.Digraph()
base_url = "https://pypi.org/simple/"
path = "packages_temp_test"
downloaded = []
max_depth = 2
def parse_packet(pkg_name, depth=0):
    if depth >= max_depth:
        return
    request = requests.get(f'{base_url + pkg_name}')
    if request.status_code == 200:
        soup = bs(request.text, "html.parser")
        tag_list = soup.find_all('a')[::-1]
        downloaded.append(pkg_name)
        for item in tag_list:
            if item.text[-4:] == '.whl':
                file_name = path + "/" + item.text
                with open(file_name, 'wb') as f:
                    f.write(requests.get(item["href"], stream=True).raw.read())
                depends = pkginfo.get_metadata(path + '/' + item.text).requires_dist
                for dep in depends:
                    dep_name = re.match("^([0-9A-Za-z-_])+", dep)[0]
                    if dep_name not in downloaded:
                        downloaded.append(dep_name)
                        dot.edge(pkg_name, dep_name)
                        parse_packet(dep_name, depth + 1)
                break
    elif request.status_code == 404:
        print(f'Не удалось найти папку {pkg_name}')
if len(sys.argv) != 2:
    print(f'Использование: {sys.argv[0]} **название папки**')
else:
    try:
        os.mkdir(path)
    except OSError as error:
        pass
    parse_packet(sys.argv[1])
    shutil.rmtree(path)
    print(dot.source)