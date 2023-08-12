import sys
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QFormLayout, QVBoxLayout, QWidget
import re
import pandas as pd
import copy
import pygraphviz as pyg
from treelib import Tree
import json
from PyQt5.QtWidgets import QApplication, QLabel, QWidget


#oplst=['+','-','*','/','%','^','(',')']
def split_expression(expression):#使用正则表达式将表达式拆分为数字、运算符和括号
    tokens = re.findall(r'\d+\.?\d*|\w+|\S', expression)
    # 去除空格，并将拆分后的结果存放在列表中
    result = [token.strip() for token in tokens if token.strip()]
    return result
def split_productions(txt):#分割文法产生式  ['A1 -> A1+B', 'A1 -> A1-B', 'A1 -> B', 'B -> B*C', 'B -> B/C', 'B -> B%C', 'B -> C', 'C -> C^D', 'C -> D', 'D -> (A1)', 'D -> v']
    productions = []
    lines = txt.split('\n')
    for line in lines:
        if '—>' in line:
            non_terminal, production_str = line.split('—>')
            non_terminal = non_terminal.strip()
            productions_list = [p.strip() for p in production_str.split('|')]
            for production in productions_list:
                productions.append(f"{non_terminal} —> {production}")
    return productions

def split_productions1(productions):#[0][0]:['A', '—', '>', 'A', '+', 'B']
    split_productions_list = []

    for production in productions:
        split_production = re.findall(r'\w+|\W', production)
        split_production = [element.strip() for element in split_production if element.strip() != '']
        split_productions_list.append(split_production)
    return split_productions_list

def extract_VT_and_VN(lst):
    VT = set(['+', '-', '*', '/', '%', '^', '(', ')', 'v','i'])
    VN = set()
    VT1=set()
    for sublist in lst:
        for item in sublist:
            if item in VT:
                VT1.add(item)
            if item not in VT and item != '>' and item !='—':
                VN.add(item)

    VT.discard('>')
    
    return list(VT1), list(VN)


#FIRSTVT  LASTVT

txt1='A1—>A1+B|A1-B|B\n\
B—>B*C|B/C|B%C|C\n\
C—>C^D|D\n\
D—>(A1)|v\n'
txt2='E—>E+T|E-T|T\n\
T—>T*F|T/F|F\n\
F—>P^F|P\n\
P—>(E)|v\n'

txt3='1+2*3-4/2'
txt4='12-2*3-4/2+9^2'
txt5='a+bc-12*34/(abc/(1^d))'

#print(split_productions1(split_productions(txt1)))


#print(input_list)

#terminals, nonterminals = extract_VT_and_VN(input_list)
def move(str1,str2,M,VT):
    for i in VT:
        if M.at[str1,i]==1:
            M.at[str2,i]=1
def getFIRSTVT(biglst:list):#biglst:[  ['A1', '-', '>', 'A1', '+', 'B'],  ['C', '-', '>', 'D'], ['D', '-', '>', '(', 'A1', ')'], ['D', '-', '>', 'v']   ]
    VT,VN=extract_VT_and_VN(biglst)
    #print(VT)
    #print(VN)
    M= pd.DataFrame(index=VN, columns=VT)
    for i in range(len(VN)):# M全部置0
       for j in range(len(VT)):
           M.at[VN[i],VT[j]] =0
    
    M1=copy.deepcopy(M)
    while(1):
        M1=copy.deepcopy(M)
        for i in biglst:# i: ['A1', '-', '>', 'A1', '+', 'B']
            if len(i)==4:
                if i[3] in VT:
                    M.at[i[0],i[3]]=1
                else:
                    #i[3]->i[0]
                    move(i[3],i[0],M,VT)
            else:
                if i[3] in VT:#P->a...则a->FIRSTVT[P]
                    M.at[i[0],i[3]]=1
                else:
                    move(i[3],i[0],M,VT)
                    if i[4] in VT:
                        M.at[i[0],i[4]]=1
        if M1.equals(M):
            break
    
    return M
#print(input_list)

def getLASTVT(biglst:list):
    VT,VN=extract_VT_and_VN(biglst)
    M= pd.DataFrame(index=VN, columns=VT)
    for i in range(len(VN)):# M全部置0
       for j in range(len(VT)):
           M.at[VN[i],VT[j]] =0
    M1=copy.deepcopy(M)
    while(1):
        M1=copy.deepcopy(M)
        for i in biglst:# i: ['A1', '-', '>', 'A1', '+', 'B']
            if len(i)==4:
                if i[3] in VT:#P->a
                    M.at[i[0],i[3]]=1
                else:
                    #i[3]->i[0]
                    move(i[3],i[0],M,VT)
            else:
                if i[-1] in VT:#P->...a 则a->LASTVT[P]
                    M.at[i[0],i[-1]]=1
                else:
                    move(i[-1],i[0],M,VT)#P->...Q
                    if i[-2] in VT:
                        M.at[i[0],i[-2]]=1
        if M1.equals(M):
            break
    return M

#print(getFIRSTVT(input_list))
#print(getLASTVT(input_list))#
def gettable(FM,LM,biglst:list):
    VT,VN=extract_VT_and_VN(biglst)
    table = pd.DataFrame(index=VT, columns=VT)
    for i in biglst:# FOR每条产生式 P→×1×2...Xn DO
        for j in range(3,len(i)-1):#FOR i:=1 TO n-1 DO
            if i[j] in VT and i[j+1] in VT:
                table.at[i[j],i[j+1]]='='
            if j<len(i)-2 and i[j] in VT and i[j+2] in VT and i[j+1] in VN:#['D', '-', '>', '(', 'A1', ')']
                table.at[i[j],i[j+2]]='='
            if i[j] in VT and i[j+1] in VN:
                for k in list(FM.columns[FM.loc[i[j+1]] == 1]):
                    table.at[i[j],k]='<'
            if i[j] in VN and i[j+1] in VT:
                for k in list(LM.columns[LM.loc[i[j]] == 1]):
                    table.at[k,i[j+1]]='>'
    print(list(FM.columns[FM.loc[biglst[0][0]] == 1]))
    for k in list(FM.columns[FM.loc[biglst[0][0]] == 1]):
        table.at['#',k]='<'
    for k in list(LM.columns[LM.loc[biglst[0][0]] == 1]):
        table.at[k,'#']='>'
    table.at['#','#']='='
    #print(table)
    return table
#print(gettable(getFIRSTVT(input_list),getLASTVT(input_list),input_list))

def compare(littlelst:list,S:list,VT:list):
    if len(littlelst)!=len(S)+3:
        return 0
    else:
        for i in range(len(S)):
            if littlelst[i+3] in VT:
                if littlelst[i+3]==S[i]:
                    continue
                else:
                    return 0
        return 1
def ana(lst:list,table:pd.DataFrame,VT:list,VN:list,biglst:list):#lst是待处理的表达式
    tree = Tree()
    tree.create_node('#','#')
    lst1=[]#A1 B1 B2 A3
    lst2=[]# *  + /  -
    Slst=[]
    lst.append('#')
    VT.append('#')
    S=[]
    S.append('#')
    count=0
    cou1=0
    cou2=0
    while(1):
        #print('lst:',lst)
        if count==len(lst):
            print(count)
            break
        #
        #print('S;',S)
        tmps=copy.deepcopy(S)
        Slst.append(tmps)
        #print('Slst:',Slst)
        #print(count)
        a=lst[count]
        #print('a:',a)
        count+=1
        if a not in VT:
            S.append(a)
            continue
        if S[-1] in VT:
            j=len(S)-1
        else:
            j=len(S)-2
        #print('S:',S[j]," a:",a)
        while table.at[S[j],a]=='>':#这时候需要归约了
            while(1):
                Q=S[j]
                if S[j-1] in VT:
                    j=j-1
                else:
                    j=j-2
                #print('sj:',S[j],'Q:',Q)
                if table.at[S[j],Q]=='<':
                    break

            #把S[j+1]...S[k]归约为某个N
            for i in biglst:#  i:  ['A1', '-', '>', 'A1', '+', 'B']
                #print('i:',i,' s:',S,'  sj:',S[j:])
                if compare(i,S[j+1:],VT)==1:
                    #print(222)
                    k=S[j+1:]#['1', '+', 'B0']
                    tree.create_node(k[1],i[0]+str(cou1),parent='#')
                    lst1.append(i[0]+str(cou1))
                    lst2.append(k[1])
                    if k[0] in lst1:
                        tree.move_node(k[0],i[0]+str(cou1))
                    else:
                        tree.create_node(k[0],k[0]+str(cou2),parent=i[0]+str(cou1))
                    if k[2] in lst1:
                        tree.move_node(k[2],i[0]+str(cou1))
                    else:
                        #tree.show()
                        #print(k)
                        tree.create_node(k[2],k[2]+str(cou2),parent=i[0]+str(cou1))
                    #print('S:',S)
                    tmps=copy.deepcopy(S)
                    Slst.append(tmps)
                    S=S[:j+1]#k=j+1
                    S.append(i[0]+str(cou1))#S[k]=N
                    cou1+=1
                    cou2+=1
                    #print('S:',S)
                    tmps=copy.deepcopy(S)
                    Slst.append(tmps)
                    break
            #print('S:',S[j]," a:",a)
        #print('S:',S[j]," a:",a)
        
        if table.at[S[j],a]=='<' or table.at[S[j],a]=='=':
            S.append(a)
            
        else:
            print('error')
            return
        if a=='#':
            #print('S:',S)
            Slst.append(S)

            new_Slst =  [x for i, x in enumerate(Slst) if i == 0 or x != Slst[i-1]]
            for i in new_Slst:
                #print(i)
                pass
            tree.show()
            json_data = tree.to_json(with_data=True)
            data = json.loads(json_data)
            file_path = "data.json"
            with open(file_path, "w") as file:
                json.dump(data, file)
            return new_Slst
            break

txt1='A1—>A1+B|A1-B|B\n\
B—>B*C|B/C|B%C|C\n\
C—>C^D|D\n\
D—>(A1)|v\n'
txt2='E—>E+T|E-T|T\n\
T—>T*F|T/F|F\n\
F—>P^F|P\n\
P—>(E)|v\n'

txt3='1+2*3-4/2'
txt4='12-2*3-4/2+9^2'
txt5='a+bc-12*34/(abc/(1^d))'
input_list = split_productions1(split_productions(txt1))
VT,VN=extract_VT_and_VN(input_list)


#ana(split_expression(txt5),gettable(getFIRSTVT(input_list),getLASTVT(input_list),input_list),VT,VN,input_list)
#txt3='1+2*3-4/2'

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.input_list = []
        self.new_Slst = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("字符串处理窗口")

        # 创建输入框1和输入框2
        self.input_text1 = QLineEdit()
        self.input_text2 = QLineEdit()

        
        
        # 设置输入框的最小尺寸
        self.input_text1.setMinimumSize(300, 30)

        
        # 创建提交按钮
        self.submit_button = QPushButton("提交")
        self.submit_button.clicked.connect(self.process_input)
        
        # 创建显示结果的标签
        self.result_label = QLabel()
        
        # 创建表单布局，并添加输入框和标签
        form_layout = QFormLayout()
        form_layout.addRow("输入框1:", self.input_text1)

        
        layout = QVBoxLayout()#创建垂直布局对象
        layout.addLayout(form_layout)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)

    def process_input(self):
        input_string1 = self.input_text1.text()
        print(input_string1)
        # 保存输入的字符串到input_list列表中
        txt1 ='A1—>A1+B|A1-B|B\n\
        B—>B*C|B/C|B%C|C\n\
        C—>C^D|D\n\
        D—>(A1)|v\n'
        
        input_list = split_productions1(split_productions(txt1))
        VT,VN=extract_VT_and_VN(input_list)
        # 将处理后的结果设置到结果标签中进行显示
        self.new_Slst=ana(split_expression(input_string1),gettable(getFIRSTVT(input_list),getLASTVT(input_list),input_list),VT,VN,input_list)
        result=''
        for i in self.new_Slst:
            result=result+str(i)+'\n'
        self.result_label.setText(result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    
    # 设置窗口尺寸
    window.resize(400, 300)
    
    window.show()
    
    sys.exit(app.exec_())
#    1+2*3-4/2
#txt4='    12-2*3-4/2+9^2
#txt5='      a+b-12*34/(abc/(1^d))
