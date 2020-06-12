
#coding: utf-8

import shutil
import os

class Dictionary:
    def __init__(self):
        self.filepath         = './dictionary/dictionary.txt'
        self.old_filepath     = './dictionary/dictionary_old.txt'
        self.twi_filepath     = './dictionary/dictionary_twi.txt'
        self.twi_old_filepath = './dictionary/dictionary_twi_old.txt'
        self.used_filepath    = './dictionary/used_dictionary.txt'
        self.keywords         = './dictionary/keyword.txt'
        self.dictionary       = self.read_dictionary(self.filepath)
        self.null_dictionary  = self.read_dictionary(self.keywords)
        self.twi_dictionary   = self.read_dictionary(self.keywords)
        self.used_dictionary  = self.read_dictionary(self.keywords)

    #--------------------------------------------------
    # dictionaryディレクトリ下にある任意の辞書ファイルを
    # 読み込んで, 辞書型変数dを作り、返す
    #--------------------------------------------------
    def read_dictionary(self, filepath):
        d = {}
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                key = line[0]
                words = line[2:-1].split(',')
                d[key] = words
        return d
    
    #--------------------------------------------------
    # 現在のdictionaryの内容を辞書ファイルへ書き出す
    # 直前の辞書ファイルはバックアップを取ったあと一度削除し、  
    # 再度新しく辞書ファイルを作る
    #--------------------------------------------------
    def write_dictionary_file(self):
        shutil.copyfile(self.filepath, self.old_filepath)
        os.remove(self.filepath)
        
        with open(self.filepath, "w", encoding="utf-8") as f:
            for key in self.dictionary:
                l = len(self.dictionary[key])
                line = ''
                line = line + key + ':'
                for i in range(l):
                    if i != 0 and i != l-1 and self.dictionary[key][i] == '':                       # 途中に空白が入っていたら
                        continue                                                                    # 無視する (lineには追記しない)
                    elif i != 0 and i == l-1 and self.dictionary[key][i] == '' and line[-1] == ',': # 最後まで到達してかつ語尾がコンマならば
                        line = line[:-1]                                                            # 語尾のコンマは取り除き
                        line = line + '\n'                                                          # 改行文字を追記する
                    else:
                        if i == l-1:
                            line = line + self.dictionary[key][i] + '\n'
                        else:
                            line = line + self.dictionary[key][i] + ','
                f.write(line)

    #--------------------------------------------------
    # 引数のdictionaryの内容を引数の辞書ファイルへ書き出す
    # 直前の辞書ファイルはバックアップを取ったあと一度削除し、  
    # 再度新しく辞書ファイルを作る
    # 引数はTwitter辞書・使用済み辞書のいずれか
    # Twitter辞書の際はdebug_flagをTrueにして呼び出す
    #--------------------------------------------------
    def write_input_dictionary_file(self, filepath, old_filepath, debug_flag):
        input_dictionary = self.read_dictionary(filepath)
        shutil.copyfile(filepath, old_filepath)
        os.remove(filepath)
        
        with open(filepath, "w", encoding="utf-8") as f:
            for key in input_dictionary:
                f.write(key + ':')
                if debug_flag == True:
                    print(key + ':', end='')
                for i in range(len(input_dictionary[key])):
                    if i == len(input_dictionary[key]) - 1:
                        if debug_flag == True:
                            print(input_dictionary[key][i])
                        f.write(input_dictionary[key][i] + '\n')
                    else:
                        if debug_flag == True:
                            print(input_dictionary[key][i], end=',')
                        f.write(input_dictionary[key][i] + ',')

    #--------------------------------------------------
    # 引数のfilepathが与える辞書を操作して, 元の辞書にない 
    # 単語があれば,元の辞書に追加登録する
    #--------------------------------------------------
    def merge_dictionary(self, input_dictionary, input_filepath):
        cnt_dic = 0     # 元の辞書の単語数
        cnt_input = 0   # 引数の辞書の単語数
        cnt_up = 0      # 実際に増えた単語数
        
        #--------------------------------------------------
        # 元の辞書と引数の辞書の単語数の数え上げ
        #--------------------------------------------------
        for key in self.dictionary:
            cnt_dic += len(self.dictionary[key])
        for key in input_dictionary:
            cnt_input += len(input_dictionary[key])
        
        #--------------------------------------------------
        # 元の辞書の更新
        #--------------------------------------------------
        self.dictionary = self.read_dictionary(self.filepath)
        for key in input_dictionary:
            for i in range(len(input_dictionary[key])):
                if input_dictionary[key][i] == '':
                    continue
                elif input_dictionary[key][i] not in self.dictionary[key]:
                    cnt_up += 1
                    if len(self.dictionary[key]) == 0:
                        self.dictionary[key].append('')
                    if self.dictionary[key][0] == '':
                        self.dictionary[key][0] = input_dictionary[key][i]
                    else:
                        self.dictionary[key].append(input_dictionary[key][i])
        
        print("元の辞書の単語数　　：", cnt_dic)
        if input_filepath == self.used_filepath:
            print("取得した単語の数　　：", cnt_input//2)
        else:
            print("取得した単語の数　　：", cnt_input)
        print("実際に増えた単語数　：", cnt_up)
        print("更新後の辞書の単語数：", cnt_dic + cnt_up)
        if cnt_input != 0:
            if input_filepath == self.used_filepath:
                print("単語の学習率　　　　：", cnt_up*100/(cnt_input/2), '%')
            else:
                print("単語の学習率　　　　：", cnt_up*100/cnt_input, '%')
        print("------------------------------------------------------------------------------------------------------------------------------------------------\n")
                
    #--------------------------------------------------
    # filepath と twi_filepath を統合する
    # すなわち, twi_dictionaryをmerge_dictionaryに入力し, 
    # dictionary に存在しない単語を学習し, 
    # 最後にdictionary を filepath へ書き出す
    #--------------------------------------------------
    def merge_twi_dictionary_file(self):
        self.dictionary = self.read_dictionary(self.filepath)

        #--------------------------------------------------
        # 辞書ファイルのバックアップを行う
        #--------------------------------------------------
        shutil.copyfile(self.filepath, self.old_filepath)
        shutil.copyfile(self.twi_filepath, self.twi_old_filepath)
        
        #--------------------------------------------------
        # Twitter辞書を操作して, 元の辞書にない単語があれば, 
        # 元の辞書に追加登録する
        # 最後に更新された辞書を辞書ファイルへ書き出す
        #--------------------------------------------------
        self.merge_dictionary(self.twi_dictionary, self.twi_filepath)
        self.write_dictionary_file()