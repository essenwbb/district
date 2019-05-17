from bs4 import BeautifulSoup
import re
import requests
import time


class DistrictData:
    base_url = 'http://www.mca.gov.cn'
    url = ''
    title = ''
    data = []

    def __newest_url(self):
        home_url = '{}/article/sj/xzqh/{}/'.format(self.base_url, time.localtime().tm_year)
        res = requests.get(url=home_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.select("#list_content > div.list_right > div > ul > table > tr > td > a")

        for link in links:
            if "中华人民共和国县以上行政区划代码" in link["title"]:
                self.title = link["title"]
                self.url = '{}{}'.format(self.base_url, link["href"])
                return

    def __redirected_url(self):
        if not self.url:
            self.url = None
            return
        re_link = r"http://www.mca.gov.cn/article/sj/xzqh/.*?\.html"
        res = requests.get(url=self.url)
        res.encoding = 'utf-8'
        links = re.findall(re_link, res.text)
        self.url = links[0] if links else ''

    def __newest_data(self):
        if not self.url:
            self.data = []
            return
        res = requests.get(url=self.url)
        soup = BeautifulSoup(res.text, 'html.parser')
        self.data = [{"id": i.contents[3].text, "name": i.contents[5].text} for i in soup.select('tr[height="19"]')]

    def __fix_data(self):
        for name, id_area in (("北京城区", 110100), ("天津城区", 120100), ("上海城区", 310100), ("重庆城区", 500100)):
            self.data.append({
                "id": id_area,
                "name": name
            })
        self.data.sort(key=lambda k: int(k["id"]))

    def get_url(self):
        self.__newest_url()
        return self.url

    def __call__(self, *args, **kwargs):
        self.__newest_url()
        self.__redirected_url()
        self.__newest_data()
        self.__fix_data()
        return self.data
