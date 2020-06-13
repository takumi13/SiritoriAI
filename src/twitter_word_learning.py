
#coding: utf-8

import tweepy
import config
import random
from janome.tokenizer import Tokenizer

import hirakata as hk
import DictionaryClass
import WordInfoClass

##################################################333
CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATK = config.ACCESS_TOKEN_SECRET
##################################################333

#--------------------------------------------------
# TwitterAPIを取得
#--------------------------------------------------
def get_twieetr_api(CK, CS, AT, ATK):
    try:                                    #例外処理
        auth = tweepy.OAuthHandler(CK, CS)  #authにCONSUMER_KEYとCONSUMER_SECRETを渡す
        auth.set_access_token(AT, ATK)      #authにアクセストークンをセットする
        API = tweepy.API(auth)              #記述を楽にする
    except tweepy.TweepError as e:          #エラーが発生した場合TweepErrorが返ってくる
        print(e.reason)                     #エラー内容を出力
    return API

###########################################################################
api = get_twieetr_api(CK, CS, AT, ATK)
############################################################################

#-----------------------------------------------------
# TwitterAPIを用いてツイートをテキストとしてcount数取得
#-----------------------------------------------------
def get_text(q, count=100):
    text_list = []
    search_results = api.search(q=q, count=count)
    for tweet in search_results:
        text = tweet.text.encode('cp932', "ignore")
        text = text.decode('cp932')
        text = text.encode('utf-8', "ignore")
        text_list.append(text.decode('utf-8'))
    return text_list

#--------------------------------------------------
# 検索ワードをランダム決定
#--------------------------------------------------
def define_word():
    word = ''
    k = random.randint(0, 44)
    word = hk.hiragana[k]
    return word

#--------------------------------------------------
# ツイートから名詞を抽出する
#--------------------------------------------------
def extract_word(dictionary, text_list):
    debug_flag = False
    word = WordInfoClass.WordInfo()
    t = Tokenizer()
    cnt = 0
    for text in text_list:
        for token in t.tokenize(text):
            if token.part_of_speech.split(',')[0] == '名詞' and len(token.surface) >= 2 and token.reading != '*':
                word.set_word_info_by_scraping(token.surface, debug_flag)
                # if (word.reading == 'コトバンク - お探しのペ'):
                if word.is_exist_input() == False:
                    print('[ NG ]' + token.surface)
                else:
                    print('[', cnt, ']' +  token.surface + '(' + word.initial + ')')
                    cnt+=1
                    if word.tail != 'ん' and token.surface not in dictionary[word.initial]:
                        if dictionary[word.initial][0] == '':
                            dictionary[word.initial][0] = token.surface
                        else:
                            dictionary[word.initial].append(token.surface)
    for key in dictionary:
        if dictionary[key][0]=='' and len(dictionary[key])==1:
            dictionary[key] = []
    return dictionary

#--------------------------------------------------
# ツイート詳細情報
#--------------------------------------------------
def _tweet_info(tweet):
	print('--------------------------------------------------------------------------------------------')
	user_name = tweet.user.name.encode('cp932', "ignore")
	user_screen_name = tweet.user.screen_name.encode('cp932', "ignore")
	user_id = tweet.id
	text = tweet.text.encode('cp932', "ignore")
	time = tweet.created_at
	print(user_name.decode('cp932'), '(', user_screen_name.decode('cp932'), ')')
	print('ID:', user_id)
	print('[Tweet]\n', text.decode('cp932'))
	print(time)

#--------------------------------------------------
# ツイートを表示する
#--------------------------------------------------
def _print_tweet(q, count):
    search_results = api.search(q=q, count=count)
    for tweet in search_results:
        _tweet_info(tweet)

#--------------------------------------------------
# タイムラインを見る
#--------------------------------------------------
def view_timeline():
    word = input('検索ワード:')
    num = int(input('検索ツイート数(最大100個)：'))
    if num > 100:
        num = 100
    _print_tweet(word, num)

#--------------------------------------------------
# main文
#--------------------------------------------------
def main():
    dic = DictionaryClass.Dictionary()
    search_word = define_word()
    word_num = int(input('取得したいツイート数(最大10個)：'))
    if word_num > 10:
        word_num = 10
    text_list = get_text(search_word, word_num)
    print('---------------------------------------------------------------------------------------------------------')
    for text in text_list:
        print(text)
    print('---------------------------------------------------------------------------------------------------------')
    dic.twi_dictionary = extract_word(dic.null_dictionary, text_list)
    dic.merge_twi_dictionary_file()