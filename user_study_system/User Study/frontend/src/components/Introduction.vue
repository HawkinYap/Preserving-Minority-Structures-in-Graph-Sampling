<template>
    <div>
        <div class="header">
            <span><a href="/"><i class="el-icon-share"></i> Open-End Graph Exploration - User Study</a></span>
        </div>
        <div class="content">
            <div class="title-container">
                <h2>Experimental Introduction</h2>
            </div>
            <div class="text-container">
                <p>The experiment focuses on the domains that users may concern in graph structures for further
                    explorations
                    of graph visualizations, in which key informations of users’ interactive explorations of the graph
                    data
                    are recorded from the perspective of users’ visual perceptions. This helps figure out the domains
                    that
                    users concern in the visual presentations of the graph data and provides a basis for the subsequent
                    work
                    that the design and research of the graph visualizations.</p>
            </div>
            <div class="video-container">
                <video src="/static/video/video-Fullmp4.mp4" controls></video> <!-- http://www.w3school.com.cn/i/movie.ogg -->
            </div>
            <div class="button-container">
                <input type="button" id="OK" value="I know" @click="toHome">
                <!--            <el-button id="OK" type="primary" plain @click="toHome" ></el-button>-->
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'Home',
        props: {},
        data() {
            return {}
        },
        mounted() {
            this.$nextTick(() => {
                let screenWidth = document.documentElement.clientWidth || document.body.clientWidth;
                let screenHeight = document.documentElement.clientHeight || document.body.clientHeight;
                // console.log(screenWidth, screenHeight);
                document.querySelector(".video-container").style.width = screenWidth * 0.6 + "px";
            })
        },
        methods: {
            toHome() {
                this.$router.push({name: 'home', params: {msg: 'intro'}});
            }
        },
        computed: {}
    }
</script>
<style scoped>
    .content {
        width: 100%;
        height: 100%;
        cursor: default;
    }

    .title-container {
        width: 90%;
        margin: 1% auto;
        text-align: center;
    }

    .text-container {
        width: 85%;
        margin: 0 auto;
    }

    .text-container p {
        font: normal 20px arial, sans-serif;
    }

    .video-container {
        margin: 2% auto;
        text-align: center;
    }

    video {
        width: 100%;
        height: 100%;
    }

    .button-container {
        text-align: center;
    }


    #OK {
        height: 50px;
        width: 8%;
        font-size: 20px;
        margin-bottom: 15px;
        cursor: pointer;
    }


</style>