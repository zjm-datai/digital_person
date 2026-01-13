from datetime import date, datetime

MOCK_PATIENT_DATA = [
    # 呼吸复诊女
    {
        "patientIdentity": {
            "patientId": "PID1234548",
            "idType": "01",
            "idNumber": "110101199001011234",
            "patientName": "王雨惠"
        },
        "visitInfo": {
            "department": "呼吸科",
            "visitNumber": "V0000123"
        },
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "女",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+"
            },
            "vitalSigns": {
                "systolicPressure": 120,
                "diastolicPressure": 80,
                "height": 165,
                "weight": 60
            },
            "marriageChildInfo": {
                "marriageStatus": "已婚",
                "fullTermCount": 1,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 1
            },
            "pastHistory": {
                "personalHistory": "无烟酒不良嗜好，否认冶游史。",
                "bloodTransfusionHistory": "无",
                "diseaseHistory": "患者平素体健，无重大慢性疾病无传染病史",
                "epidemiologicalHistory": "无传染病史，流行病学史",
                "menstrualHistory": {
                    "menarcheAge": 13,
                    "intervalDays": 28,
                    "durationDays": 5,
                    "isSterilization": False,
                    "lastMenstrualDate": "2025-10-25"
                },
                "surgeryHistory": "无",
                "familyHistory": "无家族性遗传病、精神病、肿瘤等类似病史。"
            },
            "allergyHistory": "未发现",
            "childGrowthInfo": None
        },
        "revisitInfo": {
            "isRevisit": 1,
            "lastRecord": {
                "chiefComplaint": "反复咳嗽、咳痰10年，活动后气促5年，加重1周。",
                "presentIllness": (
                    "患者近10年来每于冬春季节出现咳嗽、咳白色黏痰，晨起明显。近5年逐渐出现登楼或快走时气促，休息后可缓解。1周前受凉后咳嗽加剧，"
                    "痰量增多呈黄脓性，气促加重，日常活动受限，无发热、咯血、夜间阵发性呼吸困难。自服“头孢类抗生素”及止咳药效果不佳，今来诊。"
                ),
                "menstrualHistory": {
                    "menarcheAge": 13,
                    "intervalDays": 28,
                    "durationDays": 5,
                    "isSterilization": False,
                    "lastMenstrualDate": "2024-09-25"
                },
                "tcmFourExams": {
                    "inspection": "红黄隐隐，明润含蓄",
                    "inquiry": "时有腹胀便溏，倦怠乏力",
                    "listeningAndSmelling": "口气",
                    "palpation": "脉弦"
                },
                "physicalExam": "无",
                "auxiliaryExam": "血常规：WBC 9.5×10^9/L，CRP 12 mg/L",
                "diagnosis": {
                    "tcmDiagnosisName": "湿疮",
                    "tcmDiagnosisCode": "A08.01.07",
                    "tcmSyndromeName": "脾虚湿困证",
                    "westernDiagnosisName": "特应性皮炎",
                    "westernDiagnosisCode": "L20.900"
                },
                "treatmentPrinciple": "健脾化湿",
                "treatmentAdvice": "少食多餐，避免辛辣油腻",
                "prescription": {
                    "prescriptionName": "复方参蝉汤",
                    "herbs": ["党参", "蝉蜕", "生白术", "茯苓", "温山药", "炒白扁豆", "薏苡仁", "生黄芪", "炒麦芽", "炒稻芽", "炒鸡内金", "大枣", "生甘草", "蚕砂"]
                }
            }
        }
    },
    # 呼吸复诊男性
    {
        "patientIdentity": {
            "patientId": "PID1234549",
            "idType": "01",
            "idNumber": "110101199001011235",
            "patientName": "王刚惠"
        },
        "visitInfo": {
            "department": "呼吸科",
            "visitNumber": "V0000222"
        },
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "男",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+"
            },
            "vitalSigns": {
                "systolicPressure": 118,
                "diastolicPressure": 76,
                "height": 178,
                "weight": 75
            },
            "marriageChildInfo": {
                "marriageStatus": "已婚",
                "fullTermCount": 0,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 0
            },
            "pastHistory": {
                "personalHistory": "无烟酒不良嗜好，否认冶游史。",
                "bloodTransfusionHistory": "无",
                "diseaseHistory": "患者平素体健，有过敏性鼻炎，无重大慢性疾病无传染病史",
                "epidemiologicalHistory": "无传染病史，流行病学史",
                "surgeryHistory": "无手术史",
                "familyHistory": "无家族性遗传病、精神病、肿瘤等类似病史.",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                }
            },
            "allergyHistory": "未发现",
            "childGrowthInfo": None
        },
        "revisitInfo": {
            "isRevisit": 1,
            "lastRecord": {
                "chiefComplaint": "反复咳嗽、咳痰10年，活动后气促5年，加重1周。",
                "presentIllness": (
                    "患者近10年来每于冬春季节出现咳嗽、咳白色黏痰，晨起明显。近5年逐渐出现登楼或快走时气促，休息后可缓解。1周前受凉后咳嗽加剧，"
                    "痰量增多呈黄脓性，气促加重，日常活动受限，无发热、咯血、夜间阵发性呼吸困难。自服“头孢类抗生素”及止咳药效果不佳，今来诊。"
                ),
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                },
                "tcmFourExams": {
                    "inspection": "红黄隐隐，明润含蓄",
                    "inquiry": "时有腹胀便溏，倦怠乏力",
                    "listeningAndSmelling": "口气",
                    "palpation": "脉弦"
                },
                "physicalExam": "无",
                "auxiliaryExam": "血常规：WBC 9.5×10^9/L，CRP 12 mg/L",
                "diagnosis": {
                    "tcmDiagnosisName": "湿疮",
                    "tcmDiagnosisCode": "A08.01.07",
                    "tcmSyndromeName": "脾虚湿困证",
                    "westernDiagnosisName": "特应性皮炎",
                    "westernDiagnosisCode": "L20.900"
                },
                "treatmentPrinciple": "健脾化湿",
                "treatmentAdvice": "少食多餐，避免辛辣油腻",
                "prescription": {
                    "prescriptionName": "复方参蝉汤",
                    "herbs": ["党参", "蝉蜕", "生白术", "茯苓", "温山药", "炒白扁豆", "薏苡仁", "生黄芪", "炒麦芽", "炒稻芽", "炒鸡内金", "大枣", "生甘草", "蚕砂"]
                }
            }
        }
    },
    # 呼吸初诊男性
    {
        "patientIdentity": {
            "patientId": "PID1234543",
            "idType": "01",
            "idNumber": "110101199001011235",
            "patientName": "李铁惠"
        },
        "visitInfo": {
            "department": "呼吸科",
            "visitNumber": "V0000222"
        },
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "男",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+"
            },
            "vitalSigns": {
                "systolicPressure": 118,
                "diastolicPressure": 76,
                "height": 178,
                "weight": 75
            },
            "marriageChildInfo": {
                "marriageStatus": "已婚",
                "fullTermCount": 0,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 0
            },
            "pastHistory": {
                "personalHistory": "",
                "bloodTransfusionHistory": "2015年输过2U红细胞",
                "diseaseHistory": "",
                "epidemiologicalHistory": "否认出国及接触史",
                "surgeryHistory": "无手术史",
                "familyHistory": "否认家族性遗传病、精神病、肿瘤等类似病史",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                }
            },
            "allergyHistory": "无",
            "childGrowthInfo": None
        },
        "revisitInfo": {
            "isRevisit": 0,
            "lastRecord": {
                "chiefComplaint": "",
                "presentIllness": "",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                },
                "tcmFourExams": {
                    "inspection": "",
                    "inquiry": "",
                    "listeningAndSmelling": "",
                    "palpation": ""
                },
                "physicalExam": "",
                "auxiliaryExam": "",
                "diagnosis": {
                    "tcmDiagnosisName": "",
                    "tcmDiagnosisCode": "",
                    "tcmSyndromeName": "",
                    "westernDiagnosisName": "",
                    "westernDiagnosisCode": ""
                },
                "treatmentPrinciple": "",
                "treatmentAdvice": "",
                "prescription": {
                    "prescriptionName": "",
                    "herbs": []
                }
            }
        }
    },
    # 呼吸初诊女性
    {
        "patientIdentity": {
            "patientId": "PID1234542",
            "idType": "01",
            "idNumber": "110101199001011235",
            "patientName": "李雨惠"
        },
        "visitInfo": {
            "department": "呼吸科",
            "visitNumber": "V0000222"
        },
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "女",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+"
            },
            "vitalSigns": {
                "systolicPressure": 118,
                "diastolicPressure": 76,
                "height": 178,
                "weight": 75
            },
            "marriageChildInfo": {
                "marriageStatus": "已婚",
                "fullTermCount": 0,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 0
            },
            "pastHistory": {
                "personalHistory": "",
                "bloodTransfusionHistory": "无记录",
                "diseaseHistory": "",
                "epidemiologicalHistory": "否认出国及接触史",
                "surgeryHistory": "无手术史",
                "familyHistory": "否认家族性遗传病、精神病、肿瘤等类似病史。",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                }
            },
            "allergyHistory": "无",
            "childGrowthInfo": None
        },
        "revisitInfo": {
            "isRevisit": 0,
            "lastRecord": {
                "chiefComplaint": "",
                "presentIllness": "",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                },
                "tcmFourExams": {
                    "inspection": "",
                    "inquiry": "",
                    "listeningAndSmelling": "",
                    "palpation": ""
                },
                "physicalExam": "",
                "auxiliaryExam": "",
                "diagnosis": {
                    "tcmDiagnosisName": "",
                    "tcmDiagnosisCode": "",
                    "tcmSyndromeName": "",
                    "westernDiagnosisName": "",
                    "westernDiagnosisCode": ""
                },
                "treatmentPrinciple": "",
                "treatmentAdvice": "",
                "prescription": {
                    "prescriptionName": "",
                    "herbs": []
                }
            }
        }
    },
    # 肛肠复诊女
    {
        "patientIdentity": {
            "patientId": "PID1234569",
            "idType": "01",
            "idNumber": "110101199001011234",
            "patientName": "王雨西"
        },
        "visitInfo": {
            "department": "肛肠科",
            "visitNumber": "V0000123"
        },
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "女",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+"
            },
            "vitalSigns": {
                "systolicPressure": 120,
                "diastolicPressure": 80,
                "height": 165,
                "weight": 60
            },
            "marriageChildInfo": {
                "marriageStatus": "已婚",
                "fullTermCount": 1,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 1
            },
            "pastHistory": {
                "personalHistory": "无烟酒不良嗜好，否认冶游史。",
                "bloodTransfusionHistory": "无",
                "diseaseHistory": "患者平素体健，无重大慢性疾病无传染病史",
                "epidemiologicalHistory": "无传染病史，流行病学史",
                "menstrualHistory": {
                    "menarcheAge": 13,
                    "intervalDays": 28,
                    "durationDays": 5,
                    "isSterilization": False,
                    "lastMenstrualDate": "2025-10-25"
                },
                "surgeryHistory": "无",
                "familyHistory": "无家族性遗传病、精神病、肿瘤等类似病史。"
            },
            "allergyHistory": "未发现",
            "childGrowthInfo": None
        },
        "revisitInfo": {
            "isRevisit": 1,
            "lastRecord": {
                "chiefComplaint": "反复肛门肿物脱出伴便血3年，加重1周。",
                "presentIllness": (
                    "患者近3年来反复出现排便时肛门肿物脱出，初始可自行回纳，偶伴便后滴血，色鲜红，量少，无黏液脓血便，无腹痛、腹泻或便秘。"
                    "食欲减退，睡眠安"
                ),
                "menstrualHistory": {
                    "menarcheAge": 13,
                    "intervalDays": 28,
                    "durationDays": 5,
                    "isSterilization": False,
                    "lastMenstrualDate": "2024-09-25"
                },
                "tcmFourExams": {
                    "inspection": "红黄隐隐，明润含蓄",
                    "inquiry": "时有腹胀便溏，倦怠乏力",
                    "listeningAndSmelling": "口气",
                    "palpation": "脉弦"
                },
                "physicalExam": "无",
                "auxiliaryExam": "血常规：WBC 9.5×10^9/L，CRP 12 mg/L",
                "diagnosis": {
                    "tcmDiagnosisName": "湿疮",
                    "tcmDiagnosisCode": "A08.01.07",
                    "tcmSyndromeName": "脾虚湿困证",
                    "westernDiagnosisName": "特应性皮炎",
                    "westernDiagnosisCode": "L20.900"
                },
                "treatmentPrinciple": "健脾化湿",
                "treatmentAdvice": "少食多餐，避免辛辣油腻",
                "prescription": {
                    "prescriptionName": "复方参蝉汤",
                    "herbs": ["党参", "蝉蜕", "生白术", "茯苓", "温山药", "炒白扁豆", "薏苡仁", "生黄芪", "炒麦芽", "炒稻芽", "炒鸡内金", "大枣", "生甘草", "蚕砂"]
                }
            }
        }
    },
    # 肛肠复诊男性
    {
        "patientIdentity": {
            "patientId": "PID1234578",
            "idType": "01",
            "idNumber": "110101199001011235",
            "patientName": "王刚西"
        },
        "visitInfo": {
            "department": "肛肠科",
            "visitNumber": "V0000222"
        },
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "男",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+"
            },
            "vitalSigns": {
                "systolicPressure": 118,
                "diastolicPressure": 76,
                "height": 178,
                "weight": 75
            },
            "marriageChildInfo": {
                "marriageStatus": "已婚",
                "fullTermCount": 0,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 0
            },
            "pastHistory": {
                "personalHistory": "无烟酒不良嗜好，否认冶游史。",
                "bloodTransfusionHistory": "无",
                "diseaseHistory": "患者平素体健，有过敏性鼻炎，无重大慢性疾病无传染病史",
                "epidemiologicalHistory": "无传染病史，流行病学史",
                "surgeryHistory": "无手术史",
                "familyHistory": "无家族性遗传病、精神病、肿瘤等类似病史.",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                }
            },
            "allergyHistory": "未发现",
            "childGrowthInfo": None
        },
        "revisitInfo": {
            "isRevisit": 1,
            "lastRecord": {
                "chiefComplaint": "反复肛门肿物脱出伴便血3年，加重1周。",
                "presentIllness": (
                    "患者近3年来反复出现排便时肛门肿物脱出，初始可自行回纳，偶伴便后滴血，色鲜红，量少，无黏液脓血便，无腹痛、腹泻或便秘。"
                    "食欲减退，睡眠安"
                ),
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                },
                "tcmFourExams": {
                    "inspection": "红黄隐隐，明润含蓄",
                    "inquiry": "时有腹胀便溏，倦怠乏力",
                    "listeningAndSmelling": "口气",
                    "palpation": "脉弦"
                },
                "physicalExam": "无",
                "auxiliaryExam": "血常规：WBC 9.5×10^9/L，CRP 12 mg/L",
                "diagnosis": {
                    "tcmDiagnosisName": "湿疮",
                    "tcmDiagnosisCode": "A08.01.07",
                    "tcmSyndromeName": "脾虚湿困证",
                    "westernDiagnosisName": "特应性皮炎",
                    "westernDiagnosisCode": "L20.900"
                },
                "treatmentPrinciple": "健脾化湿",
                "treatmentAdvice": "少食多餐，避免辛辣油腻",
                "prescription": {
                    "prescriptionName": "复方参蝉汤",
                    "herbs": ["党参", "蝉蜕", "生白术", "茯苓", "温山药", "炒白扁豆", "薏苡仁", "生黄芪", "炒麦芽", "炒稻芽", "炒鸡内金", "大枣", "生甘草", "蚕砂"]
                }
            }
        }
    },
    # 肛肠初诊男性
    {
        "patientIdentity": {
            "patientId": "PID1234588",
            "idType": "01",
            "idNumber": "110101199001011235",
            "patientName": "李铁西"
        },
        "visitInfo": {
            "department": "肛肠科",
            "visitNumber": "V0000222"
        },
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "男",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+"
            },
            "vitalSigns": {
                "systolicPressure": 118,
                "diastolicPressure": 76,
                "height": 178,
                "weight": 75
            },
            "marriageChildInfo": {
                "marriageStatus": "已婚",
                "fullTermCount": 0,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 0
            },
            "pastHistory": {
                "personalHistory": "",
                "bloodTransfusionHistory": "2015年输过2U红细胞",
                "diseaseHistory": "",
                "epidemiologicalHistory": "否认出国及接触史",
                "surgeryHistory": "无手术史",
                "familyHistory": "否认家族性遗传病、精神病、肿瘤等类似病史",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                }
            },
            "allergyHistory": "无",
            "childGrowthInfo": None
        },
        "revisitInfo": {
            "isRevisit": 0,
            "lastRecord": {
                "chiefComplaint": "",
                "presentIllness": "",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                },
                "tcmFourExams": {
                    "inspection": "",
                    "inquiry": "",
                    "listeningAndSmelling": "",
                    "palpation": ""
                },
                "physicalExam": "",
                "auxiliaryExam": "",
                "diagnosis": {
                    "tcmDiagnosisName": "",
                    "tcmDiagnosisCode": "",
                    "tcmSyndromeName": "",
                    "westernDiagnosisName": "",
                    "westernDiagnosisCode": ""
                },
                "treatmentPrinciple": "",
                "treatmentAdvice": "",
                "prescription": {
                    "prescriptionName": "",
                    "herbs": []
                }
            }
        }
    },
    # 肛肠初诊女性
    {
        "patientIdentity": {
            "patientId": "PID1234589",
            "idType": "01",
            "idNumber": "110101199001011235",
            "patientName": "李雨西"
        },
        "visitInfo": {
            "department": "肛肠科",
            "visitNumber": "V0000222"
        },
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "女",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+"
            },
            "vitalSigns": {
                "systolicPressure": 118,
                "diastolicPressure": 76,
                "height": 178,
                "weight": 75
            },
            "marriageChildInfo": {
                "marriageStatus": "已婚",
                "fullTermCount": 0,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 0
            },
            "pastHistory": {
                "personalHistory": "",
                "bloodTransfusionHistory": "无记录",
                "diseaseHistory": "",
                "epidemiologicalHistory": "否认出国及接触史",
                "surgeryHistory": "无手术史",
                "familyHistory": "否认家族性遗传病、精神病、肿瘤等类似病史。",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                }
            },
            "allergyHistory": "无",
            "childGrowthInfo": None
        },
        "revisitInfo": {
            "isRevisit": 0,
            "lastRecord": {
                "chiefComplaint": "",
                "presentIllness": "",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                },
                "tcmFourExams": {
                    "inspection": "",
                    "inquiry": "",
                    "listeningAndSmelling": "",
                    "palpation": ""
                },
                "physicalExam": "",
                "auxiliaryExam": "",
                "diagnosis": {
                    "tcmDiagnosisName": "",
                    "tcmDiagnosisCode": "",
                    "tcmSyndromeName": "",
                    "westernDiagnosisName": "",
                    "westernDiagnosisCode": ""
                },
                "treatmentPrinciple": "",
                "treatmentAdvice": "",
                "prescription": {
                    "prescriptionName": "",
                    "herbs": []
                }
            }
        }
    },
    # 皮肤科复诊男性
    {
        "patientIdentity": {
            "patientId": "PID1234563",
            "idType": "01",
            "idNumber": "110101199001011235",
            "patientName": "王刚"
        },
        "visitInfo": {
            "department": "皮肤医美中心",
            "visitNumber": "V0000222"
        },
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "男",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+"
            },
            "vitalSigns": {
                "systolicPressure": 118,
                "diastolicPressure": 76,
                "height": 178,
                "weight": 75
            },
            "marriageChildInfo": {
                "marriageStatus": "已婚",
                "fullTermCount": 0,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 0
            },
            "pastHistory": {
                "personalHistory": "无烟酒不良嗜好，否认冶游史。",
                "bloodTransfusionHistory": "无",
                "diseaseHistory": "患者平素体健，有过敏性鼻炎，无重大慢性疾病无传染病史",
                "epidemiologicalHistory": "无传染病史，流行病学史",
                "surgeryHistory": "无手术史",
                "familyHistory": "否认家族性遗传病、精神病、肿瘤等类似病史.",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                }
            },
            "allergyHistory": "未发现",
            "childGrowthInfo": None
        },
        "revisitInfo": {
            "isRevisit": 1,
            "lastRecord": {
                "chiefComplaint": "下肢红斑、丘疹、抓痕伴瘙痒8日",
                "presentIllness": (
                    "8日前无明显诱因下下肢红斑、丘疹、抓痕，伴瘙痒，外院多次就诊（卤米松乳膏 外用应急软膏 氯雷他定片 ），皮疹仍反复发作"
                    "口不渴，睡眠安，"
                    "大便便次正常，小便尿次正常"
                ),
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                },
                "tcmFourExams": {
                    "inspection": "红黄隐隐，明润含蓄",
                    "inquiry": "时有腹胀便溏，倦怠乏力",
                    "listeningAndSmelling": "口气",
                    "palpation": "脉弦"
                },
                "physicalExam": "无",
                "auxiliaryExam": "血常规：WBC 9.5×10^9/L，CRP 12 mg/L",
                "diagnosis": {
                    "tcmDiagnosisName": "湿疮",
                    "tcmDiagnosisCode": "A08.01.07",
                    "tcmSyndromeName": "脾虚湿困证",
                    "westernDiagnosisName": "特应性皮炎",
                    "westernDiagnosisCode": "L20.900"
                },
                "treatmentPrinciple": "健脾化湿",
                "treatmentAdvice": "少食多餐，避免辛辣油腻",
                "prescription": {
                    "prescriptionName": "复方参蝉汤",
                    "herbs": ["党参", "蝉蜕", "生白术", "茯苓", "温山药", "炒白扁豆", "薏苡仁", "生黄芪", "炒麦芽", "炒稻芽", "炒鸡内金", "大枣", "生甘草", "蚕砂"]
                }
            }
        }
    },
    # 皮肤科复诊女性
    {
        "patientIdentity": {
            "patientId": "PID1234562",
            "idType": "01",
            "idNumber": "110101199001011234",
            "patientName": "王雨"
        },
        "visitInfo": {
            "department": "皮肤医美中心",
            "visitNumber": "V0000123"
        },
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "女",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+"
            },
            "vitalSigns": {
                "systolicPressure": 120,
                "diastolicPressure": 80,
                "height": 165,
                "weight": 60
            },
            "marriageChildInfo": {
                "marriageStatus": "已婚",
                "fullTermCount": 1,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 1
            },
            "pastHistory": {
                "personalHistory": "无烟酒不良嗜好，否认冶游史。",
                "bloodTransfusionHistory": "无",
                "diseaseHistory": "患者平素体健，无重大慢性疾病无传染病史",
                "epidemiologicalHistory": "无传染病史，流行病学史",
                "menstrualHistory": {
                    "menarcheAge": 13,
                    "intervalDays": 28,
                    "durationDays": 5,
                    "isSterilization": False,
                    "lastMenstrualDate": "2025-10-25"
                },
                "surgeryHistory": "无",
                "familyHistory": "否认家族性遗传病、精神病、肿瘤等类似病史。"
            },
            "allergyHistory": "未发现",
            "childGrowthInfo": None
        },
        "revisitInfo": {
            "isRevisit": 1,
            "lastRecord": {
                "chiefComplaint": "颈项部红斑、抓痕伴瘙痒2月",
                "presentIllness": (
                    "2月前无明显诱因下颈项部红斑、抓痕，伴瘙痒，未予特殊处理"
                    "食欲减退，睡眠安，"
                    "大便溏结不调，小便尿次正常"
                ),
                "menstrualHistory": {
                    "menarcheAge": 13,
                    "intervalDays": 28,
                    "durationDays": 5,
                    "isSterilization": False,
                    "lastMenstrualDate": "2024-09-25"
                },
                "tcmFourExams": {
                    "inspection": "红黄隐隐，明润含蓄",
                    "inquiry": "时有腹胀便溏，倦怠乏力",
                    "listeningAndSmelling": "口气",
                    "palpation": "脉弦"
                },
                "physicalExam": "无",
                "auxiliaryExam": "血常规：WBC 9.5×10^9/L，CRP 12 mg/L",
                "diagnosis": {
                    "tcmDiagnosisName": "湿疮",
                    "tcmDiagnosisCode": "A08.01.07",
                    "tcmSyndromeName": "脾虚湿困证",
                    "westernDiagnosisName": "特应性皮炎",
                    "westernDiagnosisCode": "L20.900"
                },
                "treatmentPrinciple": "健脾化湿",
                "treatmentAdvice": "少食多餐，避免辛辣油腻",
                "prescription": {
                    "prescriptionName": "复方参蝉汤",
                    "herbs": ["党参", "蝉蜕", "生白术", "茯苓", "温山药", "炒白扁豆", "薏苡仁", "生黄芪", "炒麦芽", "炒稻芽", "炒鸡内金", "大枣", "生甘草", "蚕砂"]
                }
            }
        }
    },
    # 皮肤科初诊男性
    {
        "patientIdentity": {
            "patientId": "PID1234565",
            "idType": "01",
            "idNumber": "110101199001011235",
            "patientName": "李铁"
        },
        "visitInfo": {
            "department": "皮肤医美中心",
            "visitNumber": "V0000222"
        },
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "男",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+"
            },
            "vitalSigns": {
                "systolicPressure": 118,
                "diastolicPressure": 76,
                "height": 178,
                "weight": 75
            },
            "marriageChildInfo": {
                "marriageStatus": "已婚",
                "fullTermCount": 0,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 0
            },
            "pastHistory": {
                "personalHistory": "",
                "bloodTransfusionHistory": "2015年输过2U红细胞",
                "diseaseHistory": "",
                "epidemiologicalHistory": "否认出国及接触史",
                "surgeryHistory": "无手术史",
                "familyHistory": "否认家族性遗传病、精神病、肿瘤等类似病史",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                }
            },
            "allergyHistory": "无",
            "childGrowthInfo": None
        },
        "revisitInfo": {
            "isRevisit": 0,
            "lastRecord": {
                "chiefComplaint": "",
                "presentIllness": "",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                },
                "tcmFourExams": {
                    "inspection": "",
                    "inquiry": "",
                    "listeningAndSmelling": "",
                    "palpation": ""
                },
                "physicalExam": "",
                "auxiliaryExam": "",
                "diagnosis": {
                    "tcmDiagnosisName": "",
                    "tcmDiagnosisCode": "",
                    "tcmSyndromeName": "",
                    "westernDiagnosisName": "",
                    "westernDiagnosisCode": ""
                },
                "treatmentPrinciple": "",
                "treatmentAdvice": "",
                "prescription": {
                    "prescriptionName": "",
                    "herbs": []
                }
            }
        }
    },
    # 皮肤科初诊女性
    {
        "patientIdentity": {
            "patientId": "PID1234566",
            "idType": "01",
            "idNumber": "110101199001011235",
            "patientName": "李雨"
        },
        "visitInfo": {
            "department": "皮肤医美中心",
            "visitNumber": "V0000222"
        },
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "女",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+"
            },
            "vitalSigns": {
                "systolicPressure": 118,
                "diastolicPressure": 76,
                "height": 178,
                "weight": 75
            },
            "marriageChildInfo": {
                "marriageStatus": "",
                "fullTermCount": 0,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 0
            },
            "pastHistory": {
                "personalHistory": "",
                "bloodTransfusionHistory": "无记录",
                "diseaseHistory": "",
                "epidemiologicalHistory": "否认出国及接触史",
                "surgeryHistory": "无手术史",
                "familyHistory": "否认家族性遗传病、精神病、肿瘤等类似病史。",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                }
            },
            "allergyHistory": "无",
            "childGrowthInfo": None
        },
        "revisitInfo": {
            "isRevisit": 0,
            "lastRecord": {
                "chiefComplaint": "",
                "presentIllness": "",
                "menstrualHistory": {
                    "menarcheAge": 0,
                    "intervalDays": 0,
                    "durationDays": 0,
                    "isSterilization": False,
                    "lastMenstrualDate": ""
                },
                "tcmFourExams": {
                    "inspection": "",
                    "inquiry": "",
                    "listeningAndSmelling": "",
                    "palpation": ""
                },
                "physicalExam": "",
                "auxiliaryExam": "",
                "diagnosis": {
                    "tcmDiagnosisName": "",
                    "tcmDiagnosisCode": "",
                    "tcmSyndromeName": "",
                    "westernDiagnosisName": "",
                    "westernDiagnosisCode": ""
                },
                "treatmentPrinciple": "",
                "treatmentAdvice": "",
                "prescription": {
                    "prescriptionName": "",
                    "herbs": []
                }
            }
        }
    },
]


def _find_patient(opc_id: str):
    return next(
        (p for p in MOCK_PATIENT_DATA if p["patientIdentity"]["patientId"] == opc_id),
        None
    )

def _calc_age(birthday_str: str) -> int:
    birth = datetime.strptime(birthday_str, "%Y-%m-%d").date()
    today = date.today()
    return today.year - birth.year - (
        (today.month, today.day) < (birth.month, birth.day)
    )

class PatientService:

    @staticmethod
    def get_patient_base(opc_id: str):

        patient = _find_patient(opc_id)
        if not patient:
            return None

        basic = patient["latestMedicalRecord"]["basicInfo"]
        visit = patient.get("visitInfo", {})

        return {
            "name": patient["patientIdentity"].get("patientName"),
            "department": visit.get("department"),
            "visit_number": visit.get("visitNumber"),
            "age": _calc_age(basic["birthday"])
        }

    @staticmethod
    def get_patient_detail(opc_id: str):

        return _find_patient(opc_id)

    @staticmethod
    def get_all_patients():
        return MOCK_PATIENT_DATA