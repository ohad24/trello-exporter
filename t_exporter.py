import requests, os
from prometheus_client import start_http_server
from prometheus_client.core import CounterMetricFamily, REGISTRY
import time

key = os.getenv('TRELLO_API_KEY')
token = os.getenv('TRELLO_API_TOKEN')
board = os.getenv('TRELLO_BOARD_ID')

def get_trello_lists_count(board, key, token):
    url = "https://api.trello.com/1/boards/{}".format(board)
    querystring = dict(actions="all", boardStars="none", cards="all", card_pluginData="false", checklists="none",
                       customFields="false",
                       fields="name,desc,descData,closed,idOrganization,pinned,url,shortUrl,prefs,labelNames", lists="all",
                       members="none", memberships="none", membersInvited="none", membersInvited_fields="all",
                       pluginData="false", organization="false", organization_pluginData="false", myPrefs="false",
                       tags="false", key=key,
                       token=token)
    response = requests.request("GET", url, params=querystring)
    if response.status_code == 200:
        d = response.json()
        cards = d['cards']
        list_ids = tuple(set(x['idList'] for x in cards))
        metric_counts = {}
        for list_id in list_ids:
            url = "https://api.trello.com/1/lists/{}".format(list_id)
            querystring = dict(fields="name,closed,idBoard,pos",
                               key=key,
                               token=token)
            response = requests.request("GET", url, params=querystring)
            d = response.json()
            metric_counts[d['id']] = dict(name=d['name'], count=0)

        for card in cards:
            metric_counts[card['idList']]['count'] += 1
        return metric_counts
    else:
        print('Error {}: {}'.format(response.status_code, response.content.decode()))
        return {}


class TrelloCollector(object):
    @staticmethod
    def collect():
        c = CounterMetricFamily('trello_lists_counter', 'Count the cards within a trello lists', labels=['ListName'])
        metrics = get_trello_lists_count(board, key, token)
        for k, metric in metrics.items():
            c.add_metric([str(metric['name'])], metric['count'])
        yield c


if __name__ == '__main__':
    REGISTRY.register(TrelloCollector())
    start_http_server(9999)
    while True:
        time.sleep(1)
