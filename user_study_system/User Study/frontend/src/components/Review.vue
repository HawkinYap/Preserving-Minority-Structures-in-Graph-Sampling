<template>
    <div>
        <div class="header">
            <span><a href="/"><i class="el-icon-share"></i> Open-End Graph Exploration - Result Reviewing Mode for Participants</a></span>
        </div>

        <div class="content">
            <el-container>
                <div id="aside">
                    <el-scrollbar style="height: 100%;border: 2px solid #cccccc;">
                        <div class="img-thumbnail-container" :class="{ selected: index===current_index }"
                             v-for="(item,index) in images" :key="index" @click="switchImg(item,index)">
                            <div style="margin-top: 10px">
                                
                                <img class="img-main" src="" data-src=""/>
                                <p class="img-name">Graph Data Set {{index + 1}}</p>

                            </div>
                        </div>
                    </el-scrollbar>
                </div>
                <div id="main">
                    <div class="graph-container"
                         v-loading="isLoading">

                    </div>
                </div>
            </el-container>
        </div>
    </div>
</template>

<script>
    import * as d3 from "d3"
    import axios from '../utils/axios'
    import cookie_manager from "../utils/cookie_manager";

    export default {
        name: 'Review',
        props: {},
        data() {
            return {
                current_index: 0,
                images: [],
                svg_cache: {},
                isLoading: true,
                
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
                axios.get("/getSvgRecordList/", {
                    params: {'current_user': cookie_manager.getCookie("current_user")},
                })
                    .then(res => {
                        this.images = res.data.img_list;
                        this.images.forEach((item, index) => {
                            this.setImgSrc(item, index);
                        });
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
                d3.xml(_this.svg_cache[image_name]).then(function (xml) {
                    d3.select(".graph-container svg").remove();
                    document.querySelector(".graph-container").appendChild(xml.documentElement);
                    _this.svg = d3.select(".graph-container svg");
                    // 进行缩放
                    let svgWidth = _this.svg.attr("width").replace("px","");
                    let svgHeight = _this.svg.attr("height").replace("px","");
                    let margin = {left: 20, right: 20, top: 20, bottom: 20};
                    let scaleNumber = d3.min([(_this.width - margin.left - margin.right) / svgWidth, (_this.height - margin.top - margin.bottom) / svgHeight]);
                    _this.svgWidth = svgWidth * scaleNumber;
                    _this.svgHeight = svgHeight * scaleNumber;
                    _this.svg.attr("width", _this.svgWidth)
                        .attr("height", _this.svgHeight)
                        .style("margin", (_this.height - _this.svgHeight) / 2 + "px auto");
                    //隐藏标注顺序
                    //d3.select("g.rectangles").selectAll("text").nodes().forEach(d => {
                    //    d3.select(d).attr("fill-opacity", 0)
                    //});
                    //隐藏选框
                    // d3.select("g.rectangles").selectAll("rect").nodes().forEach(d => {
                    //     d3.select(d).style("stroke", null);
                    // });
                    _this.isLoading = false;
                });
            },
            //用于设置侧边栏预览列表的图片略缩图
            setImgSrc(image_name, index) {
                axios.get("/getSvgUserImage/", {
                    params: {'image_name': image_name, 'current_user': cookie_manager.getCookie("current_user")},
                    responseType: "arraybuffer"
                }).then(res => {
                    return 'data:image/svg+xml;base64,' + btoa(
                        new Uint8Array(res.data).reduce((data, byte) => data + String.fromCharCode(byte), '')
                    );
                }).then(data => {
                    this.svg_cache[image_name] = data;
                    if (index === 0) {
                        this.loadSvg(image_name);
                    }
                    document.getElementsByClassName("img-main")[index].setAttribute("src", data);
                    // this.img_urls[index] = data;
                }).catch(error => {
                    console.log(error);
                });
            },
            switchImg(image_name, index) {
                this.isLoading = true;
                this.current_index = index;
                this.loadSvg(image_name);
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
