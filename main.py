import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

MAX_CONCURRENT_DOWNLOADS = 10


async def download_txt(url, download_dir, semaphore):
  async with semaphore:
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as response:
        if response.status == 200:
          content = await response.read()
          filename = os.path.basename(url)
          txt_file_name = os.path.join(download_dir, filename)
          with open(txt_file_name, "wb") as file:
            file.write(content)
          print(f"下载文件 {txt_file_name}")


async def main():
  # 目标网页URL
  url = "https://h5book.pages.dev/"

  # 创建一个目录用于保存下载的txt文件
  download_dir = "files"
  if not os.path.exists(download_dir):
    os.makedirs(download_dir)

  # 发送GET请求获取网页内容
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      if response.status == 200:
        content = await response.text()

        # 使用BeautifulSoup解析网页内容
        soup = BeautifulSoup(content, "html.parser")

        # 定义一个正则表达式来匹配包含"thread"的文件名
        pattern = re.compile(r".txt")

        # 找到所有的<a>标签，提取链接并下载匹配正则表达式的txt文件
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)
        tasks = []
        for link in soup.find_all("a", href=pattern):
          href = link.get("href")
          txt_url = url + href
          tasks.append(download_txt(txt_url, download_dir, semaphore))

        await asyncio.gather(*tasks)

  print("下载完成")


if __name__ == "__main__":
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
