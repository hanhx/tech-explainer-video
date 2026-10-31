# 机制、来源与教学边界（Wi-Fi 主线）

本片是已发布“从地址栏到服务器”的独立续篇。浅色手绘、16:9、中文本人音色；使用教学场景，不是真实抓包。V1 与尚未完成的有线 V2 均保留。

## 场景假设

- 现代笔记本 PC-A，以无线网卡 B 接入家庭 Wi-Fi。蓝色有线接口 A 仅作对照，可内置或外接；它没有连接，不提供备用路径。“无线网卡”与“实体网卡”并非对立分类。
- 本例为 IPv4，第一次接入时没有可用租约，采用 DHCPv4。不是每次连 Wi-Fi 都必然从 IP 空白开始；静态配置、已有租约、IPv6、缓存命中可改变实际过程。
- 本例为基础设施模式、家庭 WPA2-Personal 场景。扫描、认证、关联、相应密钥协商合并演示；只有接入可用后才开始普通 DHCP 数据通信。省略完整安全帧、802.11 ACK/重试、聚合、漫游、企业认证、门户认证等细节。
- 无线 B 的当前 MAC 为 `02:6A:10:20:30:41`；有线 A 的示例 MAC 为 `02:6A:10:20:30:40`；网关 LAN MAC 为 `02:AA:BB:CC:DD:01`。均为人为构造的本地管理单播地址。当前 Wi-Fi MAC 可以是系统为本网络使用的私有地址；不声称它固定不变。
- 家用网关将 AP、LAN 网关和 DHCP 服务集成在同一设备中。AP 的 BSSID 与网关 LAN MAC 属于不同角色，不能因为同一盒子就假设它们相同。
- DHCP 结果：电脑 `192.168.1.20/24`、网关 `192.168.1.1`、解析器 `192.0.2.53`。本片故意选远端解析器，且邻居缓存初始没有网关记录，以便呈现路由与 ARP。若 DNS 在本网段或邻居缓存已有记录，实际过程会不同。
- 示例 `www.example.com` 的假设结果为 `198.51.100.80`，不是它的真实 DNS 记录。文档网段用于教学。五层剖面是发送端封装视图，网关后的 NAT、逐跳换帧及服务器内部处理由上一集解释，此处缩略。

## 协议与画面映射

| 主题 | 本片必须准确表达的内容 | 一手资料 |
|---|---|---|
| 802.3 / 802.11 | IEEE 802 是标准族，有线以太网与无线局域网的接入/帧格式不同；无线网卡也包含物理收发功能 | [IEEE 802](https://www.ieee802.org/)、[IEEE 802.11](https://www.ieee802.org/11/)、[IEEE 802.3](https://www.ieee802.org/3/) |
| Wi-Fi 接入 | 基础认证、关联及相应安全协商先于普通 DHCP/ARP/应用数据；各安全模式具体顺序与内容有区别 | [Cisco 无线认证与关联流程](https://www.cisco.com/c/en/us/support/docs/wireless-mobility/wireless-lan-wlan/116493-technote-technology-00.html) |
| 私有 MAC | 系统可为不同无线网络使用不同地址，并可按策略改变；不称为永久身份证 | [Apple 私有 Wi-Fi 地址](https://support.apple.com/en-sg/102509) |
| DHCPv4 | Discover、Offer、Request、ACK；UDP 服务端 67、客户端 68；初始源 IP 全零；回应可广播或单播；配置不只 IP | [RFC 2131](https://www.rfc-editor.org/rfc/rfc2131.html)、[RFC 2132](https://www.rfc-editor.org/rfc/rfc2132.html) |
| ARP | 本地链路上解析 IPv4 邻居的 MAC；此例查网关，不查远端 DNS/网站的 MAC | [RFC 826](https://www.rfc-editor.org/rfc/rfc826.html) |
| 无线帧地址 | 此例上行 To DS：无线接收者是 AP，发送者是无线 B，另一地址表示链路最终目的。广播 ARP 请求目的为广播；DNS 查询载荷的链路目的为网关 | [Cisco 802.11 帧地址说明](https://community.cisco.com/t5/networking-knowledge-base/802-11-frames-a-starter-guide-to-learn-wireless-sniffer-traces/ta-p/3110019) |
| 类型封装 | 无线数据帧的解密后概念视图：LLC/SNAP 中以 0x0806 标识 ARP、0x0800 标识 IPv4；不是把以太网 EtherType 字段直接改名为无线帧头 | [IANA IEEE 802 Numbers](https://www.iana.org/assignments/ieee-802-numbers/ieee-802-numbers.xhtml)、[IEEE 802.11-2012 标准副本](https://mrncciew.com/wp-content/uploads/2014/10/ieee-802-11-2012.pdf) |
| DNS | 本例 UDP 目标端口 53；DNS 也支持 TCP 等传输，不将 DNS 与 UDP 画等号 | [RFC 1035 §4.2](https://www.rfc-editor.org/rfc/rfc1035.html) |
| UDP / TCP | 独立数据报与有序字节流；是传输选择，不是连续必经的两层 | [RFC 768](https://www.rfc-editor.org/rfc/rfc768.html)、[RFC 9293](https://www.rfc-editor.org/rfc/rfc9293.html) |
| 断开与重连 | 关闭无线接口与物理拔线是不同动作，都可能让当前路径不可用；不等于正常发送 TCP FIN；重连检查后可复用有效旧配置 | [Linux 接口状态](https://docs.kernel.org/networking/operstates.html)、[RFC 2131 §3.7](https://www.rfc-editor.org/rfc/rfc2131.html)、[RFC 4436](https://www.rfc-editor.org/rfc/rfc4436.html) |
| RARP | 历史有线工作站 C 的独立对照，用自己的 MAC 向本地服务器询问自己的 IP，不接在 DHCP 后面 | [RFC 903](https://www.rfc-editor.org/rfc/rfc903.html) |

## 五层与简化边界

本片用常见五层教学划分：应用、传输、网络、链路、物理。DNS 查询先作为应用数据，再由 UDP、IPv4、无线链路封装，物理层编码成无线电信号；物理层不是又加一层报头。不是把每个出现的协议都塞进同一个套娃：ARP 不套在 IP/UDP 内，RARP 不参加现代 DHCP 主线。

HTTPS 镜头仅回顾 TCP、TLS、HTTP 的先后关系；握手、安全记录、HTTP 版本和服务器内部流程已缩略。本例选 HTTPS/TCP，不覆盖 HTTP/3/QUIC。无线帧概念图省略加密开销、校验、QoS 等字段，不按字节比例，也不是实际抓到的明文帧。无线电曲线仅表示编码信号，不对应某种实际调制波形。

已绘制页面在断网后可以保留；新请求可能等待、重传后失败或被系统立即通知。切断当前接口没有自动生成正常 FIN 的含义。本例没有其他可用接口；有备用路径时，应用行为还取决于路由、连接迁移和实现。

## 验收边界

机制来源核对、实际编码帧抽查、完整解码和音频哈希/波形对齐分别记录。自动校验与抽帧不等于完整观众测试或本人连续听音认可。

## V6 表述与节奏修订

- 把 DHCP 首次确认、四步回放、UDP 端口拆开。回放期间参数已生效，底部明确标记回看，避免以为又进行一轮配置。
- 首次正式解释 TCP 时，口播为“TCP，传输控制协议”；UDP 为“UDP，用户数据报协议”。DNS、ARP、RARP 也对应口播缩写和中文名。实际音频文件与处理溯源见 audio-provenance.json。
- 五层图补出源/目的端口与地址：DNS 查询示意源 UDP 端口 53000、目的 53；源 IP 192.168.1.20、目的 IP 192.0.2.53。53000 是任取的示意客户端端口，既不是固定值，也不是本机抓包结果。
- HTTPS 镜头的一次移动胶囊表示该阶段交换的概括，不能据此推算 TCP 或 TLS 握手报文数。画面只说明连接、加密会话、网页请求和响应的顺序。浏览器绘制在内容到达后开始，实际浏览器也可流式解析、边收边绘。
- 箭头不是协议事实。本版去掉说明性动态箭头，保留消息位移与状态更新；定义读图段允许停留。四步回放各消息移动 2.00 至 2.98 秒，MAC 推近/拉回各 2.1 秒，这些是本片编排选择，并非协议耗时或统一教学标准。
