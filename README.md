# wbu_power_message_push
武汉商学院电费查询

---

## 简介

也没啥好说的，就是突发奇想爬了下交电费的网页，不得不说这个系统做的就是（史），企业微信缴费还得复制到微信上调用微信的支付Api，一堆新生电费都不知道怎么交！，而且没电费了也没啥提醒，每次没电费了就突然断电，更（史）了 !!!
PS：目前版本只支持北区查询，具体原因看下面原理

Update：2023/12/1


[Docker镜像](https://hub.docker.com/repository/docker/fushin/wbupowerapi) 


[Github链接](https://github.com/Xingsandesu/wbu_power_message_push) 

## 原理

### Step 1 

#### 分析链接传参

![image.png](https://cdn.jsdelivr.net/gh/Xingsandesu/kookoo-picbed/img/2023%2F11%2F28%2F20231128185836_18-58-37.png)

```
http://yktyd.wbu.edu.cn/wechat/elecpay/queryelec.html
?
json=PsawsniNuAsphjoIwdJTVW%252BKBRQ1A4RVpp1BYcPWhTgZg%252BDxDkRlnEvwxDJQk81qzvX6JH7LRf6Q%250D%250AXBtpgI2dRCJlQZgGkpSXM8mcggc4PpX9FzSFCYa%252BeuZ3dkJDAhKRufQQem3czCkpHxdk9EsWJMq9%250D%250AqqJ0nflhNtCCvYSWcSk%253D%250D%250A
&
token=wWC46I31LgDeBN%252B%252B5gSh%252FA%253D%253D%250D%250A
&
xxbh=synjones
&
jkbh=0014
```

可以看到充电费的页面传递了四个参数，其他三个都一样，最重要的是token，用于OAuth身份验证，经过测试。这个token时效是有限的，并且该页面在token有效期内是可以通过其他UA进行访问的。token过期则意味着之后打开构造的链接就会显示从`微信客户端打开页面`的提示，并且进行伪造微信UA，进入页面也会发现页面不传递任何信息。所以我们不能依赖于token来构建这个链接进行自动化爬虫工作。但是经过抓包有有了新地发现。

### Step 2

#### 填写表单分析HTTP请求

![image.png](https://cdn.jsdelivr.net/gh/Xingsandesu/kookoo-picbed/img/2023%2F11%2F28%2F20231128190626_19-06-27.png)
![image.png](https://cdn.jsdelivr.net/gh/Xingsandesu/kookoo-picbed/img/2023%2F11%2F28%2F20231128191139_19-11-40.png)
填写表单后，浏览器抓包发现响应了一个Http请求，那么，我们是不是可以直接构建一个链接去请求这个api呢？答案是可以的，并且可以不经过token的验证，那么事情就好办了。我们直接构建如下链接访问。

```
https://yktyd.wbu.edu.cn/wechat/basicQuery/queryElecRoomInfo.html?aid=0030000000001401&area=%7B%22area%22%3A%22%22%2C%22areaname%22%3A%22%22%7D&building=%7B%22building%22%3A%22%E8%A7%82%E6%B9%96%E8%8B%915%E6%A0%8B%22%2C%22buildingid%22%3A%2240%22%7D&floor=%7B%22floorid%22%3A%22%22%2C%22floor%22%3A%22%22%7D&room=%7B%22room%22%3A%22%22%2C%22roomid%22%3A%22520%22%7D
```
![image.png](https://cdn.jsdelivr.net/gh/Xingsandesu/kookoo-picbed/img/2023%2F11%2F28%2F20231128191553_19-15-54.png)
发现可以直接返回一部字典，那么事情就简单了，只需要构建一个requests请求就可以轻松查询到余额了。

### Step 3

#### 构建requests请求

首先我们先用encodeURIComponent解密这个url，如下


```
http://yktyd.wbu.edu.cn/wechat/basicQuery/queryElecRoomInfo.html
?
aid=0030000000001401
&
area={"area":"","areaname":""}
&
building={"building":"观湖苑5栋","buildingid":"40"}
&
floor={"floorid":"","floor":""}
&
room={"room":"","roomid":"520"}
```

其中有几个重要的参数，北区查询时，只需要替换这两个参数就可以查询到字典，其他参数就算不一致也可以忽视。比如`buildingid`

```
"building":"观湖苑5栋"
"roomid":"520"
```

那么我们就构建GET请求过去就好了，但是事情没这么简单，经过测试，只有北区才能只使用这两个参数去构建GET请求，并且成功获得字典，南区需要重新构建`aid`，`buildingid`，`floorid`，`floor`，`room`，`roomid`这些参数，参数过于繁杂，而且命名不规范，而且本人也不在南区，所以南区的适配计划暂时搁置，如果有人意愿适配南区的话，只需要跟着原理构建相对地请求即可适配。

经过构造的URL，我们直接去请求发现无法查询，显示`会话已超时，请尝试重新访问业务应用`，其实这个api认证的方式是一个cookies，构造这个请求还需要手动提取出一份可用的cookies，我们可以通过浏览器抓取。如下图
![image.png](https://cdn.jsdelivr.net/gh/Xingsandesu/kookoo-picbed/img/2023%2F11%2F28%2F20231128193237_19-32-38.png)

![image.png](https://cdn.jsdelivr.net/gh/Xingsandesu/kookoo-picbed/img/2023%2F11%2F28%2F20231128192136_19-21-38.png)

#### Cookies具体抓取方法
1. 进入企业微信打开校园一卡通界面
![image.png](https://cdn.jsdelivr.net/gh/Xingsandesu/kookoo-picbed/img/2023%2F11%2F28%2F20231128193622_19-36-23.png)

2. 打开缴电费页面
3. 点击左上角三个点，选择复制链接
4. 把链接复制到电脑上，使用Chrome打开
5. 打开后按F12进入开发者模式，选择应用-存储-Cookie-http://yktyd.wbu.edu.cn就可以看到对应的Cookies
6. 获取到`JSESSIONID`的值填入`config.yaml`对应位置即可
![image.png](https://cdn.jsdelivr.net/gh/Xingsandesu/kookoo-picbed/img/2023%2F11%2F28%2F20231128194143_19-41-45.png)


## 功能列表

| 功能       | 描述                         |
|----------|----------------------------|
| 查电费      | 构建GET请求查询API               |
| 电费记录     | 使用.power.yaml记录每次查询的电费并且对比 |
| 企业微信推送   | 电费信息通过企业微信推送               |
| 断电提醒     | 每次电费快用完时会提醒用户              |
| 自动抓包     | 自动抓取cookies                |
| adb自动运行  | 自动运行企业微信进行抓包               |
| docker部署 | 提供打包了运行环境的镜像               |

## 快速开始-自动
- 你需要事先安装`Docker`
- 你需要一台没有密码的安卓手机, 安装好企业微信并且登录，开启开发者选项-USB调试
- 本次使用的系统为Debian Arm64
- 运行在Docker环境中
- 注意，请确保 `8080` 端口没有被使用
---
  
1. 在手机上打开`开发者选项-USB调试`，`指针位置`
2. 手动打开一次企业微信，记录企业微信主页面的`工作台`的`x，y坐标`，然后点击工作台，记录工作台页面的`校园一卡通`的`x，y坐标`
3. 记录运行的ip地址
4. 创建文件夹，保存程序运行的logs与配置

```
mkdir power && cd power
```

5. 创建配置文件，并且填写相关配置

```
touch config.yaml && touch .power.yaml
```

```
vim config.yaml
```

``` config.yaml
WBUPower:  
  Corp_id: 企业微信 Corp_id  
  Corp_secret: 企业微信 Corp_secret  
  Agentid: 企业微信 Agentid  
  Building: 观湖苑X栋  
  Roomid: 房间号,例如222  
  adbinputone: adb shell input tap 工作台x轴坐标 工作台y轴坐标 
  adbinputtwo: adb shell input tap 校园一卡通x轴坐标 校园一卡通y轴坐标  
  hostip: 填运行脚本主机的ip，请确保主机与手机可以通讯  
  Cookies:  
    JSESSIONID: 这里不用填，留空自动获取
```
6. 连接手机在电脑或者其他设备上，运行Docker镜像(支持AMD64, ARM64)

```
docker run -itd \  
    --privileged \  
    --network bridge \  
    --rm \  
    --name power \  
    -p 8080:8080 \  
    -v "$(pwd)"/config.yaml:/app/config.yaml \  
    -v "$(pwd)"/.power.yaml:/app/.power.yaml \  
    -v "$(pwd)"/adb_logs:/app/adb_logs \  
    -v "$(pwd)"/main_logs:/app/main_logs \  
    -v "$(pwd)"/proxy_logs:/app/proxy_logs \  
    -v "$(pwd)"/keys:/root/.android \  
    fushin/wbupowerapi
```

7. 挂载自动任务，`快速开始-手动`一致，命令替换成`sh run.sh`，使用`run.sh`之前首先先编辑脚本设置启动位置

## 快速开始-手动

你需要事先安装`python3.10`
本文使用的系统为Debian，Windows系统请使用计划任务运行即可

1. 下载源码并解压（假设当前路径为/root）

```
mkdir wbupower & cd wbupower
```

```
wget https://github.com/Xingsandesu/wbu_power_message_push/archive/refs/tags/1.0.zip
```

```
unzip main.zip
```

```
cd wbu_power_message_push-main
```

2. 安装依赖

```
pip install -r requirements.txt
```

3. 第一次运行生成config.yaml并配置

```
python main.py
```

4. 修改config.yaml

```
vim config.yaml
```

5. 试运行一次，确保配置可以运行

```
python main.py
```

6. 挂载自动任务(每天早上八点自动运行)

```
crontab -e
```


```
0 8 * * * python /root/wbupower/wbu_power_message_push-main/main.py
```

7. 完成

## 效果展示

![image.png](https://cdn.jsdelivr.net/gh/Xingsandesu/kookoo-picbed/img/2023%2F11%2F28%2F20231128200132_20-01-33.png)

![image.png](https://cdn.jsdelivr.net/gh/Xingsandesu/kookoo-picbed/img/2023%2F11%2F28%2F20231128201653_20-16-55.png)

## 二次开发

欢迎各位

## 相关依赖

```
见 requirements.txt
```

## 遇到问题

- 提交/logs的日志发送邮件到 fushinn888@gmail.com
- 提交issues，但是不要提交任何日志在上面，因为日志包含敏感信息!!!

---
<p align="right">By KooKoo</p>
<p align="right">Date :  2023 / 11 / 30
</p>
