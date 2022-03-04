
#coding: utf-8

import random
import sys

import hirakata as hk
import DictionaryClass
import WordInfoClass

#--------------------------------------------------
# main文
#--------------------------------------------------
def main(debug_flag):
    dic = DictionaryClass.Dictionary()
    word_player = WordInfoClass.WordInfo()
    word_AI     = WordInfoClass.WordInfo()
    
    for key in dic.used_dictionary:
        dic.used_dictionary[key].clear()
    
    # if debug_flag == True:
    #     print("------------------------------------------------------------------------------------------------------------------------------------------------")
    #     for key in dic.dictionary:
    #         print('key=' + key + ' :', end=' ')
    #         print(dic.dictionary[key])
    #     print("------------------------------------------------------------------------------------------------------------------------------------------------")

    rally_cnt = 0
    loop_flag = True
    end_flag = False
    name_flag = True
    end_cnt = 0
    
    while loop_flag == True:
        #--------------------------------------------------
        # 人間の名前を入力
        #--------------------------------------------------
        if name_flag == True:
            print('\nしりとりを終了したいときは, Enterキーを3回連続で押してください(ゲーム中もこの操作は有効です).')
            player_name = input("あなたの名前を教えてください：")
            print('\n' + player_name + "さんですね. よろしくお願いします.")
            print("しりとりはあなたからです. 好きな単語から始めてください.")
            print("------------------------------------------------------------------------------------------------------------------------------------------------\n")
            name_flag = False

        while True:
            #--------------------------------------------------
            # 人間の入力. 3回連続でEnterキーを押したらシステム終了
            #--------------------------------------------------
            while True:
                word_player_input = input(player_name + " : ")
                if word_player_input == '':
                    end_cnt += 1
                else:
                    break
                if end_cnt == 3:
                    loop_flag = True
                    end_flag = True
                    break
            
            #--------------------------------------------------
            # Enterキーが3回押されてるか否かを判定
            # Enterキーを3回連続で押した場合, システムを停止する
            # しりとりが続いていれば, エンドカウンターを初期化
            #--------------------------------------------------
            if end_flag == True:
                print(rally_cnt, "回続いたよ\n")
                print('対戦ありがとうございました\n')
                #--------------------------------------------------
                # しりとり中に強制終了したとき用の辞書更新
                #--------------------------------------------------    
                if rally_cnt != 0:
                    #--------------------------------------------------
                    # 使用済み辞書を操作して, 辞書にない単語(人間が入力した単語)
                    # があれば, 辞書に追加登録する
                    #--------------------------------------------------
                    dic.merge_dictionary(dic.used_dictionary, dic.used_filepath)

                    #--------------------------------------------------
                    # 使用済み辞書をリセットする
                    #--------------------------------------------------
                    for key in dic.used_dictionary:
                        dic.used_dictionary[key].clear()

                #--------------------------------------------------
                # 更新された辞書を, 辞書ファイルに書き出す
                # すなわち,辞書ファイルを更新する(自律学習)
                #--------------------------------------------------
                dic.write_dictionary_file()
                sys.exit()
            else:
                end_cnt = 0

            #--------------------------------------------------
            # 人間の単語のURL生成, キーワード抽出
            #--------------------------------------------------
            word_player.set_word_info_by_scraping(word_player_input, debug_flag)
            
            #--------------------------------------------------
            # カタカナひらがな変換をして再検索
            #--------------------------------------------------
            if word_player.is_exist_input() == False:
                if hk.is_hira(word_player.input) == True:
                    word_player.input = hk.to_kata(word_player.input)
                elif hk.is_kata(word_player.input) == True:
                    word_player.input = hk.to_hira(word_player.input)
                word_player.set_word_info_by_scraping(word_player.input, debug_flag)

            #--------------------------------------------------
            # 変換をして再検索しても見つからない ⇒ 入力に戻る
            #--------------------------------------------------    
            # if word_player.reading == 'コトバンク - お探しのペ':
            if word_player.is_exist_input() == False:
                print("ごめんさない. その単語はこのしりとりには使えません.")
                print("もし漢字に変換できる単語であれば, お手数ですが, 漢字に変換して再度入力してください\n")
            
            #--------------------------------------------------
            # この時点で, コトバンクで単語は見つかっている
            #--------------------------------------------------    
            else:
                #--------------------------------------------------
                # 人間の一回目の入力ではない, かつ
                # 人間が単語下入力の頭文字が
                # 直前にAIが出力した単語の語尾と一致しない
                # 入力のループから抜け出せない
                #--------------------------------------------------
                if word_player.next_initial != '' and word_player.next_initial != word_player.initial:
                    print('しりとりになってません')
                    print('「' + word_player.next_initial + '」で始まる言葉を入力してください\n')
                #--------------------------------------------------
                # 入力のループから抜け出す
                #--------------------------------------------------
                else:
                    break      
        #--------------------------------------------------
        # AIのnext_initialを設定する
        #--------------------------------------------------
        word_AI.next_initial = hk.to_hira(word_player.tail)
        
        #--------------------------------------------------
        # この時点で, 人間の入力はしりとりとして機能している
        # 人間が入力した単語が既出 ⇒ AI勝利宣言
        #--------------------------------------------------
        if rally_cnt > 0 and word_player.input in dic.used_dictionary[word_player.initial]:
            print("その言葉はすでに使われています")
            print(rally_cnt, "回続いたよ")
            print("私の勝ちです\n")
            loop_flag = False
        
        #--------------------------------------------------
        # 「ん」で終わる単語 ⇒ AI勝利宣言
        #--------------------------------------------------
        elif word_AI.next_initial == 'ん' or word_AI.next_initial == 'ン':
            print("「ん」で終わりました")
            print(rally_cnt, "回続いたよ")
            print("私の勝ちです\n")
            loop_flag = False
        
        #--------------------------------------------------
        # この時点で, 人間の入力は完了し, AIの出力ターンに移る
        # ラリー回数を増やし, 使用済み辞書に単語を登録する
        # ここ以前で使用済み辞書に登録すると、語尾が「ん」の単語を
        # 登録してしまう恐れがあるので注意
        # また, 人間の入力単語が辞書に入っている場合は, 
        # 辞書からその単語を一時的に取り除く
        #--------------------------------------------------
        else:
            rally_cnt += 1
            dic.used_dictionary[word_player.initial].append(word_player.input)
            
            if word_player.input in dic.dictionary[word_player.initial]:
                dic.dictionary[word_player.initial].remove(word_player.input)
            #--------------------------------------------------
            # 人間の入力がひらがな・カタカナの場合, 
            # ひらがな。カタカナ表記の同じ単語が辞書にあれば取り除く
            #--------------------------------------------------
            if hk.is_hira(word_player.input) == True or hk.is_kata(word_player.input) == True:
                if hk.to_hira(word_player.input) in dic.dictionary[word_player.initial]:
                    dic.dictionary[word_player.initial].remove(hk.to_hira(word_player.input))
                if hk.to_kata(word_player.input) in dic.dictionary[word_player.initial]:
                    dic.dictionary[word_player.initial].remove(hk.to_kata(word_player.input))
        
            #--------------------------------------------------
            # 辞書に使える単語が残っていなければ
            #--------------------------------------------------
            dict_len = len(dic.dictionary[word_AI.next_initial])-1
            if dict_len == 0:
                print("私の負けです")
                print(rally_cnt, "回続いたよ\n")
                loop_flag = False
            
            #--------------------------------------------------
            # AIが出力する単語を辞書から乱数的に取り出す
            #--------------------------------------------------
            else:
                rnd = random.randint(0, dict_len)
                word_AI_dict = dic.dictionary[word_AI.next_initial][rnd]
            
                #--------------------------------------------------
                # AIが出力した単語を辞書から削除し
                # 使用済み辞書に登録する
                #--------------------------------------------------
                dic.dictionary[word_AI.next_initial].remove(word_AI_dict)
                dic.used_dictionary[word_AI.next_initial].append(word_AI_dict)
                
                #--------------------------------------------------
                # AIの単語のコトバンクページのURLをつくり, 
                # そこから単語の読み方をスクレイピングし, 
                # さらに単語のinitial, tailを設定する
                #--------------------------------------------------    
                word_AI.set_word_info_by_scraping(word_AI_dict, debug_flag)
                
                #--------------------------------------------------
                # 人間のnext_initialを設定
                #--------------------------------------------------
                word_player.next_initial = word_AI.tail
                
                #--------------------------------------------------
                # そもそも語尾が「ん」の単語は辞書登録しないように
                # フィルタリングしているが念のため記述
                #--------------------------------------------------
                if word_player.next_initial == 'ん':
                    print('私の負けです')
                    print(rally_cnt, '回続いたよ')
                    loop_flag = False

                #--------------------------------------------------
                # 人間が次に入力する単語の頭文字確定
                # AIの単語の出力を行い, 人間の入力部に戻る
                #--------------------------------------------------
                if hk.is_hira(word_AI.input) == True or hk.is_kata(word_AI.input) == True:
                    print("AI : " + word_AI.input + '\n')
                else:
                    print("AI : " + word_AI.input + '(' + word_AI.reading + ')\n')
        #--------------------------------------------------
        # 勝敗が決している場合
        # もろもろの初期化と, 辞書の更新(学習)
        #--------------------------------------------------
        if loop_flag == False:
            print("------------------------------------------------------------------------------------------------------------------------------------------------\n")
            word_player.next_initial = ''
            word_AI.next_initial     = ''
            loop_flag = True
            end_flag  = False
            name_flag = True
            end_cnt   = 0
            rally_cnt = 0
            #--------------------------------------------------
            # 使用済み辞書を操作して, 辞書にない単語(人間が入力した単語)
            # があれば, 辞書に追加登録する
            #--------------------------------------------------
            dic.merge_dictionary(dic.used_dictionary, dic.used_filepath)

            #--------------------------------------------------
            # 使用済み辞書をリセットする
            # dic[key].clear()などとしないのは, 
            # 要素のリストすべてを['']にするため
            # clear()を使うと[]になってしまう
            #--------------------------------------------------
            dic.used_dictionary = dic.read_dictionary(dic.keywords)

            #--------------------------------------------------
            # 更新された辞書の表示
            #--------------------------------------------------
            # if debug_flag == True:
            #     print("------------------------------------------------------------------------------------------------------------------------------------------------")
            #     for key in dic.dictionary.keys():
            #         print('key=' + key + ' :', end=' ')
            #         print(dic.dictionary[key])
            #     print("------------------------------------------------------------------------------------------------------------------------------------------------")
            #     print()
