<template>
    <div>
        <div class="header">
<!--            <span><a href="/"><i class="el-icon-share"></i> Open-End Graph Exploration - Result Reviewing by Heat Map</a></span>-->
            <span><a href="/"><i class="el-icon-share"></i> Open-End Graph Exploration - Result Reviewing Mode for Instructors</a></span>
        </div>

        <div class="content">
            <el-container>
                <div id="aside">
                    <el-scrollbar style="height: 100%;border: 2px solid #cccccc;">
                        <div class="img-thumbnail-container" :class="{ selected: index===current_index }"
                             v-for="(item,index) in images" :key="index" @click="switchImg(item,index)">
<!--                            <div style="float: left">-->
<!--                                <span style="font-size: 20px;cursor: default; color: #cccccc;font-weight: bold">{{index+1}}</span>-->
<!--                            </div>-->
                            <div style="margin-top: 10px">
                                <img class="img-main" :src="imagePath(item)"/>
                                <p class="img-name">{{item}}</p>
                            </div>
                        </div>
                    </el-scrollbar>
                </div>
                <div id="main">
                    <div class="graph-container">

                    </div>
                </div>
            </el-container>
        </div>
    </div>
</template>

<script>
    import * as d3 from "d3"
    import * as h337 from "heatmap.js"
    import axios from '../utils/axios'

    export default {
        name: 'Heatmap',
        props: {},
        data() {
            return {
                current_index: 0,
                images: [],
                svg_cache: {}
            }
        },
        mounted() {
            this.$nextTick(() => {
                let screenWidth = document.documentElement.clientWidth || document.body.clientWidth;
                let screenHeight = document.documentElement.clientHeight || document.body.clientHeight;
                document.querySelector("#aside").style.height = screenHeight * 0.80 + "px";
                document.querySelector("#aside").style.width = screenWidth * 0.30 + "px";
                document.querySelector("#main").style.height = screenHeight * 0.80 + "px";
                document.querySelector("#main").style.width = screenWidth * 0.65 + "px";
                document.querySelector(".graph-container").style.height = screenHeight * 0.80 + "px";
                this.initImages();
                this.getSize();
            })
        },
        methods: {
            initImages() {
                axios.get("/getAllImages/")
                    .then(res => {
                        // this.images = res.data.img_list;
                        this.images = ['cond_mat6_5.svg','formal_us-air2_26.svg']
                        this.loadSvg(this.images[0]);
                    })
                    .catch(error => {
                            console.log(error)
                        }
                    );
            },
            setContainerSize() {
                let screenWidth = document.documentElement.clientWidth || document.body.clientWidth;
                let screenHeight = document.documentElement.clientHeight || document.body.clientHeight;
                document.querySelector(".graph-container").style.height = screenHeight * 0.80 + "px";
            },
            getSize() {
                let parentNode = document.querySelector(".graph-container");
                this.width = parentNode.clientWidth;
                this.height = parentNode.clientHeight;
            },
            //用于加载右边栏图片大图
            loadSvg(image_name) {
                let _this = this;
                d3.xml(_this.imagePath(image_name)).then(function (xml) {
                    d3.select(".graph-container svg").remove();
                    document.querySelector(".graph-container").appendChild(xml.documentElement);
                    _this.svg = d3.select(".graph-container svg");
                    // 进行缩放
                    let svgWidth = _this.svg.attr("width").replace("px","");;
                    let svgHeight = _this.svg.attr("height").replace("px","");;
                    let margin = {left: 20, right: 20, top: 20, bottom: 20};
                    let scaleNumber = d3.min([(_this.width - margin.left - margin.right) / svgWidth, (_this.height - margin.top - margin.bottom) / svgHeight]);
                    _this.svgWidth = svgWidth * scaleNumber;
                    _this.svgHeight = svgHeight * scaleNumber;
                    _this.svg.attr("width", _this.svgWidth)
                        .attr("height", _this.svgHeight)
                        .style("margin", (_this.height - _this.svgHeight) / 2 + "px auto");
                    //创建热力图布局
                    _this.createHeatmap();
                });
            },
            createHeatmap() {
                d3.select("#heatmap").remove();
                let heatmapDiv = document.createElement("div");
                heatmapDiv.id = "heatmap";
                document.querySelector(".graph-container").appendChild(heatmapDiv);
                var margin_top = ((this.height - this.svgHeight) / 2 + this.svgHeight)*1.007;
                d3.select("#heatmap")
                    .style("width", this.svgWidth + "px")
                    .style("height", this.svgHeight + "px")
                    .style("margin", -margin_top + "px auto") //调整位置偏移
                    .style("fill", 'red');

                axios.post("/readRects/", {img_name: this.images[this.current_index]})
                    .then(response => {
                        let responseData = response.data;
                        let map = new Map();
                        let points = [];
                        let viewBox = this.svg.attr("viewBox");
                        let viewBoxArr = viewBox.split(" ");
                        let radius = 10;
                        let xScale = d3.scaleLinear()
                            .domain([parseFloat(viewBoxArr[0]), parseFloat(viewBoxArr[0]) + parseFloat(viewBoxArr[2])])
                            .range([0, this.svgWidth]);
                        let yScale = d3.scaleLinear()
                            .domain([parseFloat(viewBoxArr[1]), parseFloat(viewBoxArr[1]) + parseFloat(viewBoxArr[3])])
                            .range([0, this.svgHeight]);

                        responseData.datum.forEach(d => {
                            d3.selectAll("circle").nodes().forEach(c => {
                                let circle = d3.select(c);
                                let x = parseFloat(circle.attr("cx"));
                                let y = parseFloat(circle.attr("cy"));
                                radius = parseInt(circle.attr("r")) * 1.5;
                                if (x > d.x1 && x < d.x2 && y > d.y1 && y < d.y2) {
                                    let position = map.get(x + ',' + y);
                                    if (position === undefined) {
                                        map.set(x + ',' + y, 1);
                                    } else {
                                        map.set(x + ',' + y, position + 1)
                                    }
                                }
                            })
                        });

                        for (let [key, value] of map.entries()) {
                            let arr = key.split(",");
                            points.push({
                                x: parseInt(xScale(parseFloat(arr[0]))),
                                y: parseInt(yScale(parseFloat(arr[1]))),
                                value: value
                            });
                        }

                        let heatmapInstance = h337.create({
                            container: document.querySelector('#heatmap'),
                            maxOpacity: 0.6,
                            minOpacity: 0,
                            radius: 25,
                            gradient: {
                                0.25: "#7B68EE",
                                0.33: "#1E90FF",
                                0.66: "#54FF9F",
                                1.0: "#FFA500"

                                // 0:'#5d9baa',
                                // 0.5:'#f3dfc1',
                                // 1:'#edd2a5'

                            }

                        });

                        let max = d3.max(points.map(d => d.value));

                        heatmapInstance.setData({
                            max: max,
                            data: points
                        });
                        this.downLoadCanvas()
                    })
            },
            switchImg(image_name, index) {
                this.current_index = index;
                this.loadSvg(image_name);
            },
            imagePath: function (item) {
                return "/static/images/formal/" + item;
            },
            //下载热力图canvas
            downLoadCanvas: function () {
                var imgdata = document.querySelector("canvas").toDataURL('png');
                imgdata = imgdata.replace('image/png', 'image/octet-stream');
                var saveFile = function (data, filename) {
                    var link = document.createElement('a');
                    link.href = data;
                    link.download = filename;
                    var event = document.createEvent('MouseEvents');
                    event.initMouseEvent('click', true, false, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
                    link.dispatchEvent(event);
                }
                var filename = this.images[this.current_index].replace('.svg', '') + '_canvas.png';
                saveFile(imgdata, filename);
            }
        },
        computed: {}
    }
</script>

<!--用于除去滚动栏x轴方向的滚动-->
<style>
    .el-scrollbar__wrap {
        overflow-x: hidden;
    }
</style>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .content {
        width: 75%;
        margin: 2% auto;
        text-align: center;
    }

    .img-thumbnail-container {
        overflow: hidden;
        margin: 3% 6%;
        padding: 5px;
        border: 2px solid #cccccc;
    }

    .img-thumbnail-container:hover {
        border: 2px solid #999999;
    }

    .selected {
        border: 2px solid #999999;
    }

    .img-main {
        width: 87%;
    }

    .img-name {
        margin: 5px auto;
        color: #666666;
        cursor: default;
    }

    #main {
        border: 2px solid #d7dae2;
        border-radius: 2px;
        margin-left: 1%;
    }
</style>
