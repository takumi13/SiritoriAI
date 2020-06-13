
#coding: utf-8

import twitter_word_learning
import siritoriAI

def main():
    debug_flag = False
    print('[メニュー]')
    print('AIとしりとりがしたい　　　　　　　：1')
    print('AIとしりとりがしたい(debug mode)  ：2')
    print('ツイートから未知単語を学習したい　：3')
    print('Twitterからツイートを取得したい　 ：4')
    select = int(input('選択：'))
    
    if select == 1:
        debug_flag = False
        siritoriAI.main(debug_flag)
    elif select == 2:
        debug_flag = True
        siritoriAI.main(debug_flag)
    elif select == 3:
        twitter_word_learning.main()
    elif select == 4:
        twitter_word_learning.view_timeline()
    else:
        print('存在しないコマンドです')
    

if __name__ == '__main__':
    main()