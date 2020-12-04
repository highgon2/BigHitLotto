import time
import random

import tkinter
import tkinter.ttk
import tkinter.messagebox

from lotto import *

class BigHit:
    __version = 0.01

    def __init__(self):
        self.__abort = 0
        self.__is_loading = 0

        # Window Global Option
        self.__root = tkinter.Tk()

        self.__root.resizable(0, 0)
        self.__root.geometry('600x410+100+100')
        self.__root.option_add('*Font', '맑은고딕 10')
        self.__root.title('BigHit Lotto version {}'.format(BigHit.__version))
        self.__root.protocol('WM_DELETE_WINDOW', self.__remove_dialog)

        self.__str_range = tkinter.StringVar(self.__root, 10)
        self.__chb_optval1 = tkinter.IntVar(self.__root, 1)
        self.__chb_optval2 = tkinter.IntVar(self.__root, 1)
        self.__chb_optval3 = tkinter.IntVar(self.__root, 0)

        if not self.__init_db():
            return

        self.__init_widget()
        self.__set_widget_config()
        self.__add_widget_to_window()

        num = 0
        for i in range(self.__db.last_episode, 0, -1):
            self.__lbx_episode.insert(num, self.__db.get_lottery_episode_string(i))
            num += 1

    def __init_db(self):
        self.__db = db.Manager(1)
        if not self.__db.open():
            msg_result = tkinter.messagebox.askyesno('데이터 생성', '로또 데이터를 생성 하시겠습니까?\n생성하지 않을 경우 프로그램이 종료됩니다.')
            if not msg_result:
                self.__root.destroy()
                return False
            if not self.__draw_dialog():
                return False
        else:
            if self.__db.last_episode != lottery.Episode.get_last_episode():
                prog_value = tkinter.IntVar()

                self.__dialog = tkinter.Toplevel(self.__root)
                self.__dialog.resizable(0, 0)
                self.__dialog.geometry('400x90')
                self.__dialog.attributes('-topmost', 'true')
                self.__dialog.title('Lottery DB')
                self.__dialog.grab_set()
                self.__dialog.transient(self.__root)
                self.__dialog.protocol('WM_DELETE_WINDOW', self.__remove_dialog)

                self.__lbl_load_info = tkinter.Label(self.__dialog, text='로또 DB 구성을 완료할 때까지 기다려주세요.')
                self.__progressbar   = tkinter.ttk.Progressbar(self.__dialog, maximum=100, variable=prog_value)

                self.__lbl_load_info.place(x=10, y=10)
                self.__progressbar.place(x=10, y=45, width=380)
                self.__root.update()

                self.__is_loading = 1
                for episode in range(self.__db.last_episode + 1, lottery.Episode.get_next_episode()):
                    prog_value.set(100 * episode / lottery.Episode.get_last_episode())
                    numbers = lottery.Episode.request_lotto_number(episode)
                    self.__db.update(episode, numbers)

                    if episode == lottery.Episode.get_last_episode():
                        self.__lbl_load_info.config(text='로또 데이터를 모두 받았습니다.')
                    else:
                        self.__lbl_load_info.config(text='로또 {}회 정보를 받고 있습니다.'.format(episode))

                    self.__root.update()
                    if self.__abort: return False
                self.__dialog.destroy()
            self.__is_loading = 0
        return True

    def __remove_dialog(self):
        if self.__is_loading == 0:
            self.__root.destroy()
        else:
            self.__abort = 1
            self.__root.destroy()

    def __draw_dialog(self):
        prog_value = tkinter.IntVar()

        self.__dialog = tkinter.Toplevel(self.__root)
        self.__dialog.resizable(0, 0)
        self.__dialog.geometry('400x90')
        self.__dialog.attributes('-topmost', 'true')
        self.__dialog.title('Lottery DB')
        
        self.__dialog.grab_set()
        self.__dialog.transient(self.__root)
        self.__dialog.protocol('WM_DELETE_WINDOW', self.__remove_dialog)

        self.__lbl_load_info = tkinter.Label(self.__dialog, text='로또 DB 구성을 완료할 때까지 기다려주세요.')
        self.__progressbar   = tkinter.ttk.Progressbar(self.__dialog, maximum=100, variable=prog_value)

        self.__lbl_load_info.place(x=10, y=10)
        self.__progressbar.place(x=10, y=45, width=380)
        self.__root.update()

        lotto_list = {}
        self.__is_loading = 1
        for i in range(1, lottery.Episode.get_next_episode()):
            numbers = lottery.Episode.request_lotto_number(i)
            lotto_list[i] = numbers;
            prog_value.set(100 * i / lottery.Episode.get_last_episode())

            if i == lottery.Episode.get_last_episode():
                self.__lbl_load_info.config(text='로또 데이터를 모두 받았습니다.')
            elif i >= 10:
                self.__lbl_load_info.config(text='로또 {}회 정보를 받고 있습니다.'.format(i))

            self.__root.update()
            if self.__abort: return False
        self.__db.create(lotto_list)
        self.__is_loading = 0

        time.sleep(1)
        self.__is_loading = 0
        self.__dialog.destroy()
        return True

    def __init_widget(self):
        self.__lfm_draw_opt = tkinter.LabelFrame(self.__root, text='추첨번호 옵션')
        self.__lbl_range    = tkinter.Label(self.__lfm_draw_opt, text='지난 로또 비교 차수 범위')
        self.__spb_range    = tkinter.Spinbox(self.__lfm_draw_opt, textvariable=self.__str_range, from_=1, to=100, justify='right')
        self.__speparator1  = tkinter.ttk.Separator(self.__lfm_draw_opt, orient='horizontal')
        self.__chb_option1  = tkinter.Checkbutton(self.__lfm_draw_opt, variable=self.__chb_optval1, text='전체 차수 동안 4개 동일번호 포함 제외')
        self.__chb_option2  = tkinter.Checkbutton(self.__lfm_draw_opt, variable=self.__chb_optval2, text='{}주 동안 3개 동일번호 포함 제외'.format(self.__str_range.get()))
        self.__chb_option3  = tkinter.Checkbutton(self.__lfm_draw_opt, variable=self.__chb_optval3, text='{}주 동안 추점된 번호 우선'.format(self.__str_range.get()))
        self.__btn_generate = tkinter.Button(self.__lfm_draw_opt, text='생성')
        self.__speparator2  = tkinter.ttk.Separator(self.__lfm_draw_opt, orient='horizontal')

        self.__lfm_draw_nums = tkinter.LabelFrame(self.__root, text='생성번호')
        self.__lbx_draw_nums = tkinter.Listbox(self.__lfm_draw_nums, font='monospace 10')

        self.__lfm_lotterys = tkinter.LabelFrame(self.__root, text='지난 당첨번호')
        self.__lbl_episode  = tkinter.Label(self.__lfm_lotterys, text='당첨회차', anchor='w')
        self.__spb_episode  = tkinter.Spinbox(self.__lfm_lotterys, from_=1, to=lottery.Episode.get_next_episode(), justify='right')
        self.__btn_episode  = tkinter.Button(self.__lfm_lotterys, text='검색')
        self.__scl_episode  = tkinter.ttk.Scrollbar(self.__lfm_lotterys)
        self.__lbx_episode  = tkinter.Listbox(self.__lfm_lotterys, font='monospace 10', selectmode='single', yscrollcommand=self.__scl_episode.set)

    def __set_widget_config(self):
        self.__spb_range['validate'] = 'all'
        self.__spb_range['validatecommand'] = (self.__root.register(self.__is_valid_range), '%P')
        self.__spb_range['command'] = self.__refresh_label
        self.__btn_generate['command'] = self.__draw_number_generate

        self.__spb_episode['validate'] = 'all'
        self.__spb_episode['validatecommand'] = (self.__root.register(self.__is_valid_episode), '%P')

        self.__btn_episode['command'] = self.__search_episode
        self.__scl_episode['command'] = self.__lbx_episode.yview

    def __add_widget_to_window(self):
        self.__lfm_draw_opt.place(x=10, y=10, width=300, height=210)
        self.__lbl_range.place(x=10, y=10, width=150)
        self.__spb_range.place(x=170, y=8, width=60)
        self.__speparator1.place(x=5, y=40, width=285)
        self.__chb_option1.place(x=0, y=45)
        self.__chb_option2.place(x=0, y=75)
        self.__chb_option3.place(x=0, y=105)
        self.__speparator2.place(x=5, y=135, width=285)
        self.__btn_generate.place(x=230, y=145, width=50)

        self.__lfm_draw_nums.place(x=10, y=220, width=300, height=180)
        self.__lbx_draw_nums.place(x=10, y=10, width=275, height=135)

        self.__lfm_lotterys.place(x=320, y=10, width=270, height=390)
        self.__lbl_episode.place(x=10, y=10, width=60, height=30)
        self.__spb_episode.place(x=75, y=10, width=95, height=30)
        self.__btn_episode.place(x=180, y=10, width=75, height=30)
        self.__lbx_episode.place(x=10, y=50, width=235, height=305)
        self.__scl_episode.place(x=240, y=51, height=304)

    def __refresh_label(self):
        self.__chb_option2.config(text='{}주 동안 3개 동일번호 포함 제외'.format(self.__str_range.get()))
        self.__chb_option3.config(text='{}주 동안 추점된 번호 우선'.format(self.__str_range.get()))

    def __is_valid_range(self, value):
        if not value.isdigit():
            return False
        elif int(value) < 1 or 100 < int(value):
            return False
        return True

    def __is_valid_episode(self, value):
        if not value.isdigit():
            return False
        elif int(value) < 1 or lottery.Episode.get_next_episode() < int(value):
            return False
        return True

    def __search_episode(self):
        value = self.__db.last_episode - int(self.__spb_episode.get())

        self.__lbx_episode.selection_clear(0, tkinter.END)
        self.__lbx_episode.see(value)
        self.__lbx_episode.activate(value)
        self.__lbx_episode.selection_set(value)

    def __draw_number_generate(self):
        basic_set   = set(range(1, 46))
        number_set  = set()
        number_list = []
        base_episode = self.__db.last_episode - int(self.__spb_range.get()) +1

        self.__lbx_draw_nums.delete(0, tkinter.END)
        for i in range(base_episode, lottery.Episode.get_next_episode()):
            numbers = lottery.Episode.request_lotto_number(i)
            number_set = number_set.union(numbers)

        diff_set = basic_set - number_set
        no_draw_num = list(diff_set)
        no_draw_num.sort()

        number_list.append(no_draw_num)
        number_list.append([3, 5, 8, 22, 31, 43])

        count = 0;
        while count < 4:
            number = []
            while 1:
                n = random.randrange(1, 46)
                if n not in number: number.append(n)
                if len(number) == 6: break

            number.sort()
            if self.__chb_optval1.get() and self.__db.has_number_in_lottery(4, number): 
                continue

            if self.__chb_optval2.get() and  self.__db.has_number_in_lottery(3, number, base_episode):
                continue
            
            if self.__chb_optval3.get() and diff_set.intersection(number):
                continue

            number_list.append(number)
            count += 1

        for i, number in enumerate(number_list):
            if i == 0: number_string = '{:>3} : '.format('X')
            else:      number_string = '{:3d} : '.format(i)
            for k, n in enumerate(number):
                if k != (len(number) - 1):
                    number_string += '{:2d}'.format(n) + ', '
                else:
                    number_string += '{:2d}'.format(n)
            self.__lbx_draw_nums.insert(i, number_string)
            
    def run(self):
        self.__root.mainloop()
