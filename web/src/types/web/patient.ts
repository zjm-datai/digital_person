// 📄 src/types/patient.ts

/** 病人身份信息 */
export interface PatientIdentity {
    patientId: string;
    idType: string;
    idNumber: string;
    patientName: string;
}

/** 就诊信息 */
export interface VisitInfo {
    department?: string;
    visitNumber?: string;
}

/** 基础健康信息 */
export interface BasicInfo {
    gender?: string;
    birthday?: string;
    aboBloodType?: string;
    rhBloodType?: string;
}

/** 生命体征 */
export interface VitalSigns {
    systolicPressure?: number;
    diastolicPressure?: number;
    height?: number;
    weight?: number;
}

/** 月经历史 */
export interface MenstrualHistory {
    menarcheAge?: number;
    intervalDays?: number;
    durationDays?: number;
    isSterilization?: boolean;
    lastMenstrualDate?: string;
}

/** 婚育信息 */
export interface MarriageChildInfo {
    marriageStatus?: string;
    fullTermCount?: number;
    prematureCount?: number;
    abortionCount?: number;
    livingChildrenCount?: number;
}

/** 既往史 */
export interface PastHistory {
    personalHistory?: string;
    bloodTransfusionHistory?: string;
    diseaseHistory?: string;
    epidemiologicalHistory?: string;
    menstrualHistory?: MenstrualHistory;
    surgeryHistory?: string;
    familyHistory?: string;
}

/** 处方信息 */
export interface Prescription {
    prescriptionName?: string;
    herbs?: string[];
}

/** 中西医诊断 */
export interface Diagnosis {
    tcmDiagnosisName?: string;
    tcmDiagnosisCode?: string;
    tcmSyndromeName?: string;
    westernDiagnosisName?: string;
    westernDiagnosisCode?: string;
}

/** 中医四诊 */
export interface TcmFourExams {
    inspection?: string;
    inquiry?: string;
    listeningAndSmelling?: string;
    palpation?: string;
}

/** 最近一次就诊记录 */
export interface LastRecord {
    chiefComplaint?: string;
    presentIllness?: string;
    menstrualHistory?: MenstrualHistory;
    tcmFourExams?: TcmFourExams;
    physicalExam?: string;
    auxiliaryExam?: string;
    diagnosis?: Diagnosis;
    treatmentPrinciple?: string;
    treatmentAdvice?: string;
    prescription?: Prescription;
}

/** 复诊信息 */
export interface RevisitInfo {
    isRevisit: number;
    lastRecord?: LastRecord;
}

/** 完整的病人详情结构 */
export interface PatientDetail {
    patientIdentity: PatientIdentity;
    visitInfo?: VisitInfo;
    latestMedicalRecord?: {
        basicInfo?: BasicInfo;
        vitalSigns?: VitalSigns;
        marriageChildInfo?: MarriageChildInfo;
        pastHistory?: PastHistory;
        allergyHistory?: string | null;
        childGrowthInfo?: any;
    };
    revisitInfo?: RevisitInfo;
}

/** 与后端 `/base` 接口对应的概要信息 */
export interface PatientBase {
    name: string;
    department?: string;
    visit_number?: string;
    age: number;
}
