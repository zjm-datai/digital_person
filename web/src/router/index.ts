
import { createRouter, createWebHashHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

const HomePage = () => import("@/views/pad/HomePage.vue")
const ChatPage = () => import("@/views/pad/ChatPage.vue")
const HomePhonePage = () => import("@/views/phone/HomePage.vue")
const ChatPagePhone = () => import("@/views/phone/ChatPage.vue")
const ReportPage = () => import("@/views/ReportPage.vue")
const WelcomePage = () => import("@/views/pad/WelcomePage.vue")

const PatientListPage = () => import("@/views/pad/PatientListPage.vue")

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        redirect: '/home'
    },
    {
        path: '/home',
        name: 'HomePage',
        component: HomePage
    },
    {
        path: '/welcome',
        name: 'WelcomePage',
        component: WelcomePage
    },
    {
        path: '/patients',
        name: 'PatientListPage',
        component: PatientListPage
    },
    {
        path: '/phone/home',
        name: 'HomePhonePage',
        component: HomePhonePage
    },
    {
        path: '/chat',
        name: 'ChatPage',
        component: ChatPage
    },
    {
        path: '/phone/chat',
        name: 'ChatPagePhone',
        component: ChatPagePhone
    },
    {
        path: '/report',
        name: 'ReportPage',
        component: ReportPage
    }
]

const router = createRouter({
    history: createWebHashHistory(),  // HTML5 模式
    routes,
});

export default router;