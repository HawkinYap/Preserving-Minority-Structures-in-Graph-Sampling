<template>
    <div class="body">
        <div class="header">
            <span><a href="#"><i class="el-icon-share"></i> Open-End Graph Exploration - User Study</a></span>
        </div>
        <div class="content">
            <p id="tip">Thank you !</p>
        </div>
    </div>
</template>

<script>
    import cookie_manager from "../utils/cookie_manager";
    export default {
        name: 'Thanks',
        props: {},
        data() {
            return {}
        },
        mounted() {
            cookie_manager.deleteCookie("current_user")
        },
        methods: {},
        computed: {}
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
    .body {
        width: 100%;
    }

    .content {
        width: 100%;
        text-align: center;
    }

    #tip {
        margin-top: 13%;
        text-align: center;
        cursor: default;
        font-size: 85px;
        font-weight: bold;
        color: #ccc;
    }

</style>
