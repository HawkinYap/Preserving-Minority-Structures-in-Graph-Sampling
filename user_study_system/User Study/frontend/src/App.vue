<template>
    <div id="app">
<!--        <div class="header">-->
<!--            <span><a href="/"><i class="el-icon-share"></i> Graph Structure</a></span>-->
<!--        </div>-->
        <router-view></router-view>
    </div>
</template>

<script>
    import axios from './utils/axios'

    export default {
        name: 'app',
        components: {},
        data() {
            return {}
        },
        mounted() {
            this.$nextTick(() => {

            })
        },
        beforeDestroy() {
            axios.get('/signout/')
                .then(response => {

                })
        }
    }
</script>

<style>
    *{
        font-family: Arial;
    }
    html, body {
        width: 100%;
        height: 100%;
        margin: 0 auto;
        overflow-x: hidden;
    }

    .header {
        width: 100%;
        height: 20%;
        background-color: #ccc;
    }

    .header a {
        font-size: 30px;
        font-weight: bold;
        line-height: 60px;
        color: white;
        margin-left: 1%;
        text-decoration: none;
    }
</style>
