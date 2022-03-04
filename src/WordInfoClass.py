
#coding: utf-8

from asyncio.windows_events import NULL
import requests
from bs4 import BeautifulSoup
import binascii
import hirakata as hk

#--------------------------------------------------
# 単語の情報をまとめたクラス
#--------------------------------------------------
class WordInfo():
    def __init__(self):
        self.input = ''
        self.initial = ''
        self.tail = ''
        self.next_initial = ''
        self.reading = ''
        self.url = ''

    #--------------------------------------------------
    # 引数の単語のコトバンクページのURLをつくり, 
    # そこから単語の読み方をスクレイピングし, 
    # さらに単語のinitial, tailを設定する
    # initialとtailはすべてひらがなになる
    #--------------------------------------------------    
    def set_word_info_by_scraping(self, word, debug_flag):
        self.input = word
        self._set_URL(word, debug_flag)
        
        word_title = self._scraping_word_title(self.url)
        if word_title == 'コトバンク - お探しのペ':
            word_read = word_title
            self.reading = word_title
            self.initial = hk.to_hira(word_title[0])
        else:
            if hk.is_hira(word_title):
                word_read = word_title
            elif hk.is_kata(word_title):
                word_read = hk.to_hira(word_title)
            else:
                word_read = self._scraping_word_reading(self.url)            
            
            if word_read == NULL:
                word_read = 'コトバンク - お探しのペ'

            self.reading = word_read
            self.initial = hk.to_hira(word_read[0])
        
        if word_read[-1] == 'ー':
            self.tail = hk.to_hira(word_read[-2])
        else:
            self.tail = hk.to_hira(word_read[-1])
        if hk.is_komoji(self.tail) == True:
            self.tail = hk.to_oomoji(self.tail)

    def _scraping_word_title(self, url):
        html_doc = requests.get(url).text
        soup = BeautifulSoup(html_doc, 'html.parser')           # BeautifulSoupの初期化
        real_page_tag = soup.find("title")                      # titleタグの部分を見つけて格納する. ここでは 'ラーメン' を例に挙げる
        title_read_tmp  = real_page_tag.string                  # 文字列にして<title>, </title>を削除する
        title_read = title_read_tmp[:-10]                       # 無駄な部分を取り除く
        if ')' in title_read and ')' in title_read:             # 漢字(ふりがな) というフォーマットならば
            title_read_kakko_idx = title_read.index('(') + 1    # (の次のidxを代入
            title_read = title_read[:-1]                        # )は末尾にあるので取り除く
            title_read = title_read[title_read_kakko_idx:]      # ふりがなの部分のみを抽出する
        return title_read

    #--------------------------------------------------
    # requestsモジュールとbs4モジュールを用いて
    # 引数のURLから該当単語の読みをスクレイピングする 
    #--------------------------------------------------    
    def _scraping_word_reading(self, url):
        html_doc = requests.get(url).text
        soup = BeautifulSoup(html_doc, 'lxml')           # BeautifulSoupの初期化
        all_text = soup.find(class_="bodyWrap").text
        all_text_list = all_text.split('\n')
        for text in all_text_list:
            if "（読み）" in text:
                read_tmp = text
                break
        else:
            return NULL
        i = 0
        word_len = len(read_tmp)
        while read_tmp[i] != '）':
            i += 1
            if i >= word_len:
                break
        start = i
        
        while read_tmp[i] != '（':
            i += 1
            if i >= word_len:
                break
        
        if start >= word_len:
            return read
        elif i >= word_len:
            read = read_tmp[(start+1):]
        else:
            read = read_tmp[(start+1):i]
            
        return read

    #--------------------------------------------------
    # 引数の単語のコトバンクページのURLをつくる
    #--------------------------------------------------    
    def _set_URL(self, word, debug_flag):
        url_top = 'https://kotobank.jp/word/'
        word_byte = word.encode('utf-8')
        hex_string = str(binascii.hexlify(word_byte), 'utf-8')          # byte列を文字列に変換する
        hex_string = hex_string.upper()                                 # 大文字に変換する
        
        words = []                                                      # byte列を2文字ずつ格納する
        for i in range(len(hex_string)//2):                             # byte列の文字数/2回繰り返す
            words.append(hex_string[i*2:i*2+2])                         # 先頭から2文字ずつ切り取ってwords[i]に格納する

        url_latter = ""                                                 # URLの後半部分. 人間が入力した文字列をutf-8に変換したもの

        for i in range(len(words)):
            words[i] = '%' + words[i]                                   # 2文字ごとに%をつける(仕様)
            url_latter = url_latter + words[i]                          # 末尾に連結

        self.url = url_top + url_latter                                 # 完成したURL
        if debug_flag == True:
            print("URL : " + self.url)

    #--------------------------------------------------
    # self.inputがコトバンクに存在する単語か否かを判定
    #--------------------------------------------------
    def is_exist_input(self):
        return self.reading != 'コトバンク - お探しのペ'