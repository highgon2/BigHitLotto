import os

class Manager:
    '''
    Lotto DB will use sqlite.
    Currently, I use file system because I don't know sqlite
    '''

    __db_file = 'winning_numbers.db'

    def __init__(self):
        self.__mode    = 0
        self.__lottery = {}
        self.__last_episode = 0

    def __open_file_db(self):
        with open(Manager.__db_file, 'r') as f:
            is_read_error = 0
            line = f.readline()
            while line != '':
                try:
                    str_episode, str_numbers = line.split(':')
                    episode                  = int(str_episode)
                    numbers                  = list(map(int, str_numbers.replace('\n', '').split(',')))

                    self.__last_episode      = episode;
                    self.__lottery[episode]  = numbers
                    line = f.readline()

                except ValueError:
                    print('invaild record...')
                    is_read_error = 1
                    break

        if is_read_error:
            with open(Manager.__db_file, 'w') as f:
                for episode, numbers in self.__lottery.items():    
                    f.writelines(str(episode) + ':' + ','.join([str(n) for n in numbers]) + '\n')

    def __create_file_db(self, lottery):
        with open(Manager.__db_file, 'w') as f:
            for episode, numbers in lottery.items():
                self.__last_episode = episode
                self.__lottery[episode] = numbers
                f.writelines(str(episode) + ':' + ','.join([str(n) for n in numbers]) + '\n')
            print('Lottery DB is created')

    def __update_file_db(self, episode, numbers):
        self.__lottery[episode] = numbers
        with open(Manager.__db_file, 'a') as f:
            f.writelines(str(episode) + ':' + ','.join([str(n) for n in numbers]) + '\n')
            self.__last_episode = episode
        # print('{} episode updated in DB'.format(episode))

    def create(self, lottery, mode=0):
        self.__mode = mode
        if mode == 0: self.__create_db(lottery)
        else:         self.__create_file_db(lottery)

    def open(self, mode=0):
        self.__mode = mode
        if mode == 0: self.__open_db()
        else:         self.__open_file_db()

    def update(self, episode, numbers):
        if episode in self.__lottery.keys():
            raise ValueError('The round already exist in DB')
        
        if self.__mode == 0: self.__update_db(episode, numbers)
        else:                self.__update_file_db(episode, numbers)

    @property
    def last_episode(self):
        return self.__last_episode
    
    @property
    def lottery_list(self):
        return self.__lottery

    def has_number_in_lottery(self, same_count, candidate_num, base_episode=0):
        for episode, lottery in self.__lottery.items():
            if episode < base_episode: continue

            inter_set = set(candidate_num) & set(lottery)
            if len(inter_set) >= same_count:
                print('\tepisode = {:4d}, same_draw_numbers = {}'.format(episode, inter_set))
                return True
        return False

    def get_lottery_episode_string(self, episode):
        episode_string = ''
        if episode > self.__last_episode:
            return ''

        episode_string = '{:5d} : '.format(episode)
        for i, num in enumerate(self.__lottery[episode]):
            if i != (len(self.__lottery[episode]) - 1):
                episode_string += '{:2d}'.format(num) + ', '
            else:
                episode_string += '{:2d}'.format(num)
        
        return episode_string

    def print_lotto_numbers(self):
        for episode, numbers in self.__lottery.items():
            print('episode = {:4d}, numbers = '.format(episode), end='[')
            for num in numbers:
                print('{:2d}'.format(num), end=', ')
            print('\b\b]')
