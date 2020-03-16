<template>
    <div class="body">
        <div class="header">
            <span><a href="/"><i class="el-icon-share"></i> Open-End Graph Exploration - Free Exploration Mode</a></span>
        </div>
        <div class="content">
            <div class="progress-container">
                <el-progress :percentage="percent" color="#999999" :stroke-width="stroke_width"></el-progress>
            </div>
            <p id="second">{{second}}{{typeof second === "string"?"":"s"}}{{stop===true?" - Pause":""}}</p>
            <div class="graph-container my_loading"
                 v-loading="stop"
                 element-loading-text="Pause"
                 element-loading-spinner="none"
                 element-loading-background="rgba(255, 255, 255, 0.3)"
            ></div>
            <div class="control-container">
                <div class="button-container">
                    <input type="button" id="redo" class="button" :disabled="redo_disabled" value="Redo" @click="redo">
                    <input type="button" id="submit" class="button" value="Submit" :disabled="submit_disabled"
                           @click="submit">
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import * as d3 from "d3"
    import axios from '../utils/axios'
    import cookie_manager from "../utils/cookie_manager";

    export default {
        name: 'NodeLinkGraph',
        props: {},
        data() {
            return {
                stroke_width: 8,
                initSecond: 60,
                images: [],
                current: 0,
                width: null,
                height: null,
                svg: null,
                svgWidth: null,
                svgHeight: null,
                second: 60,
                interval: null,
                percentage: 0,
                rectangleInfos: [],
                rectIndex: 1,
                stop: false,
                isSelectNodes: false,
                isSubmiting: false
            }
        },
        mounted() {
            document.onkeydown = () => {
                if (window.event.keyCode === 32) {
                    this.stop_switch();
                }
            };
            this.$nextTick(() => {
                document.querySelector("div.el-progress__text").style.fontSize = "20px";
                this.setContainerSize();
                this.initImages();
            })
        },
        methods: {
            initImages() {
                axios.get("/getExpeSvgList/")
                    .then(res => {
                        // this.images = res.data.img_list;
                        this.images = ['cond_mat6_5.svg','formal_us-air2_26.svg']
                        this.second = 'Loading...';
                        this.loadSvg();
                    }).catch(error => {
                        console.log(error)
                    }
                );
            },
            setContainerSize() {
                let screenWidth = document.documentElement.clientWidth || document.body.clientWidth;
                let screenHeight = document.documentElement.clientHeight || document.body.clientHeight;
                document.querySelector(".graph-container").style.height = screenHeight * 0.68 + "px";
            },
            initInterval() {
                this.second = this.initSecond;
                this.interval = setInterval(() => {
                    if (this.second <= 0) {
                        // this.submit();
                        return;
                    }
                    this.second -= 1;
                }, 1000)
            },
            getSize() {
                let parentNode = document.querySelector(".graph-container");
                this.width = parentNode.clientWidth;
                this.height = parentNode.clientHeight;
                document.querySelector("div.el-progress__text").style.fontSize = "20px";
            },
            loadSvg() {
                let _this = this;
                this.getSize();
                d3.xml(_this.imagePath).then(function (xml) {
                    _this.rectIndex = 1;
                    document.querySelector(".graph-container").appendChild(xml.documentElement);
                    _this.svg = d3.select(".graph-container svg");
                    let svgWidth = _this.svg.attr("width").replace("px","");
                    let svgHeight = _this.svg.attr("height").replace("px","");
                    let margin = {left: 20, right: 20, top: 20, bottom: 20};
                    let scaleNumber = d3.min([(_this.width - margin.left - margin.right) / svgWidth, (_this.height - margin.top - margin.bottom) / svgHeight]);
                    _this.svgWidth = svgWidth * scaleNumber;
                    _this.svgHeight = svgHeight * scaleNumber;
                    _this.svg.attr("width", _this.svgWidth)
                        .attr("height", _this.svgHeight)
                        .style("position", "absolute")
                        .style("left", (_this.width - _this.svgWidth) / 2 + "px")
                        .style("top", (_this.height - _this.svgHeight) / 2 + "px");
                    _this.initInterval();
                    // document.querySelector("#second").style.visibility = "visible";
                    document.onkeydown = () => {
                        if (window.event.keyCode === 32) {
                            _this.stop_switch();
                        }
                    };
                    _this.isSubmiting = false;
                    _this.drawRectangle();
                });
            },
            drawRectangle() {
                /**
                 * 框选数据
                 */
                let brush = d3.brush().on("end", brushended);
                this.svg.append("g")
                    .attr("class", "brush")
                    .call(brush);

                this.svg.append("g")
                    .attr("class", "rectangles");
                let _this = this;

                function brushended() {
                    var s = d3.event.selection;
                    let timeFormat = d3.timeFormat("%Y-%m-%d %H:%M:%S");
                    if (s) {
                        _this.isSelectNodes = false;
                        //给节点标记颜色，同时判断是否框选节点
                        d3.selectAll("circle").nodes().forEach(d => {
                            let circle = d3.select(d);
                            let x = parseFloat(circle.attr("cx"));
                            let y = parseFloat(circle.attr("cy"));
                            if (x > s[0][0] && x < s[1][0] && y > s[0][1] && y < s[1][1]) {
                                circle.style("fill", "#f00");
                                _this.isSelectNodes = true;
                            }
                        });
                        if (_this.isSelectNodes === true) {
                            //绘制选框
                            d3.select("g.rectangles").append("rect")
                                .attr("x", s[0][0])
                                .attr("y", s[0][1])
                                .attr("width", s[1][0] - s[0][0])
                                .attr("height", s[1][1] - s[0][1])
                                .style("fill", "#fff")
                                .style("fill-opacity", 0)
                                .style("stroke", "#f00")
                             .style("stroke-width", "5px");

                            //标注顺序
                            var fontsize = parseInt(d3.select("circle").attr("r"));
                            var font_scale = fontsize >= 30 ? 8 : 10;
                            d3.select("g.rectangles").append("text")
                                .attr("fill-opacity", 0) //用户端设置为隐藏
                                .attr("x", s[1][0])
                                .attr("y", s[0][1])
                                .attr("font-size", fontsize * font_scale)
                                .attr("fill", "#f00")
                                .attr("font-family", "Arial")
                                .text(_this.rectIndex);
                            _this.rectIndex += 1;

                            _this.rectangleInfos.push({
                                timestamp: new Date().getTime(),
                                img: _this.imageName,
                                x1: s[0][0],
                                y1: s[0][1],
                                x2: s[1][0],
                                y2: s[1][1]
                            });
                        }
                    }
                }
            },
            submit() {
                let timeFormat = d3.timeFormat("%Y-%m-%d %H:%M:%S");
                this.isSubmiting = true;
                axios.post("/saveRecord/", {
                    current_user: cookie_manager.getCookie("current_user"),
                    create_time: timeFormat(new Date()),
                    img: this.imageName,
                    consuming_time: this.consuming_time,
                    rectangleInfos: this.rectangleInfos,
                }).then(response => {
                    this.rectangleInfos = [];
                    if (response.data.state === "success") {
                        //然后再保存用户图源
                        this.save_svg();
                    } else {
                        console.log("fail");
                    }
                });

            },
            redo() {
                // 删除标注
                let texts = d3.select(".graph-container .rectangles").selectAll("text").nodes();
                d3.select(texts[texts.length - 1]).remove();
                this.rectIndex = this.rectIndex >= 2 ? this.rectIndex - 1 : 1;

                //删除选框
                let rects = d3.select(".graph-container .rectangles").selectAll("rect").nodes();
                d3.select(rects[rects.length - 1]).remove();
                d3.select(".graph-container .brush").remove();
                if (this.rectangleInfos.length > 0) {
                    let rectangle = this.rectangleInfos[this.rectangleInfos.length - 1];
                    this.rectangleInfos.splice(this.rectangleInfos.length - 1, 1);
                    d3.selectAll("circle").nodes().forEach(d => {
                        let circle = d3.select(d);
                        let x = parseFloat(circle.attr("cx"));
                        let y = parseFloat(circle.attr("cy"));
                        if (x > rectangle.x1 && x < rectangle.x2 && y > rectangle.y1 && y < rectangle.y2) {
                            circle.style("fill", "rgb(192,192,192)");
                        }
                    })
                }
                this.drawRectangle();
            },
            save_svg() {
                d3.select("g.rectangles").selectAll("text").nodes().forEach(d => {
                    d3.select(d).attr("fill-opacity", 1) //服务器端设置为显示
                });
                d3.select("g.brush").remove();//清除刷子阴影布局
                var svg = d3.select("svg").nodes()[0];
                var serializer = new XMLSerializer();
                var source = serializer.serializeToString(svg);
                d3.select("g.rectangles").selectAll("text").nodes().forEach(d => {
                    d3.select(d).attr("fill-opacity", 0) //客户端设置为隐藏
                });
                var img_file_name = this.imageName.slice(0, this.imageName.length - 4) + "_" + new Date().getTime() + ".svg";
                axios.post("/receiveSvg/", {
                    current_user: cookie_manager.getCookie("current_user"),
                    svg_code: source,
                    img_name: this.imageName
                }, {
                    maxContentLength: Infinity
                }).then(response => {
                    this.rectangleInfos = [];
                    this.$message({
                        message: 'Submit successfully!',
                        type: 'success',
                        duration: '800'
                    });
                    //清除倒计时
                    clearInterval(this.interval);
                    this.percentage += (100 / this.images.length);
                    if (this.percentage >= 100 || this.current >= this.images.length - 1) {
                        this.percentage = 99;
                        //取消快捷键
                        document.onkeydown = () => {
                            if (window.event.keyCode === 32) {

                            }
                        };
                        setTimeout(() => {
                            this.$router.push({name: 'home', params: {msg: 'expertment'}});
                        }, 1000);
                    } else {
                        this.current += 1;
                        this.isSubmiting = false;
                        d3.select(".graph-container").selectAll("svg").remove();
                        // document.querySelector("#second").style.visibility = "hidden";
                        this.second = 'Loading...';
                        //取消注册
                        document.onkeydown = () => {
                            if (window.event.keyCode === 32) {

                            }
                        };
                        setTimeout(() => {
                            this.loadSvg();
                        }, 1200)
                    }
                }).catch(error => {
                    console.log(error)
                })
            },
            stop_switch() {
                if (this.stop === true) {
                    this.interval = setInterval(() => {
                        if (this.second <= 1) {
                            // this.submit();
                            return;
                        }
                        this.second -= 1;
                    }, 1000);
                    this.stop = false;
                } else {
                    this.stop = true;
                    clearInterval(this.interval)
                }
            }
        },
        computed: {
            redo_disabled: function () {
                return this.rectangleInfos.length <= 0 || this.stop === true || this.isSubmiting === true;
            },
            submit_disabled: function () {
                return this.stop === true || this.rectangleInfos.length <= 0 || this.isSubmiting === true;
            },
            imagePath: function () {
                return "/static/images/formal/" + this.images[this.current];
            },
            imageName: function () {
                let arr = this.imagePath.split("/");
                return arr[arr.length - 1];
            },
            percent: function () {
                if (this.percentage >= 100) {
                    return 100;
                } else {
                    return Math.floor(this.percentage);
                }
            },
            consuming_time: function () {
                return this.initSecond - this.second;
            }
        }
    }
</script>
<style>
    .my_loading .el-loading-spinner .el-loading-text {
        color: #666666;
        font-size: 35px;
        cursor: default;
    }

    .progress-container .el-progress__text {
        cursor: default;
        color: #999999;
        line-height: 10px;
        height: 10px;
    }
</style>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .body, .content {
        width: 100%;
    }

    .progress-container {
        text-align: center;
    }

    #second {
        position: absolute;
        left: 5%;
        top: 12%;
        font-size: 30px;
        font-weight: bold;
        color: #cccccc;
        cursor: default;
    }

    .graph-container {
        width: 62%;
        height: 720px;
        margin: 3% auto;
        border: 1px solid #999999;
        position: relative;
    }

    .button-container {
        width: 500px;
        margin: 0 auto;
        text-align: center;
    }

    .button {
        width: 120px;
        height: 50px;
        font-size: 20px;
        margin-bottom: 20px;
    }

    #redo {
        float: left;
    }

    #submit {
        float: right;
    }
</style>
