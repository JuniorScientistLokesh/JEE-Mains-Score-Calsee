from PySide6.QtWidgets import QTextEdit, QApplication
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QPushButton, QGridLayout
import qdarktheme
from itertools import count
import traceback
from datetime import datetime
def MCQ(f):
    data = [f.readline() for x in range(12)]
    q_type = data[4].partition(":")[-1].strip()
    que_ID = int(data[5].partition(':')[-1].strip())
    if 'Not ' not in data[10]:
        choice = int(data[-1].partition(':')[-1].strip())
        opt_ID = int(data[5 + choice].partition(':')[-1].strip())
    else:
        opt_ID = None
    return {que_ID: opt_ID}


def SA(f):
    data = [f.readline() for _ in range(4)]
    try:
        que_ID = int(data[2].partition(':')[-1].strip())
    except: 
        print('\n'.join(data))
    if 'Not ' not in data[3]:
        answer = float(data[0].partition(':')[-1].strip())
    else:
        answer = None
    return {que_ID: answer}


def getData(path):
    with open(path) as f:
        data = dict()
        sec_A = False
        for n in count():
            line = f.readline()
            if line == '':
                break
            if 'Section :' in line:
                sec = line.partition('Section :')[-1]
                if 'A' in sec.split(' ')[-1]:
                    sec_A = True
                elif 'B' in sec.split(' ')[-1]:
                    sec_A = False
                data[sec] = {}
            elif line.startswith('Q.'):
                if sec_A:
                    data[sec].update(MCQ(f))
                else:
                    data[sec].update(SA(f))
    return data


def getAnswerkey(path):
    with open(path) as f:
        key = dict()
        for line in f.readlines():
            if line.startswith('B TECH'):
                line = line.split('\t')
                key[int(line[1])] = int(line[2])
    return key


def calcMarks(data, key):
    marks = 0
    temp_marks = 0
    c = w = 0
    c_ = w_ = 0

    text='Section Wise analytics\n'
    for section in data:
        text+='=' * 27 + '\n' + section + '=' * 27+'\n'
        for qid in data[section]:
            # print(key[qid], data[section][qid], end='')
            if key[qid] == data[section][qid]:
                marks += 4
                c += 1
            elif data[section][qid] is not None:
                marks -= 1
                w += 1

        pr = f'''No of correct questions: {c - c_}
No of wrong questions: {w - w_}
Total questions attended: {w - w_ + c - c_}
marks:\t{marks - temp_marks}\n\n
'''
        c_ = c
        w_ = w

        text+=(pr)
        temp_marks = marks
    out = f'''
Total Marks:\t{marks}
No of correct questions: {c}
No of wrong questions: {w}
Total question attended: {c + w}
'''
    return text,out


def run():
    data = getData('MyAnswers')
    key = getAnswerkey('AnswerKey')
    return calcMarks(data, key)

messageL = '''


Just simple, open page with your answers : ctrl+a, ctrl+c
then paste it here





Ohh one more thing, All The Best

'''
messageR = '''


Just simple, open page with your answerKeys : ctrl+a, ctrl+c
then paste it here
'''


class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.setWindowTitle('JEE Mains Score Calsee')
        self.setWindowIcon(QIcon('logo.ico'))
        self.layout = QGridLayout(self)
        self.LTEdit = QTextEdit()
        self.LTEdit.setPlaceholderText('Your answers should be pasted here' + messageL)
        self.RTEdit = QTextEdit()
        self.RTEdit.setPlaceholderText('Answer Key must be pasted here' + messageR)
        self.button_submit = QPushButton('Submit')
        self.button_submit.clicked.connect(self.submitAction)
        self.LTEdit.setAcceptRichText(False)
        self.RTEdit.setAcceptRichText(False)

        self.layout.addWidget(self.LTEdit, 0, 0)
        self.layout.addWidget(self.RTEdit, 0, 1)
        self.layout.addWidget(self.button_submit, 1, 0)

    def submitAction(self):
        try:
            with open('MyAnswers', 'w') as f:
                f.write(self.LTEdit.toPlainText())
            with open('AnswerKey', 'w') as f:
                f.write(self.RTEdit.toPlainText())
            data = getData('MyAnswers')
            key = getAnswerkey('AnswerKey')
            text_L, text_R = calcMarks(data, key)
            self.LTEdit.clear()
            self.RTEdit.clear()
            self.LTEdit.setText(text_L)
            self.RTEdit.setText(text_R)
            self.LTEdit.setReadOnly(True)
            self.RTEdit.setReadOnly(True)
            self.button_submit.setText('Reset')
            self.button_submit.clicked.connect(self.reset)
        except Exception as e:
            with open('error.log','a') as f:
                f.write('====='+ str(datetime.now())+'=====\n')
                f.write(traceback.format_exc())
                f.write('====================================')


    def reset(self):
        self.LTEdit.clear()
        self.RTEdit.clear()
        self.LTEdit.setReadOnly(False)
        self.RTEdit.setReadOnly(False)
        self.button_submit.setText('Submit')
        self.button_submit.clicked.connect(self.submitAction)


app = QApplication()
app.setStyleSheet(qdarktheme.load_stylesheet())
widget = MainWidget()
widget.resize(800, 600)
widget.show()
app.exec()
