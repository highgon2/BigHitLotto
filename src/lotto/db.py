from abc import *

class DataBase(metaclass=ABCMeta):
    @abstractmethod
    def open(self, lottery):
        pass

    @abstractmethod
    def update(self, episode, numbers):
        pass

    @property
    @abstractmethod
    def last_episode(self):
        pass

class SqlDB(DataBase):
    __file_name = 'winning_numbers.db'
    
    def open(self, lottery):
        pass

    def update(self, episode, numbers):
        pass

class FileDB(DataBase):
    __file_name = 'winning_numbers.fdb'

    def __init__(self):
        self.__last_episode = 0
        self.__file = open(FileDB.__file_name, 'a+')

    def __del__(self):
        if self.__file: self.__file.close()

    def open(self, lottery):
        if self.__file.tell() == 0:
            return False

        self.__file.seek(0)
        for line in self.__file.readlines():
            try:
                str_epi, str_num = line.split(':')
                episode          = int(str_epi)
                numbers          = list(map(int, str_num.replace('\n', '').split(',')))
                lottery[episode] = numbers
                
                self.__last_episode = episode
            
            except ValueError:
                self.__file.truncate(0)
                for epi, num in lottery.items():
                    self.__file.writelines(str(epi) + ':' + ','.join([str(n) for n in num]) + '\n')
                break
        return True

    def update(self, episode, numbers):
        self.__file.writelines(str(episode) + ':' + ','.join([str(n) for n in numbers]) + '\n')
        self.__file.flush()
        self.__last_episode = episode

    @property
    def last_episode(self):
        return self.__last_episode

class Manager:
    def __init__(self, mode=0):
        self.__lottery = {}

        if mode == 0: self.__mgr = SqlDB()
        else:         self.__mgr = FileDB()

    def open(self):
        return self.__mgr.open(self.__lottery)

    def create(self, lottery):
        for episode, numbers in lottery.items():
            self.__mgr.update(episode, numbers)
            self.__lottery[episode] = numbers
        print('Lottery DB is created')

    def update(self, episode, numbers):
        if episode in self.__lottery.keys():
            raise ValueError('The episode already exist in DB')
        self.__mgr.update(episode, numbers)
        self.__lottery[episode] = numbers;

    @property
    def lottery_list(self):
        return self.__lottery

    @property
    def last_episode(self):
        return self.__mgr.last_episode

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
        if episode > self.__mgr.last_episode:
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
