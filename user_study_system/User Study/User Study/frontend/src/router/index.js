import Vue from 'vue'
import VueRouter from 'vue-router'

import Home from '../components/Home'
import Test from '../components/Test'
import Introduction from '../components/Introduction'
import NodeLinkGraph from '../components/NodeLinkGraph'
import Review from '../components/Review'
import HeatmapGraph from '../components/HeatmapGraph'
import AlgorithmEvaluation from '../components/AlgorithmEvaluation'
import Thank from '../components/Thank'
import pwm_test from '../components/pwm_test'

Vue.use(VueRouter);

const router = new VueRouter({
    routes: [
        {path: '/home', name: 'home', component: Home},
        {path: '/intro', name: 'intro', component: Introduction},
        {path: '/test', name: 'test', component: Test},
        {path: '/nodelink', name: 'nodelink', component: NodeLinkGraph},
        {path: '/review', name: 'review', component: Review},
        {path: '/evaluation', name: 'evaluation', component: AlgorithmEvaluation},
        {path: '/end', name: 'thank', component: Thank},
        {path: '/heatmap', name: 'heatmap', component: HeatmapGraph},
        {path: '/pwm_test', name: 'pwm_test', component: pwm_test},
        {path: '/', redirect: '/home'}
    ]
});

export default router;
