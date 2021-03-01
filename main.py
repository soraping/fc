import os
import re
import json
import chardet
import asyncio
import aiohttp
import inquirer
import click
from rich.table import Table
from rich.console import Console

console = Console()

BASE_URL = "http://fundgz.1234567.com.cn/js/{}.js"

# 临时文件路径
BASE_DIR = os.getcwd()
FILE_TEMP_PATH = f'{BASE_DIR}/fund-code.txt'


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


def print_table(data):
    """
    打印至终端
    :param data:
    :return:
    """
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


async def main(codes):
    async with aiohttp.ClientSession() as session:
        # async with aiofiles.open('fund-code.txt', 'r') as fd:
        #     # async for fund_code in fd:
        #     #     fund_data = await query_data(session, fund_code.strip())
        #     #     print(fund_data)
        #     content = await fd.read()
        #     fund_codes = re.split('\n', content)
        tasks = [asyncio.create_task(query_data(session, code)) for code in codes]
        data = await asyncio.gather(*tasks)
        print_table(data)


@click.group()
def fc():
    # asyncio.run(main())
    print('hello')


def extract_fund_code(fund):
    """
    匹配出 fund code
    :param fund:
    :return:
    """
    # 以竖线 | 做分割时，要用转义符号 \
    return re.match('.*?\|(.*)$', fund, re.S).group(1)


@click.command()
def run():
    try:
        with open(FILE_TEMP_PATH, 'r') as f:
            files_str = f.read().strip()
            codes = [extract_fund_code(fund) for fund in re.split('\n', files_str)]
            asyncio.run(main(codes))
    except FileNotFoundError as e:
        err_msg = f"请先执行 [bold red]fc add[/bold red] 命令添加文档"
        console.print(err_msg)


@click.command()
def add():
    console.print('正在添加 fund 文档，[bold red]ctrl+d[/bold red] 退出')
    while True:
        # 提示添加 fund code
        fund_code = click.prompt(text=click.style('请输入fund 编号', fg='yellow'), type=str)
        fund_name_alias_name = click.prompt(text=click.style('请输入fund 名称', fg='yellow'), type=str)
        console.print(f'名称：[bold blue]{fund_name_alias_name}[/bold blue]，编号：[bold red]{fund_code}[/bold red]')
        # 写入文件
        with open(FILE_TEMP_PATH, 'a') as f:
            f.write(f'{fund_name_alias_name}|{fund_code}\n')


@click.command()
def delete():
    # 读取文件
    with open(FILE_TEMP_PATH, 'r') as f:
        files = f.read()
        codes = re.split('\n', files)
        del_list = [
            inquirer.List('del',
                          message="请选择要删除的 fund：",
                          choices=codes)
        ]
        del_answers = inquirer.prompt(del_list)
        del_code = del_answers.get('del', '')

    # 删除并重新写入文件
    print('删除的 code', del_code)
    codes.remove(del_code)
    with open(FILE_TEMP_PATH, 'w') as f:
        f.write("\n".join(codes))


fc.add_command(add)
fc.add_command(delete)
fc.add_command(run)

if __name__ == '__main__':
    fc()
