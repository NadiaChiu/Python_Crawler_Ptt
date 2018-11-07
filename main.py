import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from bs4.element import Tag
from write2db import Write2Sqlite

PAGE_COUNT = 5
URL_PTT_BASE = 'https://www.ptt.cc'
URL_PTT_BOARD = URL_PTT_BASE + '/bbs/Gossiping/index.html'
COOKIES = {'over18': '1'}


def parser_post_info(url):
    code = url.split('/')[-1]
    board = url.split('/')[-2]
    dict_post = {'board': board, 'code': code}
    l_dict_push = []

    res = requests.get(url, cookies=COOKIES)
    if res.status_code != 200:
        print(res.status_code)
        print('Requests Get Failed 01')
    soup = BeautifulSoup(res.text.encode('utf-8'), "html.parser")
    main_content = soup.find(id='main-content')
    if main_content is None:
        print('')
    metalines = main_content.select('div.article-metaline')
    try:
        author = metalines[0].select('span.article-meta-value')[0].text
        title = metalines[1].select('span.article-meta-value')[0].text
        dt = metalines[2].select('span.article-meta-value')[0].text
        dict_post['author'] = author
        dict_post['title'] = title
        dict_post['dt'] = dt
    except IndexError:
        return dict_post, l_dict_push

    # remove nodes : meta
    for meta in metalines:
        meta.extract()
    for meta in main_content.select('div.article-metaline-right'):
        meta.extract()

    # remove node : f2
    spans = main_content.find_all('span', class_='f2')
    for span in spans:
        span.extract()

    # remove node : push
    pushes = main_content.find_all('div', class_='push')
    for push in pushes:
        pushinfo = {}
        try:
            pushinfo['user'] = push.select('span.f3.hl.push-userid')[0].text
            pushinfo['ipdt'] = push.select('span.push-ipdatetime')[0].text
            pushinfo['tag'] = push.select('span.hl.push-tag')[0].text
            pushinfo['content'] = push.select('span.f3.push-content')[0].text
            l_dict_push.append(pushinfo)
        except IndexError:
            pass
        push.extract()

    content = ''
    for item in main_content.contents:
        if type(item) == Tag:
            content += item.text
        else:
            content += str(item)
    dict_post['content'] = content

    return dict_post, l_dict_push


def get_post_url(soup):
    l_url = []
    for line in soup.select('div.r-ent div.title a'):
        try:
            l_url.append(URL_PTT_BASE + line.attrs['href'])
        except AttributeError:
            pass  # 本文已被刪除
    return l_url


def get_next_page(soup):
    try:
        if 'href' in soup.select('.action-bar a.btn.wide')[1].attrs:
            return URL_PTT_BASE + soup.select('.action-bar a.btn.wide')[1].attrs['href']
        else:
            return None
    except Exception as e:
        print(e)
        return None


if __name__ == '__main__':
    _post_url = URL_PTT_BOARD
    _l_post_url = []

    # 先將每頁的po文url解出來
    for _page in tqdm(range(PAGE_COUNT)):
        _res = requests.get(_post_url, cookies=COOKIES)
        if _res.status_code != 200:
            print(_res.status_code)
        _soup = BeautifulSoup(_res.text.encode('utf-8'), "html.parser")
        _l_post_url.extend(get_post_url(_soup))

        _post_url = get_next_page(_soup)

    # create db writer
    _db_writer = Write2Sqlite()

    # 解po文 - single
    for _url in tqdm(_l_post_url):
        _dict_post, _l_dict_push = parser_post_info(_url)
        # write to db
        _db_writer.execute_data(_dict_post, _l_dict_push)

    # close db
    _db_writer.close()
