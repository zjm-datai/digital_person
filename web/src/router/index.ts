
import { useAuthStore } from "@/stores/auth";
import { createRouter, createWebHashHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

const LoginPage = () => import("@/views/LoginPage.vue")

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
        path: '/login',
        name: 'LoginPage',
        component: LoginPage,
        meta: {
            public: true
        }
    },
    {
        path: '/home',
        name: 'HomePage',
        component: HomePage,
        meta: { 
            requiresAuth: true 
        }
    },
    {
        path: '/welcome',
        name: 'WelcomePage',
        component: WelcomePage,
        meta: { 
            requiresAuth: true 
        }
    },
    {
        path: '/patients',
        name: 'PatientListPage',
        component: PatientListPage,
        meta: { 
            requiresAuth: true 
        }
    },
    {
        path: '/phone/home',
        name: 'HomePhonePage',
        component: HomePhonePage,
        meta: { 
            requiresAuth: true 
        }
    },
    {
        path: '/chat',
        name: 'ChatPage',
        component: ChatPage,
        meta: { 
            requiresAuth: true 
        }
    },
    {
        path: '/phone/chat',
        name: 'ChatPagePhone',
        component: ChatPagePhone,
        meta: { 
            requiresAuth: true 
        }
    },
    {
        path: '/report',
        name: 'ReportPage',
        component: ReportPage,
        meta: { 
            requiresAuth: true 
        }
    }
]

const router = createRouter({
    history: createWebHashHistory("/consultation/"),
    routes,
});

router.beforeEach(async (to) => {
    const auth = useAuthStore();

    if (!auth.loaded) {
        await auth.bootstrap();
    }

    if (to.meta.public) return true;

    if (to.meta.requiresAuth && !auth.isAuthed) {
        return { 
            name: "LoginPage", 
            query: { redirect: to.fullPath } 
        };
    }

    // 已登录访问 login，送回 home
    if (to.name === "LoginPage" && auth.isAuthed) {
        return { name: "HomePage" };
    }

    return true;
})

export default router;