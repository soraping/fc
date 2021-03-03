### `fundgz` 命令行工具

一朋友在上班期间看手机基金信息，但上班期间频繁看手机着实不太好，于是就想到写一个能在命令行查看 `fund` 估值的命令行工具，通过输入 `fund` 编号和名称，就能查询到当前时间的估值。
网络上有很多这样的摸鱼插件，甚至在 `vscode` 里的插件比比皆是。
本着练手的态度，自己也写了一个简单的工具，就当做学习新的库了。

#### 使用预览

安装工具：

```bash
pip install fundgz
```

使用：

```bash
> fundgz

Usage: fundgz [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add
  delete
  run
```

命令行输入 `fundgz` 命令，可以查看这个命令的简介，可以看到提供了三个子命令:

```bash
> fundgz add

正在添加 fund 文档，ctrl+d 退出
请输入fund 编号: 078943
请输入fund 名称: test
```
输入 `fundgz add` 命令，终端会提示输入 `fund` 编号和名称，输入完成后，可以按 `ctrl+d` 退出。

`fundgz delete` 命令删除录入文档的编号

`fundgz run` 命令就是根据之前存入的文档执行查询了:

在终端会展示结果表格

![fund.png](https://i.loli.net/2021/03/02/ugsawYykWeALOo9.png)


#### 开发思路

- 在终端录入 `fund code` 并保存至临时文件中
- 查询临时文件，提取其中的 `fund code` 列表
- 通过 `code` 列表，批量查询 `fund` 当日的估值信息
- 在终端列表展示

#### 技术栈

`python3.7` 版本

数据抓取 - `asyncio` + `aiohttp`

命令行工具 - `click` + `inquirer`

终端展示 - `rich`

打包发布 - `setuptools`

#### `click` + `inquirer` 终端工具

使用 `click.group()` 创建命令组，实现 `add`, `delete` 和 `run` 命令

```python
@click.group()
def fc():
    pass

@fc.command()
def run():
    pass

@fc.command()
def add():
    pass
    
@fc.command()
def delete():
    pass
    
fc()
```

`@fc.command()` 是为了替代 `fc.add_command(run)` ，这样写更加优雅

```python
@click.command()
def run():
    pass

fc.add_command(run)
```

`inquirer` 库是交互式工具，提供了很多便利的操作，这次使用的是 `list` 选择。

执行 `fundgz delete` 选择要删除的 `code`：

![fund-del.png](https://i.loli.net/2021/03/03/kFdyTUYJAv35pVX.png)

```python
del_list = [
                inquirer.List('del',
                              message="请选择要删除的 fund：",
                              choices=codes)
            ]
            del_answers = inquirer.prompt(del_list)
```

#### `asyncio` + `aiohttp` 批量数据查询

读取临时文件后，提取出正在需要的 `code` 列表，通过这个列表批量查询数据

```python
async with aiohttp.ClientSession() as session:
    tasks = [asyncio.create_task(query_data(session, code)) for code in codes]
    data = await asyncio.gather(*tasks)
    print(data)
```

如果没有查询到数据，则需要做好异常处理，则请求非 `200` 的则直接返回 `None`:

```python
async def query_data(session, fund_code):
    """
    :param fund_code:
    :return:
    """
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
```

如此，批量返回的数据中就会有 `None`，所以要 `filter`

```python
data = filter(lambda fund: fund, data)
```

#### `setuptools` 打包

命令行工具已经可以了，使用

```bash
python fundgz/main.py run
```

但是期望的是

```bash
fundgz run
```

所以，就要将这个工具发布到服务上。

首先在 `https://pypi.org/` 上注册一个账号，认证邮箱等

其次，安装 `setuptools`，更新至最新版：

```bash
python -m pip install --upgrade pip setuptools wheel
```
具体可以查看官网 `https://pypi.org/project/setuptools/`

接下来就是打包的事儿了。

在项目根目录下新建两个文件 `setup.py` 和 `setup.cfg`

此时项目的结构是

```bash
├── README.md
├── fund-code.txt
├── fundgz
│   ├── __init__.py
│   └── main.py
├── setup.cfg
└── setup.py
```

在 `setup.py` 文件内，填写打包的必要信息:

```python
#!usr/bin/env python
# -*- coding:utf-8 _*-

from setuptools import setup, find_packages

VERSION = '0.1.7'

setup(
    name='fundgz',
    version=VERSION,
    description='fund search',
    long_description='fund search',
    keywords='fund asynico click rich inquirer',
    author='caoshiping',
    author_email='soraping@163.com',
    url='https://github.com/soraping/fc',
    license='MIT',
    packages=find_packages(exclude=["*.txt"]),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'aiohttp',
        'inquirer',
        'click',
        'rich'
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'fundgz = fundgz.main:main'
        ]
    }
)
```

> 关键字段详解：

- `name`

上传包的名称

- `version`

开发库版本

- `packages`

打包的内容目录，使用 `find_packages` 方法，使用参数 `exclude` 屏蔽一些文件

- `install_requires`

所依赖的库列表

- `entry_points`

自定义命令，不用 `python xxxx.py` 这样执行的，就要配置这个字段。这个字段不仅仅这个功能，当前包通过 `setuptools` 注册的一个外部可以直接调用的接口。

```bash
    entry_points={
        'console_scripts': [
            'fundgz = fundgz.main:main'
        ]
    }
```

在终端输入：

```bash
$ fundgz --help
usage: fundgz...
```

`console_scripts` 是自定义命令行列表

`fundgz = fundgz.main:main`，`fundgz` 是命令名称，等号右边的是主方法路径，其中 `fundgz.main` 包根目录下执行文件的路径，最后是执行文件的方法名

`setup.py` 文件配置完成后就可以执行打包操作了

1. 在终端执行命令：

```bash
# 使用sdist构建源码分发包
python setup.py sdist bdist_wheel
```

这里是固定的命令，且在 `setup.py` 文件相同的目录下执行，当这个命令运行结束后，确保在生成的 `dist/` 文件夹下存在相应的 `.whl` 文件和 `.tar.gz` 文件。其中 `.tar.gz` 文件是我们 `的python package` 的源文件文档。

而 `.whl` 是一个软件分发包 `(build distribution)` 。新版本的 `pip` 将会首先尝试安装软件分发包，但在失败情况下会接着尝试采用源文件包安装。

执行打包后，打开 `dist` 文件夹，可以发现有 `setup.py` 配置的 `name` 和 `version` 拼接的包文件，这些就是待上传的包

2. 上传包

需要安装上传工具 `twine`

```bash
pip install --user --upgrade twine

# 上传
twine upload dist/*
```

上传的时候，会提示输入 `pypi` 账号密码。

也可以指定版本号上传

```bash
twine upload dist/fundgz-0.1.7*
```

到此，一个包就算上传成功了，可以下载下来试下

```bash
> pip install fundgz

> fundgz --help
```

#### 参考文章

- click

https://blog.csdn.net/weixin_38278993/article/details/100052961

https://www.cnblogs.com/alexkn/p/6980400.html

- setuptools

https://www.cnblogs.com/Zzbj/p/11535625.html

https://blog.csdn.net/u011519550/article/details/105253075/

https://blog.csdn.net/yinshuilan/article/details/93469900

https://www.jb51.net/article/178728.htm

https://www.jianshu.com/p/eb27d5cb5e1d