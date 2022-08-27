# IMBroker —— 基于FaaS的跨平台群消息工具
- 原文链接： [https://github.com/taikeguluer/imbroker/blob/master/README.md](https://github.com/taikeguluer/imbroker/blob/master/README.md)
## 1. 背景
`IMBroker`是用于在飞书、企业微信、钉钉、微信及其他企业内部即时通讯工具之间的消息传递。它基于FaaS平台Knative实现，将消息的收和发设计为函数实现，使用FaaS的事件驱动机制进行解耦和通讯，实现对底层资源使用的最大弹性。当前代码仅为概念验证使用，无数据存储机制。
## 2. 技术架构
![techarch4imbroker](https://github.com/taikeguluer/imbroker/raw/master/pic4readme/techarch4imbroker.png)
## 3. 快速开始
当前部署仅能用于实践FaaS事件驱动，并且只实现了将发到飞书群里的消息转发到企业微信群，至少需要完成文末第1条Issue方可生产使用。
### 3.1 准备工作
#### 3.1.1 创建飞书企业自建应用
- 在 [飞书开发者后台](https://open.feishu.cn/app) 中创建`企业自建应用`
- 在应用配置页面的`事件订阅`中，配置`Encrypt Key`
- 在应用配置页面的`权限管理`中，获取如下权限：
  - 接收群聊中@机器人消息事件（免审权限）
  - 读取用户发给机器人的单聊消息（免审权限）
#### 3.1.2 安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)和[ngrok](https://ngrok.com/)
#### 3.1.3 在windows上使用kind安装k8s和knative
成功安装knative的前提是必须有能下载镜像的代理服务器，否则就去找个现成的Knative吧
- 将[k8s和Knative命令行工具](https://pan.baidu.com/s/1-L961uJBp8fuW6upjMBZOg?pwd=0jxb)下载至`C:\ktools`
- 将`C:\ktools`添加至OS的系统环境变量`Path`的最前面
- 创建kind的k8s集群配置文件`config.yaml`如下：
```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 31180
    listenAddress: "0.0.0.0"
  - containerPort: 30100
    hostPort: 41100
    listenAddress: "0.0.0.0"
```
- 用kind创建名字为knative的k8s集群
```commandline
kind create cluster --name knative --config .\config.yaml
```
- 获取kind在docker desktop中创建的容器ID，整个k8s集群都运行在这个容器里
```commandline
docker ps
```
- 登录到该容器的命令行
```commandline
docker exec -it your-container-id bash
```
- 设置能下载Knative镜像的代理
```shell
echo [Service] > http_proxy.conf.www
echo Environment="HTTP_PROXY=http://192.168.8.26:8080" "HTTPS_PROXY=http://192.168.8.26:8080" "NO_PROXY=localhost,127.0.0.1,10.96.0.0/12,192.168.0.0/16,.svc,203.93.118.0/24,203.93.119.0/24,172.17.0.0/16,172.18.0.0/16,10.0.0.0/8,171.18.0.0/16,.cicc.group,.jw.cicc.com.cn,.ciccs.com.cn,.cicconline.com,.ciccwm.com,.cicccloud.com,.cicc.io,.dipper.cicc.com.cn,.cicc.com.cn,crm.china-invs.cn,oa.china-invs.cn,ri.china-invs.cn,corporatebank.cib.com.cn,172.28.176.0/20">>http_proxy.conf.www 
mkdir /etc/systemd/system/containerd.service.d
cp http_proxy.conf.www /etc/systemd/system/containerd.service.d/http_proxy.conf
systemctl daemon-reload
systemctl restart containerd 
```
- 下载Knative镜像
```shell
crictl pull gcr.io/knative-releases/knative.dev/eventing/cmd/broker/filter@sha256:32d368bcbabee58fad2dd84c39c1d84b6dc5b608cc599d1387add40bae41b000
crictl pull gcr.io/knative-releases/knative.dev/eventing/cmd/broker/ingress@sha256:924bbc1944abb6ab91a8c3d7d6dfbb27f1e55b56ec456b9efc88e4f7320bae2f
crictl pull gcr.io/knative-releases/knative.dev/eventing/cmd/controller@sha256:204fdaa828603a03b66ee30141ebf88c98881829d6af5f57c34400408d15ec91
crictl pull gcr.io/knative-releases/knative.dev/eventing/cmd/in_memory/channel_controller@sha256:97d7db62ea35f7f9199787722c352091987e8816d549c3193ee5683424fef8d0
crictl pull gcr.io/knative-releases/knative.dev/eventing/cmd/in_memory/channel_dispatcher@sha256:3163f0a3b3ba5b81c36357df3dd2bff834056f2943c5b395adb497fb97476d20
crictl pull gcr.io/knative-releases/knative.dev/eventing/cmd/mtchannel_broker@sha256:915d73c4d00990d5db5aa1e26b54b128df025cea7b688b95af8f14e1570fb4d4
crictl pull gcr.io/knative-releases/knative.dev/eventing/cmd/webhook@sha256:65e83bd39a909fc6ce171750281660e3df2becd6c7b550b5d902d335f3379ae7
crictl pull gcr.io/knative-releases/knative.dev/net-kourier/cmd/kourier@sha256:197fbb71d1f115673a62843dd8d23a751a72d81d66e2fe8aa9d8d91452521d22
crictl pull gcr.io/knative-releases/knative.dev/serving/cmd/activator@sha256:08315309da4b219ec74bb2017f569a98a7cfecee5e1285b03dfddc2410feb7d7
crictl pull gcr.io/knative-releases/knative.dev/serving/cmd/autoscaler@sha256:105bdd14ecaabad79d9bbcb8359bf2c317bd72382f80a7c4a335adfea53844f2
crictl pull gcr.io/knative-releases/knative.dev/serving/cmd/controller@sha256:bac158dfb0c73d13ed42266ba287f1a86192c0ba581e23fbe012d30a1c34837c
crictl pull gcr.io/knative-releases/knative.dev/serving/cmd/domain-mapping-webhook@sha256:15f1ce7f35b4765cc3b1c073423ab8d8bf2c8c2630eea3995c610f520fb68ca0
crictl pull gcr.io/knative-releases/knative.dev/serving/cmd/domain-mapping@sha256:e384a295069b9e10e509fc3986cce4fe7be4ff5c73413d1c2234a813b1f4f99b
crictl pull gcr.io/knative-releases/knative.dev/serving/cmd/queue@sha256:813ea20d55b5063596cf967d1c63f51b9e34f883653957157b9b5341dfad0001
crictl pull gcr.io/knative-releases/knative.dev/serving/cmd/webhook@sha256:1282a399cbb94f3b9de4f199239b39e795b87108efe7d8ba0380147160a97abb
```
- 移除代理
```shell
rm /etc/systemd/system/containerd.service.d/http_proxy.conf
systemctl daemon-reload
systemctl restart containerd 
```
- 在容器内，`ip addr`查看容器的eth0的IP，如172.18.0.2
- 退出容器命令行，用kn-quickstart创建Knative
```commandline
kn quickstart kind
```
- 修改knative serving的配置文件，将其中的`127.0.0.1.sslip.io`中的`127.0.0.1`改为桌面电脑的局域网IP
```commandline
kubectl edit cm config-domain --namespace knative-serving
```
- 修改kourier负载均衡的外部IP为容器的eth0 IP，即在clusterIPs配置下添加下面两行内容
```commandline
kubectl edit service -n kourier-system kourier
```
```yaml
  externalIPs:
  - 172.18.0.2
```
- 创建飞书能回调的互联网地址，例如`https://1cb8-223-72-47-65.ngrok.io`
```commandline
ngrok http 80
``` 
- 创建nginx转发互联网地址到Knative服务
```commandline
docker run --name event-gw -p 80:80 -d nginx
```
- 获取nginx的容器ID，并登录到该容器命令行
```commandline
docker ps
docker exec -it your-container-id bash
```
- 修改nginx配置文件，将访问转发到Knative的feishu-receiver服务，即将`location /`的{}里改为下面两行转发配置
```shell
vi /etc/nginx/conf.d/default.conf
```
```
proxy_pass http://feishu-receiver.[tenant-namespace-name].[desktop-lan-ip].sslip.io:31180;
proxy_http_version 1.1;
```
### 3.1.4 编译打包
#### 3.1.4.1 获取源代码
```commandline
git clone git@gitlab.cicconline.com:songxiang/imbroker.git
cd imbroker\feishu-receiver
```
#### 3.1.4.2 编辑feishu-receiver路径下的.env
- **APP_ID**：在飞书应用配置的凭证与基础信息页面，获取`App ID`
- **APP_SECRET**：在飞书应用配置的凭证与基础信息页面，获取`App Secret`
- **VERIFICATION_TOKEN**：在飞书应用配置的事件订阅页面，获取`Verification Token`
- **ENCRYPT_KEY**：在飞书应用配置的事件订阅页面，获取`Encrypt Key`
#### 3.1.4.3 修改写死在wxwork-robot-sender的server.py代码的里[企业微信群机器人的webhook地址](https://developer.work.weixin.qq.com/document/path/91770)，设置为自己群机器人的地址
#### 3.1.4.4 打包docker镜像并上传到hub
```commandline
docker docker build -t your-docker-hub-id/imbroker-feishu-receiver .
docker push your-docker-hub-id/imbroker-feishu-receiver
cd ..\dispatcher
docker docker build -t your-docker-hub-id/imbroker-dispatcher .
docker push your-docker-hub-id/imbroker-dispatcher
cd ..\wxwork-robot-sender
docker docker build -t your-docker-hub-id/imbroker-wxwork-robot-sender .
docker push your-docker-hub-id/imbroker-wxwork-robot-sender
cd ..\feishu-receiver
```
### 3.1.5在Knative中部署整个应用
- 在网上随便生成个GUID，如`b6967144-9c39-479c-97d6-25e264ff5204`，作为租户id，并为其创建同名k8s namespace
```commandline
kubectl craete namespace b6967144-9c39-479c-97d6-25e264ff5204
```
- 创建租户命名空间的Knative eventing的broker
```commandline
kn broker create ce-broker -n b6967144-9c39-479c-97d6-25e264ff5204
```
- 创建接收飞书消息、分发消息转发任务、发送微信群机器人消息的3个Knative service
```commandline
kn service create feishu-receiver -n b6967144-9c39-479c-97d6-25e264ff5204 --image your-docker-hub-id/imbroker-feishu-receiver@the-digest-of-the-image-on-docker-hub --port 8080 --env-file ./.env
kn service create dispatcher -n b6967144-9c39-479c-97d6-25e264ff5204 --image your-docker-hub-id/imbroker-dispatcher@the-digest-of-the-image-on-docker-hub --port 8080
kn service create wxwork-robot-sender -n b6967144-9c39-479c-97d6-25e264ff5204 --image your-docker-hub-id/imbroker-wxwork-robot-sender@the-digest-of-the-image-on-docker-hub --port 8080
```
- 创建feishu-receiver到ce-broker、dispatcher到ce-broker的sinkbinding
```commandline
kn source binding create feishu-event --namespace b6967144-9c39-479c-97d6-25e264ff5204  --subject Service:serving.knative.dev/v1:feishu-receiver --sink http://broker-ingress.knative-eventing.svc.cluster.local/b6967144-9c39-479c-97d6-25e264ff5204/ce-broker
kn source binding create dispatcher-event --namespace b6967144-9c39-479c-97d6-25e264ff5204  --subject Service:serving.knative.dev/v1:dispatcher --sink http://broker-ingress.knative-eventing.svc.cluster.local/b6967144-9c39-479c-97d6-25e264ff5204/ce-broker
```
- 用以下内容创建ce-broker到dispatcher的trigger的yaml文件，并用kubectl应用
```yaml
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: dispatcher-trigger
  namespace: b6967144-9c39-479c-97d6-25e264ff5204
spec:
  broker: ce-broker
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: dispatcher
```
```commandline
kubectl apply -f dispatcher-trigger.yaml
```
- 用以下内容创建ce-broker到wxwork-robot-sender的trigger，并用kubectl应用
```yaml
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: wxwork-robot-sender-trigger
  namespace: b6967144-9c39-479c-97d6-25e264ff5204
spec:
  broker: ce-broker
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: wxwork-robot-sender
```
```commandline
kubectl apply -f wxwork-robot-sender-trigger.yaml
```
### 3.1.6 配置飞书机器人
- 进入`飞书开放平台`->`开发者后台`，在应用配置页面的`事件订阅`页面，配置请求网址URL为用ngrok发布的后端服务公网地址，例如`https://1cb8-223-72-47-65.ngrok.io`
- 在应用配置页面的`应用功能`的`机器人`页面，打开对应功能
- 将此机器人邀请入有消息要转发的飞书群
### 3.1.7 验证
- 在飞书群里发送@应用机器人的消息，对应的企业微信群里将收到同样的消息
## 4. Issues
接下来这项目还有以下开发任务，欢迎有兴趣的兄弟业余时间一起来尝试下FaaS，语言不限:D
- 实现dispatcher的数据存储机制（包括租户信息-含各IM工具的应用信息、用户配置的各IM工具之间的群对应关系-包含唯一ID/类型/IM工具内的群ID）
- 实现多租户实例的自动部署（含Knative部署yaml文件）
- 实现各IM工具消息接收和发送服务
  - 飞书机器人消息发送
  - 飞书应用消息发送
  - 企业微信消息接收
  - 企业微信应用消息发送
  - 钉钉消息接收
  - 钉钉机器人消息发送
  - 钉钉应用消息发送
  - 微信服务号消息接收
  - 微信服务号消息发送
  - 邮件消息接收
  - 邮件消息发送
- 实现租户和用户的图形配置界面
  - 飞书小程序图形界面
  - 企业微信和微信小程序图形界面
  - 钉钉小程序图形界面
