#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_TEMP_PATH = os.path.join(BASE_DIR, 'fund-code.txt')


async def query_data(session, fund_code, semaphore):
    """
    :param fund_code:
    :return:
    """
    async with semaphore:
        url = BASE_URL.format(fund_code)
        async with session.get(url=url) as response:
            if response.status == 200:
                bytes_data = await response.read()
                # 查看编码类型
                ret = chardet.detect(bytes_data)
                # bytes 转换成 str
                jsonp_data = str(bytes_data, ret['encoding'])
                # 判断是否有数据
                data = re.match('.*?({.*}).*', jsonp_data, re.S).group(1)
                return json.loads(data)
            else:
                return None


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


async def view_table(codes):
    # 设置最大并发数
    sem = asyncio.Semaphore(10)
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(query_data(session, code, sem)) for code in codes]
        data = await asyncio.gather(*tasks)
        data = filter(lambda fund: fund, data)
        print_table(data)


@click.group()
def fc():
    pass


def extract_fund_code(fund):
    """
    匹配出 fund code
    :param fund:
    :return:
    """
    # 以竖线 | 做分割时，要用转义符号 \
    return re.match('.*?\|(.*)$', fund, re.S).group(1)


@fc.command()
def run():
    try:
        with open(FILE_TEMP_PATH, 'r') as f:
            files_str = f.read().strip()
            codes = [extract_fund_code(fund) for fund in re.split('\n', files_str)]
            asyncio.run(view_table(codes))
    except FileNotFoundError as e:
        err_msg = f"请先执行 [bold red]fundgz add[/bold red] 命令添加文档"
        console.print(err_msg)


@fc.command()
def add():
    console.print('正在添加 fund 文档，[bold red]ctrl+c[/bold red] 退出')
    while True:
        # 文件是否存在
        fund_lines = []
        if os.path.exists(FILE_TEMP_PATH):
            # 读取临时文件
            with open(FILE_TEMP_PATH, 'r') as f:
                fund_lines = f.readlines()
        # 提示添加 fund code
        fund_code = click.prompt(text=click.style('请输入fund 编号', fg='yellow'), type=str)
        # 判断是否已经存在
        exist_fund = list(filter(lambda fund: fund_code in fund, fund_lines))
        if len(exist_fund):
            console.print(f'编号：[bold red]{fund_code}[/bold red] 已经存在，请重新输入编号')
        else:
            fund_name_alias_name = click.prompt(text=click.style('请输入fund 名称', fg='yellow'), type=str)
            console.print(f'名称：[bold blue]{fund_name_alias_name}[/bold blue]，编号：[bold red]{fund_code}[/bold red]')
            # 写入文件
            with open(FILE_TEMP_PATH, 'a') as f:
                f.write(f'{fund_name_alias_name}|{fund_code}\n')


@fc.command()
def ls():
    try:
        # 读取文件
        with open(FILE_TEMP_PATH, 'r') as f:
            files = f.read()
            console.print(files)
    except FileNotFoundError as e:
        err_msg = f"请先执行 [bold red]fundgz add[/bold red] 命令添加文档"
        console.print(err_msg)


@fc.command()
def delete():
    try:
        # 读取文件
        with open(FILE_TEMP_PATH, 'r') as f:
            files = f.read()
            codes = re.split('\n', files.strip())
            del_list = [
                inquirer.List('del',
                              message="请选择要删除的 fund：",
                              choices=codes)
            ]
            del_answers = inquirer.prompt(del_list)
            if del_answers is None:
                return console.print("退出删除！", style='bold red')
            del_code = del_answers.get('del', '')
            # 删除并重新写入文件
            print('删除的 code', del_code)
            codes.remove(del_code)
            with open(FILE_TEMP_PATH, 'w') as f:
                f.write("\n".join(codes))
    except FileNotFoundError as e:
        err_msg = f"请先执行 [bold red]fundgz add[/bold red] 命令添加文档"
        console.print(err_msg)


def main():
    fc()


if __name__ == '__main__':
    main()
