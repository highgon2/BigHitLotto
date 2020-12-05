import datetime
import requests

class Episode:
    '''
    Lotto was started at 2002-12-01 Sunday.
    1st draw date of Lotto is at 2002-12-07 Saturday.
    '''
    __start_date    = '2002-12-01'
    __lotto_api_url = 'https://dhlottery.co.kr/common.do'

    __last_episode = -1
    __next_episode = -1

    @classmethod
    def __caculate_episode(cls):
        if cls.__last_episode > 0 and cls.__next_episode > 0:
            return

        today      = datetime.date.today()
        start_date = datetime.date.fromisoformat(cls.__start_date)
        date_delta = today - start_date

        cls.__last_episode = date_delta.days // 7
        cls.__next_episode = cls.__last_episode + 1

    @classmethod
    def request_lotto_number(cls, episode):
        res = None
        numbers = []
        params = {
            'method': 'getLottoNumber',
            'drwNo': episode
        }

        cls.__caculate_episode()
        if episode <= 0 or cls.__next_episode <= episode:
            raise ValueError('The episode is inavlid.\nThe episode is range 1 ~ {}'.format(cls.__last_episode))

        try:
            res = requests.get(cls.__lotto_api_url, params = params)
            if res.status_code != 200:
                raise ValueError('Request status code is {}'.format(res.status_code))
            for key, value in res.json().items():
                if 'drwtNo' in key:
                    numbers.append(value)
            numbers.append(res.json().get('bnusNo'))
        
        except Exception as e:
            print(e)
        
        return numbers

    @classmethod
    def get_last_episode(cls):
        cls.__caculate_episode()
        return cls.__last_episode

    @classmethod
    def get_next_episode(cls):
        cls.__caculate_episode()
        return cls.__next_episode

if __name__ == '__main__':
    print('last episode :', Episode.get_last_episode(), 'next episode :', Episode.get_next_episode())
    for episode in range(1, Episode.get_next_episode()):
        numbers = Episode.request_lotto_number(episode)
        print(episode, numbers)