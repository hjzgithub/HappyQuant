# HappyQuant
## 项目描述
本项目旨在构建基于事件驱动框架的模拟回测系统、因子挖掘与测试框架、机器学习模型训练框架与实盘系统。

## 环境准备
1. 该项目支持python 3.10版本；
2. 激活虚拟环境（如有）；
3. 安装 requirements.txt 中的包：
   
   确保你的 requirements.txt 文件位于当前目录下，然后运行以下命令来安装所有列出的依赖：

   pip install -r requirements.txt

   注意：需要用pip下载而不是conda，否则会出现版本不兼容；

## 功能
### 已实现的功能
1. 多品种（独立账户）多策略（独立账户）的时序策略的多进程回测，只支持纯多头

### 计划中的功能
1. 多品种（独立账户）多策略（独立账户）的时序策略的多进程回测，支持多空
2. 股指数据，股指ETF数据，股指期货数据的获取与存储

## Quick Start
打开CMD后在根目录下

cd happyquant 

python test.py

使用 ./happyquant/sample_data 的示例数据

运行结果存放在 ./happyquant/sample_results 中

## 许可证
MIT