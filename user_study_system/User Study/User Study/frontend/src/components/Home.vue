<template>
    <div class="body">
        <div class="header">
            <span><a href="/"><i class="el-icon-share"></i> Open-End Graph Exploration - User Study</a></span>
        </div>
        <div class="content">
            <p id="processing">Processing</p>
            <div class="my-step-contaniner">
                <el-steps :active="step" align-center>
                    <el-step title="Introduction"></el-step>
                    <el-step title="Pre-Experiment"></el-step>
                    <el-step title="Experiment"></el-step>
                    <el-step title="Result Review"></el-step>
                </el-steps>
            </div>
            <input type="button" id="next_step_btn" :value="btn_text" @click="toNext">
        </div>
        <el-dialog
                title="Sign up"
                :visible.sync="dialogVisible"
                width="65%"
                :show-close="false">
            <el-form size="medium" label-position="left" :model="form" :rules="rules" ref="ruleForm"
                     label-width="12%">
                <el-form-item label="Name" prop="name">
                    <el-input v-model="form.name"></el-input>
                </el-form-item>
                <el-form-item label="Gender" prop="gender">
                    <el-radio-group v-model="form.gender">
                        <el-radio label="Male"></el-radio>
                        <el-radio label="Female"></el-radio>
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="Age" prop="age">
                    <el-input v-model.number="form.age"></el-input>
                </el-form-item>
                <el-form-item label="Education" prop="education">
                    <el-select v-model="form.education" placeholder="please select education">
                        <el-option key="undergraduate" label="undergraduate" value="undergraduate"></el-option>
                        <el-option key="master" label="master" value="master"></el-option>
                        <el-option key="doctor" label="doctor" value="doctor"></el-option>
                        <el-option key="others" label="others" value="others"></el-option>
                        <el-option key="" label="" value="" disabled style="cursor: default"></el-option>
                    </el-select>
                    
                </el-form-item>
                <el-form-item label="Major" prop="major">
                    
                    <el-select v-model="form.major" placeholder="please select major">
                        <el-option key="Computer Science" label="Computer Science" value="Computer Science"></el-option>
                        <el-option key="Automatization" label="Automatization" value="Automatization"></el-option>
                        <el-option key="Communication" label="Communication" value="Communication"></el-option>
                        <el-option key="Software Engineering" label="Software Engineering"
                                   value="Software Engineering"></el-option>
                        <el-option key="others" label="others" value="others"></el-option>
                        <el-option key="" label="" value="" disabled style="cursor: default"></el-option>
                    </el-select>
                    
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="submitForm('ruleForm')">Register</el-button>
                    <el-button @click="resetForm('ruleForm')">Reset</el-button>
                </el-form-item>
            </el-form>
        </el-dialog>
    </div>
</template>

<script>
    import axios from '../utils/axios'
    import cookie from '../utils/cookie_manager'

    export default {
        name: 'Home',
        props: {},
        data() {
            return {
                step: 0,
                dialogVisible: false,
                form: {
                    name: '',
                    education: '',
                    age: '',
                    sex: '',
                    research: ''
                },
                rules: {
                    name: [
                        {required: true, message: 'please input user name', trigger: 'blur'},
                    ],
                    gender: [
                        {required: true, message: 'please select gender', trigger: 'change'}
                    ],
                    education: [
                        {required: true, message: 'please select education', trigger: 'change'}
                    ],
                    age: [
                        {required: true, message: 'please input age'},
                        {type: 'number', message: 'age must be number'}
                    ],
                    major: [
                        {required: true, message: 'please select major ', trigger: 'change'}
                    ]
                }
            }
        },
        mounted() {
            this.$nextTick(() => {
                // this.isLogged();
                let msg = this.$route.params.msg;
                switch (msg) {
                    case 'intro':
                        this.step = 1;
                        break;
                    case 'test':
                        this.step = 2;
                        break;
                    case 'expertment':
                        this.step = 3;
                        // this.signout();
                        break;
                    default:
                        break;
                }
            })
        },
        methods: {
            toNext() {
                switch (this.step) {
                    case 0:
                        // this.isLogged();
                        this.$router.push('/intro');
                        break;
                    case 1:
                        if (this.isLogged()) {
                            this.$router.push('/test');
                        } else {
                            this.dialogVisible = true;
                        }
                        break;
                    case 2:
                        this.$router.push('/nodelink');
                        break;
                    case 3:
                        this.$router.push('/review');
                        break;
                    default:
                        break;
                }
            },
            submitForm(formName) {
                this.$refs[formName].validate((valid) => {
                    if (valid) {
                        axios.post("/register/", this.form)
                            .then(response => {
                                if (response.data === 'OK') {
                                    cookie.setCookie("current_user", this.form.name);
                                    this.dialogVisible = false;
                                    this.$message({
                                        message: 'Submit successfully!',
                                        type: 'success',
                                        duration: '500'
                                    });
                                    setTimeout(() => {
                                        this.$router.push('/test');
                                    }, 800);
                                } else if (response.data === 'fail') {
                                    this.$message({
                                        message: 'The user already exists',
                                        type: 'warning',
                                        duration: '800'
                                    });
                                } else {
                                    this.$message({
                                        message: 'The user has already signed in',
                                        type: 'info',
                                        duration: '800'
                                    });
                                }
                            })
                    } else {
                        return false;
                    }
                });
            },
            resetForm(formName) {
                this.$refs[formName].resetFields();
            },
            signout() {
                cookie.deleteCookie("current_user");
            },
            isLogged() {
                return cookie.getCookie("current_user");
            }
        },
        computed: {
            btn_text: function () {
                return this.step === 0 ? "Start" : "Next Step";
            },
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<!--步骤条样式-->
<style>
    .my-step-contaniner {
        width: 70%;
        margin: 5% auto;
        cursor: default;
    }

    /*步骤序号图标*/
    .my-step-contaniner .el-step__head.is-process {
        color: #666666;
        border-color: #666666;
    }

    .my-step-contaniner .el-step__icon {
        font-size: 50px;
        width: 50px;
        height: 50px;
    }

    .my-step-contaniner .is-finish {
        color: #666666;
        border-color: #666666;
    }


    /*步骤进度条*/
    .my-step-contaniner .el-step.is-horizontal .el-step__line {
        height: 6px;
        top: 22px;
    }

    .my-step-contaniner .el-step__line {
        position: absolute;
        border-color: inherit;
        background-color: #CCCCCC;
        height: 6px;
        top: 22px;
    }

    .my-step-contaniner .is-finish .el-step__line {
        background-color: #666666;
    }


    /*步骤标题*/
    .my-step-contaniner .el-step__title.is-process {
        font-weight: 700;
        color: #666666;
        margin-top: 2%;
    }

    .my-step-contaniner .el-step__title {
        font-size: 25px;
        line-height: 38px;
        margin-top: 2%;
    }

    .my-step-contaniner .el-step__head.is-process .el-step__icon.is-text {
        color: #666666;
    }

    /*步骤描述*/
    .my-step-contaniner .el-step__description.is-process {
        color: #666666;
    }

    .my-step-contaniner .el-step__description {
        padding-right: 10%;
        margin-top: -5px;
        font-size: 18px;
        line-height: 20px;
        font-weight: 400;
    }
</style>


<style scoped>
    .body {
        width: 100%;
    }

    .content {
        width: 100%;
        text-align: center;
    }

    #processing {
        margin-top: 6%;
        text-align: center;
        cursor: default;
        font-size: 60px;
        font-weight: bold;
        color: #ccc;
    }

    #next_step_btn {
        margin-top: 3%;
        width: 120px;
        height: 45px;
        line-height: 45px;
        font-size: 20px;
        margin-bottom: 20px;
        cursor: pointer;
    }

</style>
