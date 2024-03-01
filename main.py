import sys
import datetime
import aiohttp
import asyncio
import json
from pprint import pprint


async def do_request(session, url):
    print(f'Starting {url}')
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f'{resp.status} {url}')
                return data
            else:
                print(f"Error status: {resp.status} for {url}")
    except aiohttp.ClientConnectorError as err:
        print(f'Connection error: {url}', str(err))


async def data_parser(data:list[dict]) -> list[dict]:
    result_list = []
    for el in data:
        date = el["date"]
        temp_dict = {date: {}}
        rates = el["exchangeRate"]
        for rate in rates:
           if rate["currency"] == 'EUR':
               temp_dict[date]['EUR'] = {'sale': rate["saleRate"], 'purchase': rate["purchaseRate"]}
           elif rate["currency"] == 'USD':
               temp_dict[date]['USD'] = {'sale': rate["saleRate"], 'purchase': rate["purchaseRate"]}   
        result_list.append(temp_dict) 
    return result_list   


async def main():
    input_data = sys.argv
    base_url = 'https://api.privatbank.ua/p24api/exchange_rates?date='
    if len(input_data) < 2:
        return 'You should write counts of day as integer'
    if not input_data[1].isdigit():
       return 'You should write integer'
    if int(input_data[1]) <= 0 or int(input_data[1]) > 10:
       return 'You should write integer in range from 1 to 10' 
    count_days = int(input_data[1])
    current_day = datetime.datetime.now().date()
    dates = []
    for i in range(1, count_days+1):
        past_date = current_day - datetime.timedelta(days=i)
        str_past_date = past_date.strftime('%d.%m.%Y')
        dates.append(f'{base_url}{str_past_date}')
    async with aiohttp.ClientSession() as session:
        tasks = [do_request(session, url) for url in dates]
        result = await asyncio.gather(*tasks)
    output = await data_parser(result)  
    with open('exchangerate.json', 'w') as file:
        json.dump(output, file, indent=4, ensure_ascii=False) 
    return output
    
    
if __name__ == '__main__':
    pprint(asyncio.run(main()))
    


