<template>
    <div>
        <div class="header">
            <span><a href="/"><i class="el-icon-share"></i> Graph Sampling Evaluation System</a></span>
        </div>
        <div class="content">
            <div class="progress-container">
                <el-progress :percentage="percent" color="#999999" :stroke-width="stroke_width"></el-progress>
            </div>
            <div class="graph-container">
                <div class="graph-box origin-graph" v-loading="loading_origin">
                    <img id="origin-img" :src="originImgPath"
                         style=" position: absolute;height: 50%;top: 25%;margin-top:-4%;"
                         alt="please wait..." width="90%">
                    
                    <p id="origin-tip">{{this.graphs[this.current]}}</p>
                </div>
                <div class="graph-box sampling-graph">
                    <span class="sampling-tip">Please rate on the following graph samples</span>

                    <div class="select-item" v-loading="loading_sampling"
                         v-for="(item,index) in algorithm_list" :key="index"
                         :class="{'select-item-completed':isCompleteList[index],'my_padding':graphs[current]==='fb107'}"
                         @mouseenter="enter(index)" @mouseleave="leave">
                        
                        <span class="index">{{item.algorithm}}</span>
                        <img class="img_item" :src="samplingImgPath(item.algorithm)" alt="please wait..." width="100%"
                             height="100%">
                        <div class="complete-opacity-background" v-show="index !== hoverIndex && isCompleteList[index]">
                        </div>

                        <div class="opacity-background" v-show="index === hoverIndex">
                        </div>

                        <div class="rate-container" v-show="index === hoverIndex">
                            <div class="rate-div-item" v-show="step === 1">
                                <div class="my_rate">
                                    <span class="term">Community Cluster</span>
                                    <el-rate :disabled="isCompleteList[index]" class="rate" void-color="#ffffff"
                                             v-model="result_list[index].community_cluster"
                                             @change="submit(index,item.algorithm)"></el-rate>
                                </div>
                                <div class="my_rate">
                                    <span class="term">Graph Similarity</span>
                                    <el-rate :disabled="isCompleteList[index]" class="rate" void-color="#ffffff"
                                             v-model="result_list[index].graph_similarity"
                                             @change="submit(index,item.algorithm)"></el-rate>
                                </div>
                                <div class="my_rate">
                                    <span class="term">Connectivity</span>
                                    <el-rate :disabled="isCompleteList[index]" class="rate" void-color="#ffffff"
                                             v-model="result_list[index].connectivity"
                                             @change="submit(index,item.algorithm)"></el-rate>
                                </div>
                            </div>
                            <div class="rate-div-item" v-show="step === 2">
                                <div class="my_rate">
                                    <span class="term">High Degree Nodes</span>
                                    <el-rate :disabled="isCompleteList[index]" class="rate" void-color="#ffffff"
                                             v-model="result_list[index].high_degree_nodes"
                                             @change="submit(index,item.algorithm)"></el-rate>
                                </div>
                                <div class="my_rate">
                                    <span class="term">Margin Structures</span>
                                    <el-rate :disabled="isCompleteList[index]" class="rate" void-color="#ffffff"
                                             v-model="result_list[index].margin_nodes"
                                             @change="submit(index,item.algorithm)"></el-rate>
                                </div>
                                <div class="my_rate">
                                    <span class="term">Boundary Structures</span>
                                    <el-rate :disabled="isCompleteList[index]" class="rate" void-color="#ffffff"
                                             v-model="result_list[index].boundary_nodes"
                                             @change="submit(index,item.algorithm)"></el-rate>
                                </div>
                            </div>
                            
                            <span class="arrow left-arrow" @click="change_step('left')"
                                  :class="{ arrow_disabled: left_is_disabled}">‹</span>
                            <span class="arrow right-arrow" @click="change_step('right')"
                                  :class="{ arrow_disabled: right_is_disabled}">›</span>
                        </div>
                    </div>

                    <div class="button-container">
                        <input type="button" id="next_graph" class="button" value="Next Graph" @click="next_graph">
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import axios from '../utils/axios';
    import cookie_manager from "../utils/cookie_manager";

    export default {
        name: 'AlgorithmEvaluation',
        data() {
            return {
                loading_origin: true,
                loading_sampling: true,
                interval: null, //用于检查图片是否已经加载完毕
                stroke_width: 8,
                graphs: [],
                consuming_time: 0,
                current: 0,
                hoverIndex: -1,
                percentage: 0,
                testNum: null,
                algorithm_list: [
                    {index: 'A', algorithm: 'RJ'}, {index: 'B', algorithm: 'FF'}, {index: 'C', algorithm: 'NEW'},
                    {index: 'D', algorithm: 'RDN'}, {index: 'E', algorithm: 'TIES'}, {index: 'F', algorithm: 'SST'}
                ],
                result_list: [
                    {
                        community_cluster: null, graph_similarity: null, connectivity: null,
                        high_degree_nodes: null, margin_nodes: null, boundary_nodes: null,
                        // subjective_assessment: ''
                    },
                    {
                        community_cluster: null, graph_similarity: null, connectivity: null,
                        high_degree_nodes: null, margin_nodes: null, boundary_nodes: null,
                        // subjective_assessment: ''
                    },
                    {
                        community_cluster: null, graph_similarity: null, connectivity: null,
                        high_degree_nodes: null, margin_nodes: null, boundary_nodes: null,
                        // subjective_assessment: ''
                    },
                    {
                        community_cluster: null, graph_similarity: null, connectivity: null,
                        high_degree_nodes: null, margin_nodes: null, boundary_nodes: null,
                        // subjective_assessment: ''
                    },
                    {
                        community_cluster: null, graph_similarity: null, connectivity: null,
                        high_degree_nodes: null, margin_nodes: null, boundary_nodes: null,
                        // subjective_assessment: ''
                    },
                    {
                        community_cluster: null, graph_similarity: null, connectivity: null,
                        high_degree_nodes: null, margin_nodes: null, boundary_nodes: null,
                        // subjective_assessment: ''
                    }
                ],
                step: 1,
                isCompleteList: [false, false, false, false, false, false],
            }
        },
        mounted() {
            this.$nextTick(() => {
                document.querySelector("div.el-progress__text").style.fontSize = "20px";
                this.init();
                this.setContainerSize();

            })
        },
        methods: {
            init() {
                // axios.get("/getSourceData/").then(response => {
                // this.graphs = ['fb414', 'cspan', 'eurosis', 'fb107', 'fb1684', 'fb1912', 'pgp', 'as'];
                this.graphs = ['fb414', 'cspan', 'eurosis', 'fb107', 'fb1684', 'fb1912', 'as'];
                this.testNum = this.graphs.length;
                this.initSettings();
                // this.graphs = response.data.source_data.sort((a, b) => Math.random() > 0.5 ? -1 : 1);
                // this.testNum = this.graphs.length;
                // this.initSettings();
                // }).catch(error => {
                //         console.log(error)
                //     }
                // );
            },
            setContainerSize() {
                let screenWidth = document.documentElement.clientWidth || document.body.clientWidth;
                let screenHeight = document.documentElement.clientHeight || document.body.clientHeight;
                document.querySelector(".graph-container").style.height = screenHeight * 0.8 + "px";
            },
            initSettings() {
                console.log(this.graphs[this.current])
                this.consuming_time = 0;
                this.result_list.splice(0, this.result_list.length);
                this.isCompleteList.splice(0, this.isCompleteList.length);
                for (var i = 0; i < 6; i++) {
                    this.result_list.push({
                        community_cluster: null, graph_similarity: null, connectivity: null,
                        high_degree_nodes: null, margin_nodes: null, boundary_nodes: null,
                        // subjective_assessment: ''
                    });
                    this.isCompleteList.push(false);
                }
                this.step = 1;
                this.interval = setInterval(() => {
                    if (document.querySelector("#origin-img").complete === true) {
                        this.loading_origin = false;
                    }
                    let imgs = document.querySelectorAll(".img_item");
                    if (imgs[0].complete && imgs[1].complete && imgs[2].complete && imgs[3].complete && imgs[4].complete && imgs[5].complete) {
                        this.loading_sampling = false;
                    }
                    if (this.loading_origin === false && this.loading_sampling === false) {
                        document.querySelector("div.graph-box.origin-graph").style.height = document.querySelector("div.graph-box.sampling-graph").offsetHeight + "px"
                        clearInterval(this.interval);
                    }
                }, 800)
            },
            update_index(index) {
                //重新设置显示顺序
                var indexList = ['A', 'B', 'C', 'D', 'E', 'F'];
                return indexList[index];
            },
            enter(index) {
                this.hoverIndex = index;
            },
            leave() {
                this.hoverIndex = -1;
                this.step = 1;
            },
            change_step(item) {
                if (item === 'left' && this.step !== 1) {
                    this.step -= 1;
                } else if (item === 'right' && this.step !== 2) {
                    this.step += 1;
                }
            },
            submit(index, algorithm) {
                var data = this.result_list[index];
                if (data.community_cluster != null && data.graph_similarity != null && data.connectivity != null
                    && data.high_degree_nodes != null && data.margin_nodes != null && data.boundary_nodes != null) {
                    axios.post('/saveEvaluationRecord/', {
                        
                        origin_graph: this.graphs[this.current],
                        algorithm: algorithm,
                        community_cluster: data.community_cluster,
                        graph_similarity: data.graph_similarity,
                        connectivity: data.connectivity,
                        high_degree_nodes: data.high_degree_nodes,
                        margin_nodes: data.margin_nodes,
                        boundary_nodes: data.boundary_nodes,
                        
                    }).then(response => {
                        this.$message({
                            message: 'Submit successfully!',
                            type: 'success',
                            duration: '1000'
                        });
                        setTimeout(() => {
                            this.isCompleteList[index] = true;
                            document.querySelectorAll('div.select-item span.index')[index].style.color = '#cccccc';
                            this.hoverIndex = -1;
                        }, 600);
                    }).catch(error => {
                        console.log(error);
                    })
                }
            },
            //从数组中随机选count个元素
            getRandomArrayElements(arr, count) {
                var shuffled = arr.slice(0), i = arr.length, min = i - count, temp, index;
                while (i-- > min) {
                    index = Math.floor((i + 1) * Math.random());
                    temp = shuffled[index];
                    shuffled[index] = shuffled[i];
                    shuffled[i] = temp;
                }
                return shuffled.slice(min);
            },
            next_graph() {
                //更新采样算法数组的选择
                // var random_algorithms = ['ff', 'rj', 'rmsc'];
                // var my_algorithms = ['new', 'rdn', 'sst', 'ties'].concat(this.getRandomArrayElements(random_algorithms, 2));
                //
                // this.algorithm_list=[
                //     {index: 'A', algorithm: my_algorithms[0]}, {index: 'B', algorithm: my_algorithms[1]}, {index: 'C', algorithm: my_algorithms[2]},
                //     {index: 'D', algorithm: my_algorithms[3]}, {index: 'E', algorithm: my_algorithms[4]}, {index: 'F', algorithm: my_algorithms[5]}
                // ];
                // this.algorithm_list.sort((a, b) => Math.random() > 0.5 ? -1 : 1); //用于打乱顺序
                this.percentage += (100 / this.testNum);
                if (this.percentage > 100) {
                    this.percentage = 100;
                }
                if (this.current >= this.testNum - 1) {
                    setTimeout(() => {
                        // cookie_manager.setCookie("step", 2);
                        this.$router.push({name: 'thank'});
                    }, 1000);
                } else {
                    this.current += 1;
                    this.loading_origin = true;
                    this.loading_sampling = true;
                    // clearInterval(this.interval);
                    setTimeout(() => {
                        this.initSettings();
                    }, 1000)
                }

                // if (this.isCompleteList.reduce((a, b) => a && b)) {
                //     this.algorithm_list.sort((a, b) => Math.random() > 0.5 ? -1 : 1); //用于打乱顺序
                //     this.percentage += (100 / this.testNum);
                //     if (this.percentage > 100) {
                //         this.percentage = 100;
                //     }
                //     if (this.current >= this.testNum - 1) {
                //         setTimeout(() => {
                //             // cookie_manager.setCookie("step", 2);
                //             this.$router.push({name: 'thank'});
                //         }, 1000);
                //     } else {
                //         this.current += 1;
                //         this.loading_origin = true;
                //         this.loading_sampling = true;
                //         // clearInterval(this.interval);
                //         setTimeout(() => {
                //             this.initSettings();
                //         }, 1000)
                //     }
                // } else {
                //     this.$message({
                //         message: "Please complete all sampling graphs' ratings",
                //         type: 'info',
                //         duration: '1000'
                //     });
                // }
            },
            samplingImgPath: function (item) {
                if (this.graphs.length <= 0) {
                    return "/"
                } else {
                    return "/static/images/new_evaluation/" + this.graphs[this.current] + '/' + this.graphs[this.current] + '_' + item + '.svg';
                }
            },
        },
        computed: {
            originImgPath: function () {
                if (this.graphs.length <= 0) {
                    return "/"
                } else {
                    return "/static/images/new_evaluation/" + this.graphs[this.current] + '/' + this.graphs[this.current] + '_origin.svg';
                }
            },
            left_is_disabled: function () {
                return this.step === 1;
            },
            right_is_disabled: function () {
                return this.step === 2;
            },
            percent: function () {
                if (this.percentage >= 100) {
                    return 100;
                } else {
                    return Math.floor(this.percentage);
                }
            }
        }
    }
</script>

<style>

    .progress-container .el-progress__text {
        cursor: default;
        color: #999999;
        line-height: 10px;
        height: 10px;
    }

    .rate-container .my_rate {
        margin: 3% auto;
        height: 27.3%;
    }

    .rate-container .term {
        font-size: 21px;
        color: white;
        cursor: default;
    }

    .rate-container .my_rate .rate {
        margin-top: 2%;
    }

    .rate-container .my_rate .el-rate__icon {
        font-size: 28px;
    }
</style>

<style scoped>
    .body, .content {
        width: 100%;
        text-align: center;
    }

    .progress-container {
        text-align: center;
    }


    .complete_num_item {
        border: 1px;
        border-radius: 50%;
        width: 15px;
        height: 15px;
        background-color: #b3d8ff;
        margin: 0 8px;
    }

    .graph-container {
        width: 80%;
        padding-top: 1%;
        margin: 0 auto;
    }

    .graph-box {
        box-sizing: border-box;
        position: relative;
    }

    .origin-graph {
        /*float: left;*/
        /*border: 1px solid #333333;*/
        /*width: 26%;*/
        /*height: 100%;*/
        /*display: flex;*/
        /*flex-wrap: nowrap;*/
        /*flex-direction: column;*/
        /*justify-content: center;*/
        /*align-items: center;*/


        position: relative;
        width: 26%;
        float: left;
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        justify-content: center;
        padding: 4% 0.2% 0.2% 0.2%;
        box-sizing: border-box;
        border: 2px solid #cccccc;
        margin-bottom: 2%;
    }

    #origin-tip {
        position: absolute;
        top: 73%;
        margin-top: -4%;
        font-weight: bold;
        font-size: 22px;
        cursor: default;
        /*margin-top: 5%;*/
        color: #666666;
    }

    #my-origin-graph {
        padding: 5% 0;
        position: absolute;
        height: 50%;
        bottom: 25%;
        top: 21%;
        left: 0;
        right: 0;
        display: table-cell;
        vertical-align: middle;
        margin-top: -4%;
    }

    .sampling-graph {
        position: relative;
        width: 73%;
        float: right;
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        justify-content: center;
        padding: 4% 0.2% 0.2% 0.2%;
        box-sizing: border-box;
        border: 2px solid #cccccc;
        margin-bottom: 2.5%;
    }

    .sampling-tip {
        text-align: center;
        position: absolute;
        top: 2.5%;
        font-size: 25px;
        cursor: default;
        height: 25px;
        line-height: 25px;
        font-weight: bold;
    }

    .select-item {
        position: relative;
        width: 32%;
        padding: 1.6%;
        box-sizing: border-box;
        margin: 0.5%;
        border: 1px solid #cccccc
    }

    .select-item span.index {
        position: absolute;
        bottom: 1%;
        left: 1.5%;
        font-size: 28px;
        cursor: default;
        color: #cccccc;
    }

    .select-item:hover {
        border: 1px solid #CCCCCC;
    }

    .select-item-completed {
        border: 1px solid #CCCCCC;
    }

    .my_padding {
        padding-top: 8%;
        padding-bottom: 8%;
    }

    .complete-opacity-background {
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background-color: black;
        opacity: 0.02;
    }

    .opacity-background {
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background-color: black;
        opacity: 0.7;
    }

    .rate-container {
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        overflow: hidden;
        text-align: center;
        padding: 5% 8%;
    }

    .rate-container .arrow {
        font-family: Arial;
        font-size: 45px;
        color: white;
        position: absolute;
        top: 40%;
        cursor: pointer;
    }

    .rate-container .left-arrow {
        left: 2%;
    }

    .rate-container .right-arrow {
        right: 2%;
    }

    .rate-container .arrow_disabled {
        color: #999999;
        cursor: default;
    }

    .rate-container .rate-div-item {
        position: absolute;
        bottom: 10%;
        left: 7%;
        right: 7%;
        top: 10%;
    }

    .rate-container #submit {
        position: absolute;
        bottom: 0;
        width: 40%;
        left: 30%;
        right: 30%;
    }

    .button-container {
        width: 100%;
        margin: 1.5% auto;
        text-align: center;
    }

    .button {
        width: 120px;
        height: 45px;
        line-height: 45px;
        font-size: 20px;
    }

</style>
