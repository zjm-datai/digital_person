import json
from core.graph_apps.pifuke.app import App


def build_context_json_str() -> str:
    payload = {
        "patientIdentity": {
            "patientId": "PID1234565",
            "idType": "01",
            "idNumber": "110101199001011235",
            "patientName": "李铁",
        },
        "visitInfo": {"department": "皮肤医美中心", "visitNumber": "V0000222"},
        "latestMedicalRecord": {
            "basicInfo": {
                "gender": "男",
                "birthday": "1985-05-20",
                "aboBloodType": "A",
                "rhBloodType": "+",
            },
            "vitalSigns": {
                "systolicPressure": 118,
                "diastolicPressure": 76,
                "height": 178,
                "weight": 75,
            },
            "marriageChildInfo": {
                "marriageStatus": "已婚",
                "fullTermCount": 0,
                "prematureCount": 0,
                "abortionCount": 0,
                "livingChildrenCount": 0,
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
                    "lastMenstrualDate": "",
                },
            },
            "allergyHistory": "无",
            "childGrowthInfo": None,
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
                    "lastMenstrualDate": "",
                },
                "tcmFourExams": {
                    "inspection": "",
                    "inquiry": "",
                    "listeningAndSmelling": "",
                    "palpation": "",
                },
                "physicalExam": "",
                "auxiliaryExam": "",
                "diagnosis": {
                    "tcmDiagnosisName": "",
                    "tcmDiagnosisCode": "",
                    "tcmSyndromeName": "",
                    "westernDiagnosisName": "",
                    "westernDiagnosisCode": "",
                },
                "treatmentPrinciple": "",
                "treatmentAdvice": "",
                "prescription": {"prescriptionName": "", "herbs": []},
            },
        },
    }
    return json.dumps(payload, ensure_ascii=False)


if __name__ == "__main__":
    app = App()
    conversation_id = "test_pid12345678_stream"

    config = {
        "configurable": {"thread_id": conversation_id}
    }

    # =========================
    # 第一轮：输入病历上下文
    # =========================
    bingli = build_context_json_str()
    first_input = {
        "messages": bingli,
        "session_id": conversation_id,
    }

    print("=== First round: input patient record ===")

    last_state = None

    for mode, chunk in app.graph.stream(
        first_input,
        config,
        stream_mode=["messages", "values"],
    ):
        if mode == "messages":
            print("AI:", chunk)
        elif mode == "values":
            last_state = chunk

    print("\n=== FINAL STATE (after patient record) ===")
    print(last_state)

    # =========================
    # 多轮对话
    # =========================
    while True:
        user_answer = input("\nYou (type 'quit' to exit): ")
        if user_answer.lower() in ("quit", "exit"):
            break

        other_input = {
            "messages": user_answer,
            "session_id": conversation_id,
        }

        print("\n=== New round ===")

        last_state = None

        for mode, chunk in app.graph.stream(
            other_input,
            config,
            stream_mode=["messages", "values"],
        ):
            if mode == "messages":
                print("AI:", chunk)
            elif mode == "values":
                last_state = chunk

        print("\n=== FINAL STATE (this round) ===")
        print(last_state)

    # =========================
    # 资源释放
    # =========================
    from extensions.ext_apps_database import connection_pool

    if connection_pool:
        connection_pool.close()
