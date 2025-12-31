<template>
  <div class="patient-root">
    <!-- 背景图，与 Welcome 保持一致 -->
    <img class="bg-img" src="/bg.png" alt="bg" draggable="false" />

    <!-- 顶部栏 -->
    <header class="page-header">
      <div class="left">
        <el-button link type="primary" @click="goBack">
          返回
        </el-button>
        <h1 class="title">测试患者列表（Mock）</h1>
      </div>
      <!-- <div class="right">
        <img class="logo" src="/logo@2x.png" alt="logo" draggable="false" />
      </div> -->
    </header>

    <!-- 内容区域 -->
    <main class="patient-main">
      <div class="patient-card-container">
        <el-empty
          v-if="isLoading && patients.length === 0"
          description="加载中..."
        />
        <el-empty
          v-else-if="!isLoading && patients.length === 0"
          description="暂无 Mock 数据"
        />

        <div v-else class="patient-grid">
          <div
            v-for="item in patients"
            :key="item.patientIdentity.patientId"
            class="patient-card"
          >
            <div class="card-clickable" @click="openDetail(item)">
              <div class="card-header">
                <div class="name-line">
                  <span class="name">{{ item.patientIdentity.patientName }}</span>
                  <span class="tag">{{ item.visitInfo.department }}</span>
                </div>
                <div class="sub-line">
                  <span>就诊号：{{ item.visitInfo.visitNumber }}</span>
                  <span v-if="item.revisitInfo?.isRevisit === 1" class="badge revisit">
                    复诊
                  </span>
                  <span v-else class="badge first">
                    初诊
                  </span>
                </div>
              </div>

              <div class="card-body">
                <div class="row">
                  <span class="label">性别</span>
                  <span class="value">{{ item.latestMedicalRecord.basicInfo.gender }}</span>
                </div>
                <div class="row">
                  <span class="label">年龄</span>
                  <span class="value">{{ computeAge(item.latestMedicalRecord.basicInfo.birthday) }} 岁</span>
                </div>
                <div class="row">
                  <span class="label">主诉</span>
                  <span class="value ellipsis">
                    {{ item.revisitInfo?.lastRecord?.chiefComplaint || '暂无主诉' }}
                  </span>
                </div>
              </div>
            </div>

            <div class="card-footer">
              <el-button
                type="primary"
                size="small"
                @click.stop="startConsult(item)"
              >
                进入问诊
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      :title="currentPatient?.patientIdentity.patientName || '病历详情'"
      width="720px"
      destroy-on-close
    >
      <template v-if="currentPatient">
        <section class="detail-section">
          <h3>基础信息</h3>
          <div class="detail-grid">
            <div><span class="label">姓名：</span>{{ currentPatient.patientIdentity.patientName }}</div>
            <div><span class="label">科室：</span>{{ currentPatient.visitInfo.department }}</div>
            <div><span class="label">就诊号：</span>{{ currentPatient.visitInfo.visitNumber }}</div>
            <div><span class="label">性别：</span>{{ currentPatient.latestMedicalRecord.basicInfo.gender }}</div>
            <div><span class="label">生日：</span>{{ currentPatient.latestMedicalRecord.basicInfo.birthday }}</div>
            <div><span class="label">血型：</span>{{ currentPatient.latestMedicalRecord.basicInfo.aboBloodType }} 型</div>
          </div>
        </section>

        <section class="detail-section">
          <h3>主诉 & 现病史</h3>
          <p class="text-line">
            <span class="label">主诉：</span>
            <span>{{ currentPatient.revisitInfo?.lastRecord?.chiefComplaint || '暂无记录' }}</span>
          </p>
          <p class="text-block">
            <span class="label">现病史：</span>
            <span>{{ currentPatient.revisitInfo?.lastRecord?.presentIllness || '暂无记录' }}</span>
          </p>
        </section>

        <section class="detail-section">
          <h3>中医诊断</h3>
          <p class="text-line">
            <span class="label">中医诊断：</span>
            <span>{{ currentPatient.revisitInfo?.lastRecord?.diagnosis?.tcmDiagnosisName || '暂无' }}</span>
          </p>
          <p class="text-line">
            <span class="label">证型：</span>
            <span>{{ currentPatient.revisitInfo?.lastRecord?.diagnosis?.tcmSyndromeName || '暂无' }}</span>
          </p>
          <p class="text-line">
            <span class="label">西医诊断：</span>
            <span>{{ currentPatient.revisitInfo?.lastRecord?.diagnosis?.westernDiagnosisName || '暂无' }}</span>
          </p>
        </section>

        <section class="detail-section">
          <h3>处方</h3>
          <p class="text-line">
            <span class="label">方名：</span>
            <span>{{ currentPatient.revisitInfo?.lastRecord?.prescription?.prescriptionName || '暂无' }}</span>
          </p>
          <p class="text-line">
            <span class="label">药物：</span>
            <span>
              {{
                (currentPatient.revisitInfo?.lastRecord?.prescription?.herbs || []).join('、') || '暂无'
              }}
            </span>
          </p>
        </section>
      </template>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="detailVisible = false">关 闭</el-button>
          <el-button
            type="primary"
            @click="currentPatient && startConsult(currentPatient)"
          >
            进入问诊
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

import { usePatientStore } from '@/stores/patient';
import { useAppStore } from '@/stores/app';
import { apiCreateSession } from '@/api/session';

import type { PatientDetail } from '@/types/web/patient';

const router = useRouter();
const patientStore = usePatientStore();
const appStore = useAppStore();

const patients = ref<PatientDetail[]>([]);
const isLoading = ref(false);
const detailVisible = ref(false);
const currentPatient = ref<PatientDetail | null>(null);

function computeAge(birthday: string): number {
  if (!birthday) return 0;
  const birth = new Date(birthday);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const m = today.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
}

function goBack() {
  router.back();
}

function openDetail(item: PatientDetail) {
  currentPatient.value = item;
  detailVisible.value = true;
}

function getAuthToken(): string | null {
  // 与 WelcomePage 中保持一致（这里只是 demo）
  return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzY5MTYxNTA2LCJpYXQiOjE3NjYzOTY3MDYsImp0aSI6IjEtMTc2NjM5NjcwNi45NTkyMDEifQ.R22n_rEY93Ef7HataexTfZuhMY6C7v-I3qRv0WfmVrQ";
}

async function toChat(extraQuery: Record<string, any> = {}) {
  try {
    const data = await apiCreateSession(getAuthToken);
    const q = { ...extraQuery, sid: data.session_id };
    if (appStore.platform !== 'web') {
      // @ts-ignore
      q.platform = appStore.platform;
    }
    router.push({ path: '/chat', query: q });
  } catch (e) {
    console.error('创建会话失败：', e);
    ElMessage.error('创建会话失败');
  }
}

async function startConsult(item: PatientDetail) {
  try {
    const pid = item.patientIdentity.patientId;
    await patientStore.recordScan(pid);
    await toChat({ from: 'patient_list', pid });
  } catch (e) {
    console.error(e);
    ElMessage.error('进入问诊失败');
  }
}

onMounted(async () => {
  try {
    isLoading.value = true;
    const resp = await fetch('/api/v1/patient/all');
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    patients.value = data || [];
  } catch (e: any) {
    console.error('加载病人列表失败：', e);
    ElMessage.error(`加载病人列表失败：${e?.message || '未知错误'}`);
  } finally {
    isLoading.value = false;
  }
});
</script>

<style scoped>
.patient-root {
  position: relative;
  min-height: 100vh;
  width: 100%;
  overflow: hidden;
}

/* 背景图跟 Welcome 一致 */
.bg-img {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: -1;
}

/* 顶部栏 */
.page-header {
  position: relative;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.6vh 3vw;
}

.page-header .left {
  display: flex;
  align-items: center;
  gap: 1.2vw;
}

.title {
  font-size: 1.4vw;
  font-weight: 600;
  color: #1f2933;
}

.page-header .right .logo {
  width: 7vw;
  height: auto;
}

/* 主体 */
.patient-main {
  position: relative;
  z-index: 10;
  padding: 1vh 3vw 4vh;
}

.patient-card-container {
  background: linear-gradient(124deg, rgba(250, 250, 255, 0.6) 0%, #e9f2f7 100%);
  border-radius: 1.2vw;
  padding: 2vh 2vw;
  box-shadow: 0 1vh 4vh -1vh rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(4px);
}

/* 卡片网格 */
.patient-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.6vw;
  margin-top: 1vh;
}

.patient-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.92);
  border-radius: 0.9vw;
  padding: 1vw 1vw 0.8vw;
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow: 0 1vh 2vh -1vh rgba(0, 0, 0, 0.18);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.patient-card:hover {
  transform: translateY(-0.4vh);
  box-shadow: 0 1.2vh 2.4vh -1vh rgba(0, 0, 0, 0.25);
}

.card-clickable {
  cursor: pointer;
}

.card-header {
  margin-bottom: 0.6vh;
}

.name-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.4vw;
  margin-bottom: 0.3vh;
}

.name {
  font-size: 1.05vw;
  font-weight: 600;
  color: #111827;
}

.tag {
  font-size: 0.8vw;
  padding: 0.1vh 0.5vw;
  border-radius: 999px;
  background: rgba(70, 117, 234, 0.1);
  color: #3557d9;
}

.sub-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.8vw;
  color: #6b7280;
}

.badge {
  padding: 0.1vh 0.5vw;
  border-radius: 999px;
  font-size: 0.75vw;
}
.badge.revisit {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}
.badge.first {
  background: rgba(250, 204, 21, 0.12);
  color: #a16207;
}

.card-body {
  margin-top: 0.6vh;
}

.row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8vw;
  margin-bottom: 0.3vh;
}

.label {
  color: #6b7280;
}

.value {
  color: #111827;
}

.ellipsis {
  max-width: 16vw;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.8vh;
}

/* 详情弹窗 */
.detail-section {
  margin-bottom: 1.6vh;
}

.detail-section h3 {
  font-size: 1vw;
  margin-bottom: 0.8vh;
  color: #111827;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.6vh 1.4vw;
  font-size: 0.9vw;
}

.detail-grid .label {
  color: #6b7280;
}

.text-line,
.text-block {
  font-size: 0.9vw;
  margin-bottom: 0.4vh;
}

.text-block span:last-child {
  white-space: pre-wrap;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.8vw;
}
</style>
