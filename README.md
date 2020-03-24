# 基于异常检测的大图采样技术
## 研究背景
网络（Network）又称为图（Graph），由节点和连接边组成。通常一切具有关系的实体都可以抽象成一个网络（图），即实体被抽象成节点，实体之间的关系被抽象成边。在真实世界中，图无处不在——人与人之间的关系构成了社交网络，互联网的各通信节点连接起来构成了信息网络，国家内的省份、城市、乡镇之间存在不同层次的交通网络。随着大数据时代的到来，人们收集、存储与分析图数据的能力不断提高，为深入探索世界提供了前所未有的机会。例如，截至2017年底，Facebook月报告的活跃用户数达到21亿。研究人员可以通过社交网络分析来探索用户行为与交流模式。然而，随着图规模不断扩大，处理图数据的难度大幅增加，这无疑给数据挖掘领域与可视化领域带来了空前的挑战。

现实领域中，有许多应用都需要对图数据进行分析与挖掘，或者需要通过可视化手段获取图结构的直观印象。然而，由于图规模的迅速扩大，使得数据挖掘算法处理图数据的代价越来越昂贵，而图可视化方法也因算法复杂性、屏幕空间大小、视觉混杂和人的感知能力等受到诸多限制。目前已有一些方法用于有效解决可伸缩性问题。由此可知，解决该问题有两种基本策略：一种是设计高效的图数据分析算法，另一种是通过采样技术在保持原始图结构或关键图属性的同时减小图的大小。其中，采样技术因其简单性和高效性，被广泛用于数据挖掘技术与可视化技术中。

图采样是一种通过随机选择原始图的若干顶点和边构建子图的技术，通常可以分为三大类：基于顶点的图采样、基于边的图采样、基于子图的图采样。图采样技术的重点是：采样结果能够以尽可能少的采样率保持尽可能多的原始图属性或原始图结构。子图采样相较其他两种方法来说更能显示在原始图属性及特征保持上的优势。然而，根据图挖掘专家对采样结果所保留的图属性进行的量化度量评估不难发现，尽管图采样方法种类繁多，但是不同种类的采样算法对应着不同的分析目标与分析任务，没有一种单一的策略可以保留原始图的所有结构特性。因此应根据不同场景的需要选择合适的图采样算法。

针对大型复杂图数据做分析时，异常查找是必不可少的，因为了解数据中少数不寻常的内容比了解其一般结构更为重要和有趣。例如，在社交网络中为了维护网络的安全和隐私，有必要对不同于社交网络普遍行为的结构异常进行检测与分析。并且对于图可视分析而言，快速发现异常，交互推理异常是图可视分析的一种主流分析需求。因此，无论是对于原始图还是其图采样结果，异常结构对于数据分析来说都是十分重要的。然而就目前而言，极少有采样方法讨论了异常保持问题，其大都将重点放在图主特征的属性保留上，而很少涉及对异常模式的保留。甚至有一些算法在采样过程中会优先丢弃异常，这对之后的数据分析来说是很不合适的。

本项目以子图采样的方法设计为主攻方向，以采样算法的异常保留问题与原始图的重要属性保留问题作为研究目标，从图理论科学、可视化方法、异常检测技术三方面攻关多项技术难点。首先，我们需要将异常检测技术与图采样技术融合，以实现图采样结果的特征保留。其次，我们将从图拓扑角度和可视化感知角度探索两个问题：1）该场景下哪些图属性需要保留；2）采样策略需要如何保留这些关键图属性。最后，我们需要从图理论科学和可视化感知角度设计合理、有效的采样结果量化评估方案。我们的项目通过对异常保留与基于图属性与可视感知双驱动的偏差控制大图采样的探索，能够减少图数据的计算量与可视化角度的可视混杂问题，有效提高视图的可读性，帮助数据分析人员理解复杂网络数据结构与检测异常数据，节省其网络探索时间。
## 研究成果
### 异常提取策略
* 设计一种基于三角形坍缩策略的高度稀有结构提取策略
* 设计一种基于割点的边界稀有结构提取策略

### 设计一种基于异常保持的图采样方法

### 算法效果展示1

### 算法效果展示2

### 算法效果展示3

### 算法视频介绍
