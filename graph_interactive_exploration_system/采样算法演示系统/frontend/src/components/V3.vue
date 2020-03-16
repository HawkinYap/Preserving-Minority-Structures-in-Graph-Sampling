<template>
    <div class="content">
        <div class="control-bar">
            <div class="settings-item">
                <div class="setting-name">Graph Data Set</div>
                <div class="setting-value">
                    <el-select v-model="Graph_Data_Set_value" placeholder="Please select Graph Data"
                               @change="initOriginGraph">
                        <el-option
                                v-for="item in GraphDataSet_list"
                                :key="item"
                                :label="item"
                                :value="item">
                        </el-option>
                    </el-select>
                </div>
                <span id="upload_tag">or</span>
                <input type="button" class="button" value="Upload File">
            </div>
            <div class="settings-item">
                <div class="setting-name">Algorithm</div>
                <div class="setting-value">
                    <el-select v-model="algorithm_value" placeholder="Please select algorithm"
                               @change="initAgorithmParams">
                        <el-option
                                v-for="item in algorithm_list"
                                :key="item.label"
                                :label="item.label"
                                :value="item.label">
                        </el-option>
                    </el-select>
                </div>
            </div>
            <div class="settings-item">
                <div class="setting-name">Parameters</div>
                <div class="setting-value param-option">
                    <span>rate</span>
                    <input class="option_input" type="text" v-model="option_settings.rate">
                    
                    <span>seed</span>
                    <el-select v-model="option_settings.seed" placeholder="">
                        <el-option
                                v-for="item in seed_list"
                                :key="item"
                                :label="item"
                                :value="item">
                        </el-option>
                    </el-select>
                    <div class="other_options">
                        <div class="option_item" v-for="(option,index) in get_option_labels" :key="index">
                            <el-divider direction="vertical"></el-divider>
                            <span>{{option}}</span><input class="option_input" type="text"
                                                          v-model="option_settings[option]">
                        </div>
                    </div>
                </div>
            </div>
            <input type="button" id="run-btn" value="Run" @click="run">
        </div>
        <div class="graph-container">
            <div class="tooltip" v-show="node_Id">{{node_Id}}</div>
            <div class="graph-box origin-graph">
                <span id="origin-tag">Original Graph</span>
                <span id="origin-info-tag" v-show="current_graph===''">Please select or upload Graph Data Set</span>

                <div class="loading-div-origin" v-show="LoadingOrigin" v-loading="LoadingOrigin">

                </div>
            </div>
            <div class="graph-box sampling-graph" id="sampling-graph">
                <span id="sampling-tag">Graph Samples</span>
                <div class="loading-div" v-show="LoadingSampling" v-loading="LoadingSampling"
                     style="left: 1%;">

                </div>
            
                <i class="el-icon el-icon-arrow-left" v-show="queue_num>=3&&samping_hover&&left_num!==1"
                   @click="switch_view('left')"
                   style="color:#999999;font-size:25px;z-index: 2000;cursor: pointer;position: absolute;top: 45%;left: 0.8%"></i>
                <i class="el-icon el-icon-arrow-right" v-show="queue_num>=3&&samping_hover&&right_num!==queue_num"
                   @click="switch_view('right')"
                   style="color:#999999;font-size:25px;z-index: 2000;cursor: pointer;position: absolute;top: 45%;right: 0.8%;"></i>
                <div v-show="queue_num>=2"
                     style="position:absolute;left:50%;top:4%;width:1px;height:93%;border-right:1px dashed #CCCCCC;">
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import axios from "../utils/axios"
    import * as d3 from "d3"

    //鱼眼组件对象
    let d3_fisheye = {
        scale: function (scaleType) {
            return d3_fisheye_scale(scaleType(), 3, 0);
        },
        circular: function () {
            var radius = 200,
                distortion = 2,
                k0,
                k1,
                focus = [0, 0];

            function fisheye(d) {
                var dx = d.cx - focus[0],
                    dy = d.cy - focus[1],
                    dd = Math.sqrt(dx * dx + dy * dy);
                if (!dd || dd >= radius) return {x: d.cx, y: d.cy, z: 1};
                var k = k0 * (1 - Math.exp(-dd * k1)) / dd * .75 + .25;
                return {x: focus[0] + dx * k, y: focus[1] + dy * k, z: Math.min(1, 10)};
            }

            function rescale() {
                k0 = Math.exp(distortion);
                k0 = k0 / (k0 - 1) * radius;
                k1 = distortion / radius;
                return fisheye;
            }

            fisheye.radius = function (_) {
                if (!arguments.length) return radius;
                radius = +_;
                return rescale();
            };
            fisheye.distortion = function (_) {
                if (!arguments.length) return distortion;
                distortion = +_;
                return rescale();
            };
            fisheye.focus = function (_) {
                if (!arguments.length) return focus;
                focus = _;
                return fisheye;
            };
            return rescale();
        }
    };

    //鱼眼缩放辅助函数1
    function d3_fisheye_scale(scale, d, a) {

        function fisheye(_) {
            var x = scale(_),
                left = x < a,
                v,
                range = d3.extent(scale.range()),
                min = range[0],
                max = range[1],
                m = left ? a - min : max - a;
            if (m == 0) m = max - min;
            return (left ? -1 : 1) * m * (d + 1) / (d + (m / Math.abs(x - a))) + a;
        }

        fisheye.distortion = function (_) {
            if (!arguments.length) return d;
            d = +_;
            return fisheye;
        };

        fisheye.focus = function (_) {
            if (!arguments.length) return a;
            a = +_;
            return fisheye;
        };

        fisheye.copy = function () {
            return d3_fisheye_scale(scale.copy(), d, a);
        };

        fisheye.nice = scale.nice;
        fisheye.ticks = scale.ticks;
        fisheye.tickFormat = scale.tickFormat;

        return rebind(fisheye, scale, "domain", "range");
    }

    //鱼眼辅助函数2
    function rebind(e, t) {
        var n = 1, r = arguments.length, i;
        while (++n < r)
            e[i = arguments[n]] = a(e, t, t[i]);
        return e
    }

    //字符串格式化辅助函数
    String.prototype.format = function (args) {
        var result = this;
        if (arguments.length < 1) {
            return result;
        }
        var data = arguments;
        if (arguments.length === 1 && typeof (args) == "object") {
            data = args;
        }
        for (var key in data) {
            var value = data[key];
            if (undefined !== value) {
                result = result.replace("{" + key + "}", value);
            }
        }
        return result;

    };

    export default {
        name: 'demoV3',
        data() {
            return {
                GraphDataSet_list: [
                    'as', 'cagrqc', 'cspan', 'eurosis', 'facebook107', 'facebook414', 'facebook1684', 'facebook1912', 'oregon', 'p2p', 'pgp'
                ],
                Graph_Data_Set_value: '',
                algorithm_list: {
                    BF: {label: 'BF', options: []},
                    MCGS: {label: 'MCGS', options: ['alpha', 'beta', 'loss weight']},
                    FF: {label: 'FF', options: []},
                    GSP: {label: 'GSP', options: []},
                    DPL: {label: 'DPL', options: []},
                    RAS: {label: 'RAS', options: []},
                    RMSC: {label: 'RMSC', options: []},
                    SSP: {label: 'SSP', options: []},
                    SST: {label: 'SST', options: []},
                    TIES: {label: 'TIES', options: []}
                },
                algorithm_value: '',
                rate_list: [0.1, 0.2, 0.3, 0.4],
                seed_list: ["random", "high degree", "high betweenness", "peripheral nodes"],
                option_settings: {
                    'rate': '',
                    'seed': '',
                    'alpha': '1',
                    'beta': '3',
                    'loss weight': '1,0,0'
                },
                left_num: 1,
                right_num: 2,
                queue_num: 0,
                samping_hover: true,
                current_graph: '',
                LoadingSampling: false,
                LoadingOrigin: false,
                label_tip: null,
                node_Id: false,
                anomaly_total: {},
                select_minotype: '',
                rim_anomaly_total: {}
            }
        },
        mounted() {
            this.$nextTick(() => {
                this.initSetting();
            })
        },
        methods: {
            initSetting() {
                var self = this;
                // 设置原始图和采样图的框的高度大小
                let screenWidth = document.documentElement.clientWidth || document.body.clientWidth;
                let screenHeight = document.documentElement.clientHeight || document.body.clientHeight;
                document.querySelector(".origin-graph").style.height = screenHeight * 0.80 + "px";
                var sampling_graph = document.querySelector(".sampling-graph");
                sampling_graph.style.height = screenHeight * 0.80 + "px";
                sampling_graph.onmouseenter = function () {
                    self.samping_hover = true;
                };
                sampling_graph.onmouseleave = function () {
                    self.samping_hover = false;
                };
                
                this.label_tip = document.querySelector('.tooltip');

                document.querySelector("#app > div.content > div.control-bar > div:nth-child(3) > div.setting-value.param-option > div.el-select > div > input").style.width = "95%"
            },

            //重置算法参数设置
            initAgorithmParams() {
                this.option_settings = {
                    'rate': '0.3',
                    'seed': 'random',
                    'alpha': '1',
                    'beta': '3',
                    'loss weight': '1,0,0'
                }
            },
            //添加鱼眼效果的渲染原始图svg
            //使用Json格式加载
            fisheye_test() {
                var self = this;
                axios.post("/get_minotype/", {
                    graph_name: this.Graph_Data_Set_value
                }).then(response => {
                    if (response.data.state === "success") {
                        self.rim_anomaly_total = response.data.anomaly_total['sham_rim_list'];
                    }
                    else{
                        console.log("Error")
                    }
                });
                setTimeout(function () {
                    d3.json(self.origin_fisheye_file).then(function (data) {
                        // 删除之前的
                        d3.select(".origin-graph").selectAll("svg").remove();

                        //要先从data里获取svg头信息，用于设置svg元素属性
                        var origin_svg = d3.select(".origin-graph").append("svg")
                            .attr("width", data.svg_width)
                            .attr("height", data.svg_height)
                            .attr("viewBox", data.svg_viewBox);

                        var link = origin_svg.selectAll(".link")
                            .data(data.links)
                            .enter().append("line")
                            .attr("class", "link")
                            .attr("x1", function (d) {
                                return data.nodes[d.source].cx
                            })
                            .attr("y1", function (d) {
                                return data.nodes[d.source].cy
                            })
                            .attr("x2", function (d) {
                                return data.nodes[d.target].cx
                            })
                            .attr("y2", function (d) {
                                return data.nodes[d.target].cy
                            }).style("stroke", "#bcbcbc");

                        var node = origin_svg.selectAll(".node")
                            .data(data.nodes)
                            .enter().append("circle")
                            .attr("class", function (d) {
                                return d.id;
                            })
                            .attr("cx", function (d) {
                                return d.cx;
                            })
                            .attr("cy", function (d) {
                                return d.cy;
                            })
                            .attr("r", function (d) {
                                return d.r * 1.7
                            })
                            .style("fill", "#cccccc")
                            .style("stroke", "#666666");

                        let parentNode = document.querySelector(".origin-graph");
                        parentNode.setAttribute("open-fisheye", true);
                        var parent_Width = parentNode.clientWidth;
                        var parent_Height = parentNode.clientHeight;
                        let svgWidth = origin_svg.attr("width").replace("px", "");
                        let svgHeight = origin_svg.attr("height").replace("px", "");
                        var margin = {left: 20, right: 20, top: 20, bottom: 20};
                        var scaleNumber = d3.min([(parent_Width - margin.left - margin.right) / svgWidth, (parent_Height - margin.top - margin.bottom) / svgHeight]);
                        var origin_svgWidth = svgWidth * scaleNumber;
                        var origin_svgHeight = svgHeight * scaleNumber;
                        origin_svg
                            .attr("width", origin_svgWidth)
                            .attr("height", origin_svgHeight)
                            .style("position", "absolute")
                            .style("left", (parent_Width - origin_svgWidth) / 2 + "px")
                            .style("top", (parent_Height - origin_svgHeight) / 2 + "px");

                        //添加点击节点高亮事件(可取消)
                        origin_svg.selectAll("circle")
                            .on("click", function () {
                                var current_node = d3.select(this);
                                if (current_node.style("fill") === 'rgb(204, 204, 204)') {
                                    current_node.style("fill", "yellow")
                                } else {
                                    current_node.style("fill", "rgb(204, 204, 204)")
                                }
                            });

                        //添加鼠标hover标注事件
                        origin_svg.selectAll("circle")
                            .on("mouseover", function () {
                                var current_node = d3.select(this);
                                var node_id = parseInt(current_node.attr("class").replace("id_", ""));
                                var index = (self.rim_anomaly_total['origin_cspan'] || []).findIndex(item => item === node_id) + 1;
                                self.label_tip.style.left = d3.event.pageX + 15 + "px";
                                self.label_tip.style.top = d3.event.pageY + 5 + "px";
                                if (index !== 0) {
                                    self.node_Id = "Id_" + node_id + " " + "rank_" + index;
                                } else {
                                    
                                }
                               
                            })
                            .on("mouseout", function () {
                                self.node_Id = false
                            });


                        // 添加原始svg缩放事件
                        // 新建d3缩放对象
                        var origin_zoomer = d3.zoom()
                            .scaleExtent([1, 100])
                            .on("zoom", () => {
                                //先暂时关闭鱼眼特效,即恢复原始大小效果

                                parentNode.setAttribute("open-fisheye", false);
                                origin_svg.selectAll("line")
                                    .attr("x1", function (d) {
                                        return data.nodes[d.source].cx
                                    })
                                    .attr("y1", function (d) {
                                        return data.nodes[d.source].cy
                                    })
                                    .attr("x2", function (d) {
                                        return data.nodes[d.target].cx
                                    })
                                    .attr("y2", function (d) {
                                        return data.nodes[d.target].cy
                                    });
                                origin_svg.selectAll("circle")
                                    .attr("cx", function (d) {
                                        return d.cx;
                                    })
                                    .attr("cy", function (d) {
                                        return d.cy;
                                    })
                                    .attr("r", function (d) {
                                        return d.r * 1.7
                                    });
                                //将线和节点全部缩放
                                origin_svg.selectAll('line').attr("transform", d3.event.transform);
                                origin_svg.selectAll('circle').attr("transform", d3.event.transform);

                                var scale_size = d3.event.transform.k;

                                //如果是缩放为原来大小，则再打开鱼眼特效
                                if (scale_size === 1) {
                                    parentNode.setAttribute("open-fisheye", true);
                                }

                            });
                        //绑定缩放事件
                        origin_svg.call(origin_zoomer);

                        d3.selectAll('.origin-graph div.reset-btn').remove();

                        //重置svg位置-btn
                        var reset_tag = document.createElement('div');
                        reset_tag.className = 'reset-btn';
                        reset_tag.style.float = 'right';
                        reset_tag.style.marginRight = '8px';
                        reset_tag.style.marginTop = '0.5%';
                        reset_tag.style.cursor = 'pointer';
                        reset_tag.style.border = '1px solid #cccccc';
                        reset_tag.style.boxSizing = 'border-box';
                        reset_tag.style.padding = '0 5px';
                        reset_tag.style.color = '#999999';
                        reset_tag.innerText = 'reset';
                        reset_tag.style.visibility = "hidden";
                        reset_tag.onclick = function () {
                            origin_svg.selectAll("circle")
                                .style("fill", "#cccccc");
                            origin_svg.transition().duration(500).call(
                                origin_zoomer.transform,
                                d3.zoomIdentity,
                                d3.zoomTransform(origin_svg.node()).invert([origin_svgWidth / 2, origin_svgHeight / 2])
                            );
                        };
                        // parentNode.appendChild(reset_tag);

                        //添加稀有结构选择
                        var minotype_text = document.createElement('span');
                        minotype_text.style.color = '#999999';
                        minotype_text.style.position = 'absolute';
                        minotype_text.style.bottom = '3.8%';
                        minotype_text.style.left = '11%';
                        minotype_text.style.fontSize = '18px';
                        minotype_text.innerText = 'Minority Structure:';
                        parentNode.appendChild(minotype_text);
                        var minotype_button = document.createElement('div');
                        minotype_button.style.overflow = 'hidden';
                        minotype_button.style.position = 'absolute';
                        minotype_button.style.bottom = '4%';
                        minotype_button.style.left = '33%';
                        minotype_button.style.width = '60%';
                        minotype_button.style.right = '10%';
                        var minotypeList = ['Super Pivot', 'Huge Star', 'Rim', 'Tie'];
                        minotypeList.forEach(function (obj, index) {
                            var input = document.createElement('input');
                            input.className = obj.replace("Super ", "").replace("Huge ", "")
                            input.type = 'checkbox';
                            input.style.margin = '0px 5px 0 11px';
                            input.name = 'category';
                            input.value = obj;
                            input.onclick = function () {
                                let linear = d3.scaleLinear().domain([0, self.anomaly_total[obj].length]).range([0, 1]);
                                let compute = d3.interpolate('red', 'white');
                                
                                self.anomaly_total[obj].forEach(function (item, index) {
                                    var current_node = origin_svg.select("circle.id_" + item);
                                    if (current_node.style("fill") === 'rgb(204, 204, 204)') {
                                        
                                        current_node.style("fill", "rgb(123,187,109)")
                                    } else {
                                        current_node.style("fill", "rgb(204, 204, 204)")
                                    }
                                })
                            };
                            var input_span = document.createElement('span');
                            input_span.style.color = "#999999"
                            input_span.innerText = obj;
                            minotype_button.appendChild(input);
                            minotype_button.appendChild(input_span)
                        });
                        parentNode.appendChild(minotype_button);


                        //添加鱼眼效果
                        origin_svg.on("mousemove", function () {
                            if (parentNode.getAttribute("open-fisheye") === 'true') {
                                var fisheye = d3_fisheye.circular()
                                    // .radius(120);
                                    .radius(svgWidth / 5);
                                fisheye.focus(d3.mouse(this));
                                node.each(function (d) {
                                    d.fisheye = fisheye(d);
                                })
                                    .attr("cx", function (d) {
                                        return d.fisheye.x;
                                    })
                                    .attr("cy", function (d) {
                                        return d.fisheye.y;
                                    })
                                    .attr("r", function (d) {
                                        return d.fisheye.z * d.r * 1.7;
                                    });

                                link.attr("x1", function (d) {
                                    return data.nodes[d.source].fisheye.x
                                })
                                    .attr("y1", function (d) {
                                        return data.nodes[d.source].fisheye.y
                                    })
                                    .attr("x2", function (d) {
                                        return data.nodes[d.target].fisheye.x
                                    })
                                    .attr("y2", function (d) {
                                        return data.nodes[d.target].fisheye.y
                                    });
                            }
                        });
                        // parentNode.onmouseenter = function () {
                        // reset_tag.style.visibility = "visible";
                        // };
                        // parentNode.onmouseleave = function () {
                        // reset_tag.style.visibility = "hidden";
                        // };
                        self.LoadingOrigin = false
                    });
                }, 800)

            },
            //运行算法
            run() {
                var self = this;
                //检测设置值是否合法
                if (!this.Graph_Data_Set_value) {
                    this.$message('Please select Graph Data Set');
                    return;
                }
                if (!this.algorithm_value) {
                    this.$message('Please select sampling algorithm');
                    return;
                }
                for (var index in this.option_settings) {
                    if (!this.option_settings[index]) {
                        this.$message('Please set parameter - ' + index);
                        return;
                    } else {
                        var param_value = this.option_settings[index];
                        if (index === 'rate' && (!/^[0-9]*\.{0,1}[0-9]*$/.test(param_value) || !(parseFloat(param_value) > 0 && parseFloat(param_value) < 1))) {
                            this.$message.error('Please set valid parameter - ' + index);
                            return;
                        } else if (index === 'alpha' && (!/^[0-9]*\.{0,1}[0-9]*$/.test(param_value) || !(parseFloat(param_value) > 0 && parseFloat(param_value) <= 1))) {
                            this.$message.error('Please set valid parameter - ' + index);
                            return;
                        } else if (index === 'beta' && (!/^[0-9]*\.{0,1}[0-9]*$/.test(param_value) || !(parseFloat(param_value) >= 1))) {
                            this.$message.error('Please set valid parameter - ' + index);
                            return;
                        } else if (index === 'loss weight' && (!/^[0-9]*\.{0,1}[0-9]*.{1}[0-9]*\.{0,1}[0-9]*.{1}[0-9]*\.{0,1}[0-9]*$/.test(param_value))) {
                            this.$message.error('Please set valid parameter - ' + index);
                            return;
                        }
                    }
                }

                this.LoadingSampling = true;
                // 渲染采样结果并更新展示队列
                setTimeout(function () {
                    self.initSamplingGraph()
                }, 800 + 600 * Math.random());

            },
            // 加载原始图
            initOriginGraph() {
                var self = this;
                //更新当前图标识和顶部设置栏
                this.current_graph = this.Graph_Data_Set_value;
                this.algorithm_value = '';
                this.option_settings = {
                    'rate': '',
                    'seed': '',
                    'alpha': '1',
                    'beta': '3',
                    'loss weight': '1,0,0'
                };

                //删除采样图列表
                this.left_num = 1;
                this.right_num = 2;
                this.queue_num = 0;
                d3.selectAll('.sampling-item').remove();
                axios.post("/get_minotype/", {
                    graph_name: this.Graph_Data_Set_value
                }).then(response => {
                    self.anomaly_total = response.data.anomaly_total
                });
                this.LoadingOrigin = true;
                //有鱼眼效果的绘图
                this.fisheye_test()
            },
            // 加载采样图并更新展示队列
            initSamplingGraph() {
                var self = this;
                var queue_List = document.querySelectorAll(".sampling-item");

                //先将列表svg恢复原位
                for (var i = 0; i < queue_List.length; i++) {
                    var new_left = 1 + 50 * (queue_List.length - i);
                    if (new_left > 151) {
                        d3.select(queue_List[i]).remove();
                        self.queue_num -= 1;
                    } else {
                        queue_List[i].style.left = new_left + "%";
                        
                    }
                }

                this.left_num = 1;
                this.right_num = 2;

                //创建新的采样图框元素
                var sampling_div = document.createElement('div');
                sampling_div.className = 'sampling-item';
                sampling_div.style.left = '1%';
                sampling_div.style.float = 'left';
                sampling_div.style.position = 'absolute';
                sampling_div.style.top = '4%';
                sampling_div.style.width = '48%';
                sampling_div.style.height = '95%';
                


                //采样算法名称标识
                var span_algorithm = document.createElement('span');
                span_algorithm.style.position = 'absolute';
                span_algorithm.style.top = '1%';
                span_algorithm.style.left = '1%';
                span_algorithm.style.color = '#666666';
                span_algorithm.style.zIndex = '1000';
                span_algorithm.innerHTML = '<b>Algorithm</b> {algorithm}'.format({algorithm: this.algorithm_value});
                sampling_div.appendChild(span_algorithm);

                //采样算法参数标识
                var span_parameters = document.createElement('span');
                span_parameters.style.position = 'absolute';
                span_parameters.style.top = '4%';
                span_parameters.style.left = '1%';
                span_parameters.style.color = '#666666';
                span_parameters.style.zIndex = '1000';
                // var parameters = 'seed={seed} rate={rate}'.format({seed:this.option_settings.seed,rate: this.option_settings.rate});
                var parameters = 'rate={rate}'.format({rate: this.option_settings.rate});
                this.algorithm_list[this.algorithm_value].options.forEach(function (obj, index) {
                    parameters = parameters + '  ' + obj + '=' + self.option_settings[obj];
                });
                if (self.algorithm_value === 'FF') {
                    parameters = parameters + '  ' + 'seed=' + self.option_settings.seed;
                }
                span_parameters.innerHTML = '<b>Paramters</b> {parameters}'.format({parameters: parameters});
                sampling_div.appendChild(span_parameters);

                //关闭采样框标识
                var close_tag = document.createElement('i');
                close_tag.style.position = 'absolute';
                close_tag.style.right = '0.8%';
                close_tag.style.top = '7.5px';
                close_tag.style.cursor = 'pointer';
                close_tag.className = 'sampling-close-btn el-icon-close';
                close_tag.style.visibility = 'hidden';
                close_tag.onclick = function (e) {
                    var target_element = e.currentTarget;
                    var parentNode = target_element.parentNode;
                    var sampling_list = document.querySelectorAll(".sampling-item");
                    var sampling_length = sampling_list.length;
                    var old_left = null;
                    for (let i = 0; i < sampling_length; i++) {
                        if (sampling_list[i] === parentNode) {
                            d3.select(parentNode).remove();
                            self.queue_num -= 1;
                            if (self.left_num < sampling_length - i) {
                                //删的是右边
                                old_left = sampling_length - i - 2;
                            } else {
                                //删的是左边
                                old_left = self.left_num - 1;
                                if (old_left <= 0) {
                                    old_left = 1
                                }
                            }
                            break
                        }
                    }
                    //重新排列
                    var new_sampling_list = document.querySelectorAll(".sampling-item");
                    for (var i = 0; i < new_sampling_list.length; i++) {
                        new_sampling_list[i].style.left = 1 + 50 * (new_sampling_list.length - i - 1) + "%";
                    }
                    self.left_num = 1;
                    self.right_num = 2;

                    //移动回原来的地方(针对有多个item的情况)
                    while (self.queue_num > 2 && self.left_num !== old_left) {
                        self.left_num += 1;
                        self.right_num += 1;
                        new_sampling_list.forEach(function (obj, index) {
                            var new_left = parseInt(obj.style.left.replace("%", "")) - 50;
                            obj.style.left = new_left + "%";
                        });
                    }
                };
                // sampling_div.appendChild(close_tag);

                // axios.post("/run_sampling/", {
                //     graph_name: this.Graph_Data_Set_value,
                //     algorithm_name: this.algorithm_value,
                //     settings: this.option_settings
                // }).then(response => {
                //     if (response.data.state === "success") {

                //添加鱼眼特效后，以json格式读取

                sampling_div.setAttribute("open-fisheye", true);

                d3.json(self.samping_fisheye_file).then(function (data) {
                    var current_algorithm = self.samping_fisheye_file.replace("/static/graph_set/json/cspan/", "").replace(".json", "");
                    //要先从data里获取svg头信息，设置svg元素属性
                    var sampling_svg = d3.select(sampling_div).append("svg")
                        .attr("width", data.svg_width)
                        .attr("height", data.svg_height)
                        .attr("viewBox", data.svg_viewBox);
                    

                    var link = sampling_svg.selectAll(".link")
                        .data(data.links)
                        .enter().append("line")
                        .attr("class", "link")
                        .attr("x1", function (d) {
                            return data.nodes[d.source].cx
                        })
                        .attr("y1", function (d) {
                            return data.nodes[d.source].cy
                        })
                        .attr("x2", function (d) {
                            return data.nodes[d.target].cx
                        })
                        .attr("y2", function (d) {
                            return data.nodes[d.target].cy
                        }).style("stroke", "#bcbcbc");

                    var node = sampling_svg.selectAll(".node")
                        .data(data.nodes)
                        .enter().append("circle")
                        .attr("class", function (d) {
                            return d.id;
                        })
                        .attr("cx", function (d) {
                            return d.cx;
                        })
                        .attr("cy", function (d) {
                            return d.cy;
                        })
                        .attr("r", function (d) {
                            return d.r * 1.7
                        })
                        .style("fill", "#cccccc")
                        .style("stroke", "#666666");
                    var container = document.getElementById('sampling-graph');
                    container.insertBefore(sampling_div, null);//插入到最左边


                    var parent_Width = sampling_div.clientWidth;
                    var parent_Height = sampling_div.clientHeight;
                    var sampling_svg = d3.selectAll(".sampling-item svg:nth-last-child(1)");
                    let svgWidth = sampling_svg.attr("width").replace("px", "");
                    let svgHeight = sampling_svg.attr("height").replace("px", "");
                    var margin = {left: 20, right: 20, top: 20, bottom: 20};
                    var scaleNumber = d3.min([(parent_Width - margin.left - margin.right) / svgWidth, (parent_Height - margin.top - margin.bottom) / svgHeight]);
                    var sampling_svgWidth = svgWidth * scaleNumber;
                    var sampling_svgHeight = svgHeight * scaleNumber;
                    sampling_svg
                        .attr("width", sampling_svgWidth)
                        .attr("height", sampling_svgHeight)
                        .style("position", "absolute")
                        .style("left", (parent_Width - sampling_svgWidth) / 2 + "px")
                        .style("top", (parent_Height - sampling_svgHeight) / 2 + "px");

                    //为节点和边设置样式(用于提示用户当前为新的框)
                    sampling_svg.selectAll("circle")
                        .style("stroke", "#666666")
                        .style("fill", "#cccccc");
                    sampling_svg.selectAll("path")
                        .style("stroke", "#333333");

                    //添加点击节点高亮事件（可取消）
                    sampling_svg.selectAll("circle")
                        .on("click", function () {
                            var current_node = d3.select(this);
                            if (current_node.style("fill") === 'rgb(204, 204, 204)') {
                                current_node.style("fill", "yellow")
                            } else {
                                current_node.style("fill", "rgb(204, 204, 204)")
                            }
                        });


                    //添加鼠标hover标注事件
                    sampling_svg.selectAll("circle")
                        .on("mouseover", function () {
                            var current_node = d3.select(this);
                            var node_id = parseInt(current_node.attr("class").replace("id_", ""));
                            var index = (self.rim_anomaly_total[current_algorithm] || []).findIndex(item => item === node_id) + 1;
                            self.label_tip.style.left = d3.event.pageX + 15 + "px";
                            self.label_tip.style.top = d3.event.pageY + 5 + "px";
                            if (index !== 0) {
                                self.node_Id = "Id_" + node_id + " " + "rank_" + index;
                            } else {
                               
                            }
                        })
                        .on("mouseout", function () {
                            self.node_Id = false
                        });

                    // 添加采样svg缩放事件
                    var sampling_zoomer = d3.zoom()
                        .scaleExtent([1, 100])
                        .on("zoom", () => {
                            //先暂时关闭鱼眼特效,即恢复原始大小效果

                            sampling_div.setAttribute("open-fisheye", false);
                            sampling_svg.selectAll("line")
                                .attr("x1", function (d) {
                                    return data.nodes[d.source].cx
                                })
                                .attr("y1", function (d) {
                                    return data.nodes[d.source].cy
                                })
                                .attr("x2", function (d) {
                                    return data.nodes[d.target].cx
                                })
                                .attr("y2", function (d) {
                                    return data.nodes[d.target].cy
                                });
                            sampling_svg.selectAll("circle")
                                .attr("cx", function (d) {
                                    return d.cx;
                                })
                                .attr("cy", function (d) {
                                    return d.cy;
                                })
                                .attr("r", function (d) {
                                    return d.r * 1.7
                                });
                            //将线和节点全部缩放
                            sampling_svg.selectAll('line').attr("transform", d3.event.transform);
                            sampling_svg.selectAll('circle').attr("transform", d3.event.transform);
                            var scale_size = d3.event.transform.k;

                            //如果是缩放为原来大小，则再打开鱼眼特效
                            if (scale_size === 1) {
                                // self.open_fisheye = true;
                                sampling_div.setAttribute("open-fisheye", true);
                            }
                        });
                    //绑定缩放事件
                    sampling_svg.call(sampling_zoomer);

                    //重置svg位置
                    var reset_tag = document.createElement('div');
                    reset_tag.className = 'reset-btn';
                    reset_tag.style.float = 'right';
                    reset_tag.style.marginRight = '28px';
                    reset_tag.style.marginTop = '5px';
                    reset_tag.style.cursor = 'pointer';
                    reset_tag.style.border = '1px solid #cccccc';
                    reset_tag.style.boxSizing = 'border-box';
                    reset_tag.style.padding = '0 5px';
                    reset_tag.style.color = '#999999';
                    reset_tag.style.visibility = 'hidden';
                    reset_tag.innerText = 'reset';
                    reset_tag.onclick = function () {
                        sampling_svg.selectAll("circle")
                            .style("fill", "#cccccc");
                        sampling_svg.transition().duration(500).call(
                            sampling_zoomer.transform,
                            d3.zoomIdentity,
                            d3.zoomTransform(sampling_svg.node()).invert([svgWidth / 2, svgHeight / 2])
                        );
                    };
                    // sampling_div.appendChild(reset_tag);

                    //添加稀有结构选择
                    var minotype_text = document.createElement('span');
                    minotype_text.style.color = '#999999';
                    minotype_text.style.position = 'absolute';
                    minotype_text.style.bottom = '2.8%';
                    minotype_text.style.left = '11%';
                    minotype_text.style.fontSize = '18px';
                    minotype_text.innerText = 'Minority Structure:';
                    sampling_div.appendChild(minotype_text);
                    var minotype_button = document.createElement('div');
                    minotype_button.style.overflow = 'hidden';
                    minotype_button.style.position = 'absolute';
                    minotype_button.style.bottom = '3%';
                    minotype_button.style.left = '33%';
                    minotype_button.style.width = '60%';
                    minotype_button.style.right = '10%';
                    var minotypeList = ['Super Pivot', 'Huge Star', 'Rim', 'Tie'];
                    minotypeList.forEach(function (obj, index) {
                        var input = document.createElement('input');
                        input.className = obj.replace("Super ", "").replace("Huge ", "");
                        input.type = 'checkbox';
                        input.style.margin = '0px 5px 0 11px';
                        input.name = 'category';
                        input.value = obj;
                        input.onclick = function () {
                            let linear = d3.scaleLinear().domain([0, self.anomaly_total[obj].length]).range([0, 1]);
                            let compute = d3.interpolate('red', 'white');
                            self.rim_anomaly_total[current_algorithm].forEach(function (item, index) {
                                
                                sampling_svg.selectAll("circle.id_" + item).style("fill", "rgb(123,187,109)");
                                
                            })
                        };
                        var input_span = document.createElement('span');
                        input_span.style.color = "#999999"
                        input_span.innerText = obj;
                        minotype_button.appendChild(input);
                        minotype_button.appendChild(input_span)
                    });
                    sampling_div.appendChild(minotype_button);

                    // sampling_div.onmouseenter = function () {
                    //     sampling_div.style.borderColor = '#cccccc';
                    // reset_tag.style.visibility = "visible";
                    // close_tag.style.visibility = 'visible';
                    // };
                    // sampling_div.onmouseleave = function () {
                    //     sampling_div.style.borderColor = '#FFFFFF';
                    // reset_tag.style.visibility = "hidden";
                    // close_tag.style.visibility = 'hidden';
                    // };

                    self.queue_num += 1;
                    self.right_num = 2;
                    self.LoadingSampling = false;


                    //添加鱼眼效果
                    sampling_svg.on("mousemove", function () {
                        if (sampling_div.getAttribute("open-fisheye") === "true") {
                            var fisheye = d3_fisheye.circular()
                                .radius(svgWidth / 5);
                            fisheye.focus(d3.mouse(this));
                            node.each(function (d) {
                                d.fisheye = fisheye(d);
                            })
                                .attr("cx", function (d) {
                                    return d.fisheye.x;
                                })
                                .attr("cy", function (d) {
                                    return d.fisheye.y;
                                })
                                .attr("r", function (d) {
                                    return d.fisheye.z * d.r * 1.7;
                                });

                            link.attr("x1", function (d) {
                                return data.nodes[d.source].fisheye.x
                            })
                                .attr("y1", function (d) {
                                    return data.nodes[d.source].fisheye.y
                                })
                                .attr("x2", function (d) {
                                    return data.nodes[d.target].fisheye.x
                                })
                                .attr("y2", function (d) {
                                    return data.nodes[d.target].fisheye.y
                                });
                        }
                    });
                });
                
            },
            //左右浏览切换
            switch_view(director) {
                var queue_List = document.querySelectorAll(".sampling-item");
                var unit = this.queue_num === 4 ? 2 : 1;
                if (director === 'left') {
                    //左移
                    this.left_num -= unit;
                    this.right_num -= unit;
                    queue_List.forEach(function (obj, index) {
                        var new_left = parseInt(obj.style.left.replace("%", "")) + 50 * unit;
                        obj.style.left = new_left + "%";
                    });
                } else if (director === 'right' && this.queue_num > 2) {
                    //右移
                    this.left_num += unit;
                    this.right_num += unit;
                    queue_List.forEach(function (obj, index) {
                        var new_left = parseInt(obj.style.left.replace("%", "")) - 50 * unit;
                        obj.style.left = new_left + "%";
                    });
                }

            },
        },
        computed: {
            get_option_labels: function () {
                if (this.algorithm_value !== '') {
                    return this.algorithm_list[this.algorithm_value]['options']
                } else {
                    return []
                }
            },
            //svg格式
            originGraphPath: function () {
                return "/static/GraphData_Origin/origin_" + this.Graph_Data_Set_value + '.svg';
            },
            newSamplingPath: function () {
                return "/static/sampling_result/new_sampling.svg";
            },
            origin_fisheye_file: function () {
                return "/static/graph_set/json/{graph1}/origin_cspan.json".format({
                    graph1: this.Graph_Data_Set_value,
                })
            },
            samping_fisheye_file: function () {
                if (this.algorithm_value === "MCGS") {
                    return "/static/graph_set/json/{graph1}/our_{rate}_{alpha}_{beta}_".format({
                        graph1: this.Graph_Data_Set_value,
                        rate: this.option_settings.rate,
                        alpha: this.option_settings.alpha,
                        beta: this.option_settings.beta
                    }) + this.option_settings["loss weight"][0] + this.option_settings["loss weight"][2] + this.option_settings["loss weight"][4] + ".json"
                } else if (this.algorithm_value === "FF") {
                    return "/static/graph_set/json/{graph1}/{algorithm}_{rate}_{seed}.json".format({
                        graph1: this.Graph_Data_Set_value,
                        algorithm: this.algorithm_value,
                        rate: this.option_settings.rate,
                        seed: this.option_settings.seed
                    })
                } else {
                    return "/static/graph_set/json/{graph1}/{algorithm}_{rate}.json".format({
                        graph1: this.Graph_Data_Set_value,
                        algorithm: this.algorithm_value,
                        rate: this.option_settings.rate
                    })
                }
            }
        }
    }
</script>

<!--复选框颜色-->
<style>
    input.Pivot[type=checkbox]::after {
        background-color: rgb(166, 126, 177);
        color: #000;
        width: 15px;
        height: 15px;
        display: inline-block;
        visibility: visible;
        padding-left: 0;
        text-align: center;
        content: ' ';
        border-radius: 3px
    }

    input.Star[type=checkbox]::after {
        background-color: rgb(227, 136, 74);
        color: #000;
        width: 15px;
        height: 15px;
        display: inline-block;
        visibility: visible;
        padding-left: 0;
        text-align: center;
        content: ' ';
        border-radius: 3px
    }

    input.Rim[type=checkbox]::after {
        background-color: rgb(123, 187, 109);
        color: #000;
        width: 15px;
        height: 15px;
        display: inline-block;
        visibility: visible;
        padding-left: 0;
        text-align: center;
        content: ' ';
        border-radius: 3px
    }

    input.Tie[type=checkbox]::after {
        background-color: rgb(63, 141, 183);
        color: #000;
        width: 15px;
        height: 15px;
        display: inline-block;
        visibility: visible;
        padding-left: 0;
        text-align: center;
        content: ' ';
        border-radius: 3px
    }

    input[type=checkbox]:checked::after {
        content: "✓";
        font-size: 12px;
        /*font-weight: bold;*/
        color: white;
        /*color: #b3d8ff;*/
    }

</style>


<!--标签提示框-->
<style scoped>
    .tooltip {
        position: absolute;
        padding: 5px;
        height: auto;
        font-size: 14px;
        color: black;
        background-color: rgb(255, 255, 255);
        border-width: 2px;
        border-radius: 5px;
        z-index: 2000;
    }
</style>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .content {
        width: 100%;
        text-align: center;
    }

    /*上方控制栏*/
    .control-bar {
        width: 96.5%;
        border: 1px solid #CCCCCC;
        height: 60px;
        line-height: 60px;
        margin: 0 auto;
        margin-top: 15px;
        overflow: hidden;
        cursor: default;
        position: relative;
        padding: 0 20px;
        box-sizing: border-box;
    }

    /*单个设置框*/
    .control-bar .settings-item {
        float: left;
        overflow: hidden;
        margin: 0 1.5% 0 0;
    }

    /*设置标题*/
    .control-bar .settings-item .setting-name {
        float: left;
        color: #999999;
        font-weight: bold;
    }

    /*设置值*/
    .control-bar .settings-item .setting-value {
        float: left;
        color: #999999;
        margin-left: 10px;
    }

    .control-bar .settings-item .setting-value .option_input {
        width: 45px;
        height: 20px;
        line-height: 20px;
        margin: 5px;
        color: #999999;
        border-bottom: #999999 1px solid;
        border-left: none;
        border-right: none;
        border-top: none;
        text-align: center;
    }

    .control-bar .settings-item .setting-value .other_options {
        float: right;
        overflow: hidden;
    }

    .control-bar .settings-item .setting-value .other_options .option_item {
        float: left;
    }

    #upload_tag {
        color: #999999;
        margin: 0 10px;
    }

    .button {
        height: 35px;
        line-height: 50px;
        font-size: 16px;
        color: #666666;
        cursor: pointer;
    }

    #run-btn {
        position: absolute;
        width: 5.5%;
        height: 35px;
        line-height: 50px;
        font-size: 16px;
        color: #666666;
        top: 12.5px;
        right: 20px;
        cursor: pointer;
    }

    .graph-container {
        margin: 0 auto;
        width: 96.5%;
        padding-top: 1%;
        cursor: default;
    }

    .graph-box {
        box-sizing: border-box;
        position: relative;
    }

    .origin-graph {
        position: relative;
        width: 32%;
        float: left;
        padding: 0.2%;
        box-sizing: border-box;
        border: 1px solid #cccccc;
        margin-bottom: 2%;
        overflow: hidden;
    }

    #origin-tag {
        position: absolute;
        top: 1%;
        left: 2.1%;
        color: #999999;
        z-index: 1000;
    }

    #origin-info-tag {
        position: absolute;
        top: 45%;
        left: 25%;
        color: #999999;
        z-index: 1000;
    }

    .origin-graph .origin-item {
        width: 100%;
        height: 96%;
        margin-top: 4.5%;
        background: white;
    }

    .minotype_select_container {
        overflow: hidden;
        position: absolute;
        bottom: 3%;
        left: 28%;
        width: 60%;
        right: 10%;
    }

    .loading-div-origin {
        width: 100%;
        height: 100%;
        margin-top: 4.5%;
        z-index: 2000;
    }

    .sampling-graph {
        position: relative;
        width: 67%;
        float: right;
        padding: 0.2%;
        box-sizing: border-box;
        border: 1px solid #cccccc;
        margin-bottom: 2%;
        overflow: hidden;
    }

    .sampling-item, .loading-div {
        left: 1%;
        float: left;
        position: absolute;
        top: 4%;
        width: 48%;
        height: 95%;
    }

    #sampling-tag {
        position: absolute;
        top: 1%;
        left: 1%;
        color: #999999;
        z-index: 1000;
    }

    /*关闭采样图按钮*/
    .sampling-close-btn {
        position: absolute;
        right: 1%;
        top: 1%;
        cursor: pointer;
    }


    /*左右切换按钮*/
    .prev-sampling {
        margin: 0 10px;
        width: 50px;
        position: absolute;
        left: 2%;
        top: 50%;
        z-index: 1000;
        background-color: white;
    }

    .next-sampling {
        margin: 0 10px;
        width: 50px;
        position: absolute;
        right: 2%;
        top: 50%;
        z-index: 1000;

    }


</style>
