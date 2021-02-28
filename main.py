import re
import json
import chardet
import asyncio
import aiohttp
import aiofiles
import click
from rich.table import Table
from rich.console import Console

console = Console()

BASE_URL = "http://fundgz.1234567.com.cn/js/{}.js"


async def query_data(session, fund_code):
    """
    :param fund_code:
    :return:
    """
    url = BASE_URL.format(fund_code)
    async with session.get(url=url) as response:
        bytes_data = await response.read()
        # 查看编码类型
        ret = chardet.detect(bytes_data)
        # bytes 转换成 str
        jsonp_data = str(bytes_data, ret['encoding'])
        # 判断是否有数据
        data = re.match('.*?({.*}).*', jsonp_data, re.S).group(1)
        return json.loads(data)


async def main():
    async with aiohttp.ClientSession() as session:
        async with aiofiles.open('fund-code.txt', 'r') as fd:
            # async for fund_code in fd:
            #     fund_data = await query_data(session, fund_code.strip())
            #     print(fund_data)
            content = await fd.read()
            fund_codes = re.split('\n', content)
            tasks = [asyncio.create_task(query_data(session, fund_code)) for fund_code in fund_codes]
            data = await asyncio.gather(*tasks)
            fund_table = Table(show_header=True, header_style='bold magenta')
            fund_table.add_column('func_code')
            fund_table.add_column('title')
            fund_table.add_column('gszzl', justify="right")
            fund_table.add_column('gztime', justify="right")
            for fund_item in data:
                gz = fund_item['gszzl']
                color = 'green' if gz[0] == '-' else 'red'
                gz = f"[bold {color}]{gz}[/bold {color}]"
                value_tuple = (fund_item['fundcode'], fund_item['name'], gz, fund_item['gztime'])
                fund_table.add_row(*value_tuple)

            console.print(fund_table)


if __name__ == '__main__':
    asyncio.run(main())
